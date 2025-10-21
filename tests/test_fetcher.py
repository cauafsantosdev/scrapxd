"""
Unit tests for the Fetcher class in the scrapxd.fetcher module.

This test suite uses pytest and pytest-mock to isolate the Fetcher's logic
from the actual network, allowing for reliable and fast testing of its core
functionalities, including request success, error handling, and retry logic.
"""

import pytest
import requests
from bs4 import BeautifulSoup
from scrapxd.fetcher import Fetcher

# A simple HTML content to be used in mock responses
MOCK_HTML_CONTENT = b"<html><head><title>Test Page</title></head><body><h1>Hello</h1></body></html>"

@pytest.fixture
def mock_requests(mocker):
    """
    A pytest fixture that mocks the requests.Session object and its `get` method.
    This prevents actual HTTP requests from being made during tests.
    """
    mock_session_instance = mocker.Mock()
    mock_session_instance.headers = {}
    
    mock_session_class = mocker.patch('requests.Session', autospec=True)
    mock_session_class.return_value = mock_session_instance

    return mock_session_instance.get

def test_fetcher_initialization():
    """
    Tests that the Fetcher is initialized correctly, with a session and a random User-Agent.
    """
    fetcher = Fetcher(delay=0)
    # Assert that a session object was created
    assert fetcher.session is not None
    # Assert that the User-Agent header was set on the session
    assert 'User-Agent' in fetcher.session.headers
    assert fetcher.session.headers['User-Agent'] is not None

def test_fetch_page_success(mocker, mock_requests):
    """
    Tests the _fetch_page method for a successful (200 OK) response.
    Verifies that the correct URL is called and the response content is returned as bytes.
    """
    # Configure the mock response for a successful request
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = MOCK_HTML_CONTENT
    mock_response.raise_for_status.return_value = None
    mock_requests.return_value = mock_response

    fetcher = Fetcher(delay=0)
    # Mock sleep to make the test run instantly
    mocker.patch('time.sleep')
    
    # Call the method being tested
    content = fetcher._fetch_page("http://test.com", delay=0)

    # Assertions
    mock_requests.assert_called_once_with("http://test.com")
    assert content == MOCK_HTML_CONTENT

def test_fetch_soup_success(mocker):
    """
    Tests the fetch_soup method to ensure it returns a valid BeautifulSoup object
    after a successful fetch.
    """
    # Mock _fetch_page directly to isolate the soup creation logic
    mocker.patch.object(Fetcher, '_fetch_page', return_value=MOCK_HTML_CONTENT)
    
    fetcher = Fetcher(delay=0)
    soup = fetcher.fetch_soup("http://test.com")

    # Assertions
    assert isinstance(soup, BeautifulSoup)
    assert soup.title.string == "Test Page"

def test_fetch_page_client_error_no_retry(mocker, mock_requests):
    """
    Tests that a client-side error (like 404 Not Found) raises an HTTPError
    and does not trigger the retry mechanism.
    """
    # Configure the mock response for a 404 error
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.return_value = mock_response

    fetcher = Fetcher(delay=0)
    mocker.patch('time.sleep')

    # The test should raise an HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        fetcher._fetch_page("http://test.com/notfound", delay=0)

    # Assert that the request was made only once (no retries)
    assert mock_requests.call_count == 1

def test_fetch_page_server_error_with_retry(mocker, mock_requests):
    """
    Tests the retry logic for a server-side error (503 Service Unavailable).
    It simulates a scenario where the first two calls fail and the third one succeeds.
    """
    # Create a list of responses to be returned on each call
    mock_failure_response = mocker.Mock()
    mock_failure_response.status_code = 503
    mock_failure_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Service Unavailable", response=mock_failure_response
    )

    mock_success_response = mocker.Mock()
    mock_success_response.status_code = 200
    mock_success_response.content = MOCK_HTML_CONTENT
    mock_success_response.raise_for_status.return_value = None

    # The `side_effect` can be a list to simulate different results on consecutive calls
    mock_requests.side_effect = [mock_failure_response, mock_failure_response, mock_success_response]

    fetcher = Fetcher(delay=0)
    mock_sleep = mocker.patch('time.sleep')

    # Call the method. Despite the initial failures, it should eventually succeed.
    content = fetcher._fetch_page("http://test.com/service", delay=0)

    # Assertions
    assert content == MOCK_HTML_CONTENT
    # The request should have been called 3 times (1 initial + 2 retries)
    assert mock_requests.call_count == 3
    # The delay logic for retries should have been called (tenacity calls sleep)
    assert mock_sleep.call_count > 1

def test_is_retryable_exception():
    """
    Tests the static method `is_retryable_exception` to ensure it correctly
    identifies which HTTP status codes should trigger a retry.
    """
    # Test retryable status codes
    for code in [429, 500, 502, 503, 504]:
        response = requests.Response()
        response.status_code = code
        exception = requests.exceptions.HTTPError(response=response)
        assert Fetcher.is_retryable_exception(exception) is True

    # Test non-retryable status codes
    for code in [400, 401, 403, 404]:
        response = requests.Response()
        response.status_code = code
        exception = requests.exceptions.HTTPError(response=response)
        assert Fetcher.is_retryable_exception(exception) is False

    # Test other exception types
    assert Fetcher.is_retryable_exception(ValueError()) is False