import requests
import logging
from time import sleep
from random import uniform
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from scrapxd.config import BASE_URL, FILM_URL
from tenacity import retry, stop_after_attempt, wait_exponential


# TO DO: change 429 handling to user

log = logging.getLogger(__name__)

class Fetcher():
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})

    def is_retryable_exception(self, exception: Exception) -> bool:
        return (
            isinstance(exception, requests.exceptions.HTTPError) and
            exception.response.status_code in [429, 500, 502, 503, 504]
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        retry=is_retryable_exception
    )
    def _fetch_page(self, url: str, delay: float = 1):
        if delay <= 2.99:
            sleep(round(uniform(1, 3), 2))
        else:
            sleep(round(uniform(delay/2, delay), 2))
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.content
        
        except requests.exceptions.RequestException as e:
            log.error(f"Request Error - {e}")
            raise
    
    def _make_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def fetch_soup(self, url: str, delay: float = 1) -> BeautifulSoup:
        content = self._fetch_page(url, delay)
        return self._make_soup(content)

    def fetch_film(self, slug: str, delay: float = 1) -> BeautifulSoup:
        url = f"{FILM_URL}{slug}/"
        return self.fetch_soup(url, delay)

    def fetch_nanogenres(self, slug: str, delay: float = 1) -> BeautifulSoup:
        url = f"{FILM_URL}{slug}/nanogenres/"
        return self.fetch_soup(url, delay)

    def fetch_user(self, username: str, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/"
        return self.fetch_soup(url, delay)

    def fetch_list(self, username: str, list_name: str, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/list/{list_name}/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_watchlist(self, username: str, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/watchlist/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_diary(self, username: str, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/films/diary/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_user_lists(self, username: str, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/lists/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_reviews(self, username: str, page_num: int = 1 , delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/films/reviews/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_review_text(self, url: str, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{url}"
        return self.fetch_soup(url, delay)

    def fetch_logs(self, username: str, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}{username}/films/page/{page_num}"
        return self.fetch_soup(url, delay)

    def fetch_popular(self, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}films/ajax/popular/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_highest_rated(self, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}films/ajax/by/rating/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_by_decade(self, decade: int, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}films/ajax/popular/decade/{decade}s/page/{page_num}/"
        return self.fetch_soup(url, delay)

    def fetch_by_year(self, year: int, page_num: int = 1, delay: float = 1) -> BeautifulSoup:
        url = f"{BASE_URL}films/ajax/popular/year/{year}/page/{page_num}/"
        return self.fetch_soup(url, delay)
