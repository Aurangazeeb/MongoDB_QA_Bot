import pytest

from bot_exceptions import DataNotFoundError, FieldMissingError, IncorrectYearError, ViolationOfDocumentStructureError
from handle_query import QueryHandler
query_handler = QueryHandler()

# user query to mongo query conversion tests
def test_valid_user_query():
    valid_user_query =  'What is the total population of North America in 2023?'
    valid_mongo_query_expected = {'region': 'North America', 'year': 2023}
    valid_mongo_query_actual = query_handler.user_query_to_mongo_query(valid_user_query)['query']
    assert valid_mongo_query_expected == valid_mongo_query_actual, "Mongo query generated is different"

def test_unsupported_user_query():
    unsupported_user_query = 'What was the birth rate of Atlantis in 2023?'
    unsupported_user_query_response_expected = 'Unsupported Query - requested information not retrievable'
    unsupported_user_query_response_actual = query_handler.user_query_to_mongo_query(unsupported_user_query)['query']
    assert unsupported_user_query_response_expected == unsupported_user_query_response_actual, "Mongo query generated is different"

# mongo query to query result tests
def test_querying_on_available_data():
    user_query = 'What is the total population of the region Europe in 2023?'
    expected_query_response = 'The total population of Europe in 2023 is 748,420,000.'
    actual_query_response = query_handler.answer_query(user_query)
    assert expected_query_response == actual_query_response, f"Expected response was {expected_query_response} but got {actual_query_response}"

def test_querying_on_unavailable_data():
    user_query = 'What is the total population of region East Japan in 2023?'
    with pytest.raises(DataNotFoundError):
        query_handler.answer_query(user_query)

def test_querying_with_missing_field():
    user_query = 'What is the birth rate of Africa in 2023?'
    with pytest.raises(FieldMissingError):
        query_handler.answer_query(user_query)

def test_querying_with_incorrect_year():
    user_query = 'What is the total population of region Africa in 202003?'
    with pytest.raises(IncorrectYearError):
        query_handler.answer_query(user_query)

def test_querying_with_a_specific_age():
    user_query = 'What is the number of people of age 10 in North America in 2023?'
    with pytest.raises(ViolationOfDocumentStructureError):
        query_handler.answer_query(user_query)

def test_querying_with_a_different_age_range():
    user_query = 'What is the number of people between the age of 50 and 55 in Asia in 2023?'
    with pytest.raises(ViolationOfDocumentStructureError):
        query_handler.answer_query(user_query)



