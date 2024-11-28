from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

from notebooks.handle_query import DB_NAME

load_dotenv('./.env')
MONGODB_CONNECTION_STRING = os.environ['MONGODB_CONNECTION_STRING']
SAMPLE_DOC_PATH = os.environ['SAMPLE_DOC_PATH']
COLLECTION_NAME = os.environ['COLLECTION_NAME']


def setup_database():
    client = MongoClient(MONGODB_CONNECTION_STRING)
    client.drop_database(DB_NAME)
    db = client[DB_NAME]
    stats_collection = db[COLLECTION_NAME]

    with open(SAMPLE_DOC_PATH) as file:
        documents = json.load(file)

    # Insert multiple documents (add more as needed)
    stats_collection.insert_many(documents)
    print(f"Documents inserted into collection : {COLLECTION_NAME} ...")