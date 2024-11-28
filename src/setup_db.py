
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

# loading all secrets into environment
load_dotenv('.env')
MONGODB_CONNECTION_STRING = os.environ['MONGODB_CONNECTION_STRING']
SAMPLE_DOC_PATH = os.environ['DOC_PATH']
DB_NAME = os.environ['DB_NAME']
COLLECTION_NAME = os.environ['COLLECTION_NAME']


def setup_database():
    client = MongoClient(MONGODB_CONNECTION_STRING)
    client.drop_database(DB_NAME)
    db = client[DB_NAME]
    stats_collection = db[COLLECTION_NAME]

    # loading up sample documents to populate the table
    with open(SAMPLE_DOC_PATH) as file:
        documents = json.load(file)

    # Insert all documents into the collection
    stats_collection.insert_many(documents)
    print(f"Documents inserted into collection : {COLLECTION_NAME}")

if __name__ == '__main__':
    setup_database()