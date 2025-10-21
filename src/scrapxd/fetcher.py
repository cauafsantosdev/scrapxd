"""
This module provides the network layer for the Scrapxd library.

It defines the Fetcher class, which is responsible for making all HTTP requests
to the Letterboxd website. It uses requests.Session for connection pooling and
efficiency, the tenacity library for robust retries with exponential backoff,
and randomized delays to act as a good web citizen.
"""

import requests
import logging
from time import sleep
from random import uniform
from typing import Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .config import BASE_URL, FILM_URL
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

# Get a logger instance for this module
log = logging.getLogger(__name__)

class Fetcher:
    """
    A client for making robust HTTP requests to Letterboxd.

    This class encapsulates session management, headers, randomized user-agents,
    delays, and retry logic for all web scraping tasks.

    Args:
        delay (float): The default delay in seconds to wait between requests.
            The real delay will be a random float between (delay - (delay/2)) and delay
            Defaults to a random float between 1 and 3.
    """
    def __init__(self, delay: float = 0):
        """Initializes the Fetcher, setting up the requests session and user agent."""
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})
        self.delay = delay

    @staticmethod
    def is_retryable_exception(exception: Exception) -> bool:
        """
        Determines if an exception is worth retrying.

        Used by the `tenacity` retry decorator to retry only on specific
        server-side errors or rate-limiting HTTP status codes.
        """
        if not isinstance(exception, requests.exceptions.HTTPError):
            return False

        # Safely access response.status_code
        response = getattr(exception, "response", None)
        if response is None or not hasattr(response, "status_code"):
            return False

        return response.status_code in [429, 500, 502, 503, 504]

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        retry=retry_if_exception(is_retryable_exception)
    )
    def _fetch_page(self, url: str, delay: float) -> bytes:
        """
        Performs a single, robust HTTP GET request with delays and retries.

        Args:
            url (str): The URL to fetch.
            delay (float): The base delay in seconds. A random delay will be
                         calculated based on this value.

        Returns:
            bytes: The raw content of the HTTP response.
        
        Raises:
            requests.exceptions.RequestException: If the request fails after all retries.
        """
        # Calculate a randomized delay to mimic human behavior
        if delay <= 2.99:
            sleep_duration = round(uniform(1, 3), 2)
        else:
            sleep_duration = round(uniform(delay - (delay / 2), delay), 2)
        
        log.debug(f"Sleeping for {sleep_duration:.2f} seconds before request.")
        sleep(sleep_duration)
        
        try:
            log.debug(f"Requesting URL: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            log.debug(f"Successfully fetched {url} with status {response.status_code}")
            return response.content
        
        except requests.exceptions.RequestException as e:
            # Log the final error before tenacity re-raises the exception
            log.error(f"Failed to fetch {url} after all retries. Error: {e}")
            raise
    
    def _make_soup(self, html: bytes) -> BeautifulSoup:
        """Creates a BeautifulSoup object from raw HTML content."""
        return BeautifulSoup(html, "lxml")

    def fetch_soup(self, url: str, delay: Optional[float] = None) -> BeautifulSoup:
        """
        Fetches a URL and returns its content as a BeautifulSoup object.

        Args:
            url (str): The URL to fetch and parse.
            delay (float): The base delay for the request.

        Returns:
            BeautifulSoup: A parsed BeautifulSoup object of the page.
        """
        request_delay = delay if delay is not None else self.delay

        content = self._fetch_page(url, request_delay)
        return self._make_soup(content)

    def fetch_film(self, slug: str, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches the main page for a specific film."""
        url = f"{FILM_URL}{slug}/"
        return self.fetch_soup(url, delay)

    def fetch_nanogenres(self, slug: str, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches the nanogenres page for a specific film."""
        url = f"{FILM_URL}{slug}/nanogenres/"
        return self.fetch_soup(url, delay)

    def fetch_film_reviews(self, slug: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a film's popular reviews."""
        url = f"{BASE_URL}film/{slug}/reviews/by/activity/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_user(self, username: str, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches the main profile page for a specific user."""
        url = f"{BASE_URL}{username}/"
        return self.fetch_soup(url, delay)

    def fetch_list(self, username: str, list_name: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's list."""
        url = f"{BASE_URL}{username}/list/{list_name}/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_watchlist(self, username: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's watchlist."""
        url = f"{BASE_URL}{username}/watchlist/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_diary(self, username: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's diary."""
        url = f"{BASE_URL}{username}/films/diary/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_user_lists(self, username: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's collection of lists."""
        url = f"{BASE_URL}{username}/lists/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_reviews(self, username: str, page_num: int = 1 , delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's reviews."""
        url = f"{BASE_URL}{username}/films/reviews/page/{page_num}/"
        return self.fetch_soup(url, delay)
    
    def fetch_follows(self, username: str, page_num: int = 1 , delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's follows."""
        url = f"{BASE_URL}{username}/following/page/{page_num}/"
        return self.fetch_soup(url, delay)
    
    def fetch_followers(self, username: str, page_num: int = 1 , delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's followers."""
        url = f"{BASE_URL}{username}/followers/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_review_text(self, url: str, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches the full text of a review given its relative URL."""
        url = f"{BASE_URL}{url}"
        return self.fetch_soup(url, delay)

    def fetch_logs(self, username: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a specific page of a user's film logs."""
        url = f"{BASE_URL}{username}/films/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_search(self, query: str, page_num: int = 1, delay: Optional[float] = None) -> BeautifulSoup:
        """Fetches a page of popular films."""
        url = f"{BASE_URL}films/ajax/{query}/page/{page_num}/"
        return self.fetch_soup(url, delay)


# A single instance of the Fetcher to be used throughout the library,
# ensuring a single session is used for all requests.
fetcher = Fetcher()