import json

from handle_query import QueryHandler
query_handler = QueryHandler()

# user query to mongo query conversion tests
def test_valid_user_query():
    valid_user_query =  'What is the total population of North America in 2023?'
    valid_mongo_query_expected = {'region': 'North America', 'year': 2023}
    valid_mongo_query_actual = query_handler.user_query_to_mongo_query(valid_user_query)['query']
    assert valid_mongo_query_expected == valid_mongo_query_actual, "Mongo query generated is different"

# def test_valid_user_query_with_condition():
#     invalid_user_query = 'What was the total population of Atlantis in 2023?'
#     invalid_mongo_query_expected = {'region': 'Atlantis', 'year': 2023}
#     invalid_mongo_query_actual = query_handler.user_query_to_mongo_query(invalid_user_query)['query']
#     assert invalid_mongo_query_expected == invalid_mongo_query_actual, "Mongo query generated is different"

def test_unsupported_user_query():
    unsupported_user_query = 'What was the birth rate of Atlantis in 2023?'
    unsupported_user_query_response_expected = 'Unsupported Query - requested information not retrievable'
    unsupported_user_query_response_actual = query_handler.user_query_to_mongo_query(unsupported_user_query)['query']
    assert unsupported_user_query_response_expected == unsupported_user_query_response_actual, "Mongo query generated is different"

# mongo query to query result tests
invalid_mongo_query
invalid_mongo_query_result_expected
invalid_mongo_query_result_actual



