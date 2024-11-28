import pytest
from src.bot_exceptions import DataNotFoundError, FieldMissingError, IncorrectYearError, ViolationOfDocumentStructureError
from src.handle_query import QueryHandler
import time

query_handler = QueryHandler()

# user query to mongo query conversion tests
def test_valid_user_query():
    valid_user_query =  'What is the total population of North America in 2023?'
    valid_mongo_query_expected = {'region': 'North America', 'year': 2023}
    valid_mongo_query_actual = query_handler.simple_user_query_to_mongo_query(valid_user_query)['query']
    assert valid_mongo_query_expected == valid_mongo_query_actual, "Mongo query generated is different"

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
    user_query = 'What is the total population of North America in the year 202003?'
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

def test_querying_with_minor_mistakes_in_user_query():
    user_query_with_typo = 'What is the gdp of the North AMrica in 2023?'
    expected_response = 'The GDP of North America in 2023 is $23,000,000,000.'
    actual_response = query_handler.answer_query(user_query_with_typo)
    assert expected_response == actual_response, f"Expected response was {expected_response}, but got {actual_response}"

def test_in_memory_caching_performance():
    user_query = 'What is the gdp of the North America in 2023?'
    start = time.time()
    query_handler.answer_query(user_query)
    non_cached_duration = time.time() - start
    cached_query_start = time.time()
    query_handler.answer_query(user_query)
    cached_duration = time.time() - cached_query_start
    assert cached_duration < non_cached_duration, f"Expected cached query latency < non-cached query latency, but was greater"

def test_non_aggregation_query_classification():
    user_query = 'What is the total population of North America in 2023?'
    expected_query_class = 'non-aggregation'
    actual_query_class = query_handler.classify_user_query(user_query)
    assert expected_query_class == actual_query_class

def test_aggregation_query_classification():
    user_query = 'What is the average GDP of all regions in 2023?'
    expected_query_class = 'aggregation'
    actual_query_class = query_handler.classify_user_query(user_query)
    assert expected_query_class == actual_query_class

def test_querying_valid_aggregation_user_query():
    agg_user_query = 'What is the combined gdp contribution of industry and services sector to Europe in 2023?'
    expected_query_response = 'The combined GDP contribution of the industry and services sectors to Europe in 2023 is $24,250,000,000.'
    actual_query_response = query_handler.answer_query(agg_user_query)
    assert expected_query_response == actual_query_response, f"Expected response is {expected_query_response} but got {actual_query_response}"

def test_valid_aggregation_user_query():
    agg_user_query = "What is the combined gdp contribution % of services and industry sector of region Africa in 2023?"
    expected_agg_mongo_query = str([{'$match': {'region': 'Africa', 'year': 2023}},
  {'$project': {'combined_gdp_contribution': {'$add': ['$data.economy.sectors.industry',
      '$data.economy.sectors.services']}}}])
    actual_agg_mongo_query = query_handler.agg_user_query_to_mongo_query(agg_user_query)['query']
    assert expected_agg_mongo_query == str(actual_agg_mongo_query), f"Expected response is {expected_agg_mongo_query} but got {actual_agg_mongo_query}"

def test_querying_aggregation_user_query_with_missing_field():
    agg_user_query = 'What is the average unemployment rate in 2023 for the regions - Africa, North America and Asia?'
    with pytest.raises(FieldMissingError):
        query_handler.answer_query(agg_user_query)

def test_quering_aggregation_user_query_with_unavailable_data():
    agg_user_query = "What is the average % gdp contribution of services and industry sector of region Atlantis in 2023?"
    with pytest.raises(DataNotFoundError):
        query_handler.answer_query(agg_user_query)