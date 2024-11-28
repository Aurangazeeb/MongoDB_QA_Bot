import argparse
from handle_query import QueryHandler
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from pathlib import Path


if __name__ == '__main__':
    load_dotenv('.env', override=True)
    ROOT_DIR = Path(os.environ['ROOT_DIR']).absolute()
    MONGODB_CONNECTION_STRING = os.environ['MONGODB_CONNECTION_STRING']
    SAMPLE_DOC_PATH = ROOT_DIR / os.environ['SAMPLE_DOC_PATH']
    DB_NAME = os.environ['DB_NAME']
    COLLECTION_NAME = os.environ['COLLECTION_NAME']

    client = MongoClient()
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-q', '--userquery', type=str, required=True)
    args = argparser.parse_args()
    query_handler = QueryHandler()
    print(query_handler.answer_query(args.userquery))