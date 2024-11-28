import json
import re
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from handle_bot_exception import BotResponseExceptionHandler as brh
from pathlib import Path
from warnings import filterwarnings
filterwarnings('ignore')

load_dotenv('./.env')
ROOT_DIR = Path(__file__).absolute().parent
MONGODB_CONNECTION_STRING = os.environ['MONGODB_CONNECTION_STRING']
SAMPLE_DOC_PATH = os.environ['SAMPLE_DOC_PATH']
DB_NAME = os.environ['DB_NAME']
COLLECTION_NAME = os.environ['COLLECTION_NAME']
OPENAI_MODEL_NAME = os.environ['OPENAI_MODEL_NAME']
USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE = ROOT_DIR / os.environ['USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE']
MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE = ROOT_DIR / os.environ['MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE']


class QueryHandler:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING)
        self.collection = self.client[DB_NAME][COLLECTION_NAME]
        self.parser_llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=0, response_format = {'type' : 'json_object'})
        self.explainer_llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=0, response_format = {'type' : 'text'})
        self.user_query_parsing_prompt = self._get_user_query_to_mongo_query_parsing_prompt()
        self.mongo_result_parsing_prompt = self._get_mongo_result_to_natural_response_prompt()
        self.user_query_parsing_llm_chain = self.user_query_parsing_prompt | self.parser_llm
        self.mongo_result_parsing_llm_chain = self.mongo_result_parsing_prompt | self.explainer_llm

    def _get_user_query_to_mongo_query_parsing_prompt(self):
        with open(USER_QUERY_2_MONGO_QUERY_PARSING_PROMPT_TEMPLATE) as file:
            prompt_template = file.read()
        return PromptTemplate(input_variables = ['user_query'], template = prompt_template)

    def _get_mongo_result_to_natural_response_prompt(self):
        with open(MONGO_RESULT_2_NL_RESPONSE_PROMPT_TEMPLATE) as file:
            prompt_template = file.read()
        return PromptTemplate(input_variables = ['user_query'], template = prompt_template)

    def user_query_to_mongo_query(self, user_query):
        response = self.user_query_parsing_llm_chain.invoke(user_query).content
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            response = re.search(r'```json\n(.*)\n```', response, flags = re.MULTILINE | re.DOTALL).group(1)
            return json.loads(response)

    def run_query(self, mongo_query):
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
        mongo_query = self.user_query_to_mongo_query(user_query)
        if self.is_mongo_query_valid(mongo_query):
            mongo_cursor = self.run_query(mongo_query)
            if mongo_cursor:
                return self.mongo_result_to_nl_response(user_query, mongo_cursor)
            else:
                print('Data not found exception')
                brh.handle_exception()
        else:
            exception_title, exception_message = self.parse_query_exception(mongo_query['query'])
            print('Exception title : ', exception_title)
            brh.handle_exception(exception_title, exception_message)




