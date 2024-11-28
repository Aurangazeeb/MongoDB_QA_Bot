import argparse
from src.handle_query import QueryHandler
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv('.env', override=True)
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-q', '--userquery', type=str,
                           required=True, help="User query in natural language to extract data from the MongoDB stats collection")
    args = argparser.parse_args()
    query_handler = QueryHandler()
    print(query_handler.answer_query(args.userquery))