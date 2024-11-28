import json
import re

from langchain.chains.summarize.map_reduce_prompt import prompt_template
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.handle_bot_exception import BotResponseExceptionHandler as brh
import hashlib
from warnings import filterwarnings
filterwarnings('ignore')

load_dotenv('.env', override=True)
MONGODB_CONNECTION_STRING = os.environ['MONGODB_CONNECTION_STRING']
SAMPLE_DOC_PATH = os.environ['DOC_PATH']
DB_NAME = os.environ['DB_NAME']
COLLECTION_NAME = os.environ['COLLECTION_NAME']
OPENAI_MODEL_NAME = os.environ['OPENAI_MODEL_NAME']
USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE = os.environ['USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE']
MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE = os.environ['MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE']
USER_QUERY_CLASSIFIER_PROMPT_TEMPLATE = os.environ['USER_QUERY_CLASSIFIER_PROMPT_TEMPLATE']
USER_QUERY_2_AGG_MONGO_QUERY_PARSING_PROMPT_TEMPLATE = os.environ['USER_QUERY_2_AGG_MONGO_QUERY_PARSING_PROMPT_TEMPLATE']


# simple in memory caching
cache = {}

class QueryHandler:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING)
        self.collection = self.client[DB_NAME][COLLECTION_NAME]
        self.parser_llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=0, response_format = {'type' : 'json_object'}, max_completion_tokens = 500)
        self.explainer_llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=0, response_format = {'type' : 'text'},  max_completion_tokens = 800)
        self.user_query_parsing_prompt = self._get_prompt(USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE)
        self.user_query_classifier_prompt = self._get_prompt(USER_QUERY_CLASSIFIER_PROMPT_TEMPLATE)
        self.mongo_result_parsing_prompt = self._get_prompt(MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE)
        self.user_query_2_agg_mongo_query_parser_prompt = self._get_prompt(USER_QUERY_2_AGG_MONGO_QUERY_PARSING_PROMPT_TEMPLATE)
        self.user_query_parsing_llm_chain = self.user_query_parsing_prompt | self.parser_llm
        self.agg_user_query_parsing_llm_chain = self.user_query_2_agg_mongo_query_parser_prompt | self.parser_llm
        self.mongo_result_parsing_llm_chain = self.mongo_result_parsing_prompt | self.explainer_llm
        self.uesr_query_classifier_llm_chain = self.user_query_classifier_prompt | self.explainer_llm

    # Helper function to generate a cache key from the user query
    def generate_cache_key(self, user_query):
        # Use a hash of the user query as the cache key (to ensure uniqueness)
        return hashlib.md5(user_query.encode('utf-8')).hexdigest()

    def _get_prompt(self, template_path):
        with open(template_path) as file:
            prompt_template = file.read()
        return PromptTemplate(input_variables = ['user_query'], template = prompt_template)

    def user_query_to_mongo_query(self, user_query):
        query_class = self.classify_user_query(user_query)
        if query_class == 'non-aggregation':
            mongo_query = self.simple_user_query_to_mongo_query(user_query)
        else:
            mongo_query = self.agg_user_query_to_mongo_query(user_query)
        return mongo_query, query_class


    def simple_user_query_to_mongo_query(self, user_query):
        response = self.user_query_parsing_llm_chain.invoke(user_query).content
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            response = re.search(r'```json\n(.*)\n```', response, flags = re.MULTILINE | re.DOTALL).group(1)
            return json.loads(response)

    def run_query(self, mongo_query, user_query_class):
        if user_query_class != 'aggregation':
            return self.run_simple_query(mongo_query)
        else:
            return self.run_agg_query(mongo_query)

    def run_simple_query(self, mongo_query):
        return list(self.collection.find(mongo_query['query'], **mongo_query['params']))
    def mongo_result_to_nl_response(self, user_query, mongo_result):
        return self.mongo_result_parsing_llm_chain.invoke({'user_query': user_query, 'mongo_result' : str(mongo_result)}).content

    def parse_query_exception(self, exception_reason):
        exception_title, exception_message = re.search(r'Unsupported Query - ([\w\s?]+): (.*)', exception_reason).groups()
        return exception_title, exception_message

    def is_mongo_query_valid(self, mongo_query):
        if 'Unsupported Query' in mongo_query['query']:
            return False
        else:
            return True

    def answer_query(self, user_query):
        user_query_cache_key = self.generate_cache_key(user_query)
        if user_query_cache_key not in cache:
            mongo_query, user_query_class = self.user_query_to_mongo_query(user_query)
            # if mongo query is valid - it can be executed
            if self.is_mongo_query_valid(mongo_query):
                # execute mongo query depending on the user query class
                mongo_cursor = self.run_query(mongo_query, user_query_class)
                if mongo_cursor:
                    nl_response =  self.mongo_result_to_nl_response(user_query, mongo_cursor)
                    cache[user_query_cache_key] = nl_response
                    return nl_response
                else:
                    brh.handle_exception()
            # if mongo query is invalid - handle the situation
            else:
                exception_title, exception_message = self.parse_query_exception(mongo_query['query'])
                print('Exception title : ', exception_title)
                brh.handle_exception(exception_title, exception_message)
        else:
            return cache[user_query_cache_key]

    def classify_user_query(self, user_query):
        return self.uesr_query_classifier_llm_chain.invoke({'user_query': user_query}).content

    def agg_user_query_to_mongo_query(self, user_query):
        response = self.agg_user_query_parsing_llm_chain.invoke({'user_query' : user_query}).content
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            response = re.search(r'```json\n(.*)\n```', response, flags = re.MULTILINE | re.DOTALL).group(1)
            response = json.loads(response)
        return response

    def run_agg_query(self, agg_mongo_query):
        return list(self.collection.aggregate(agg_mongo_query['query']))




