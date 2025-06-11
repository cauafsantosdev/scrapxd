import requests
import logging
from time import sleep
from fake_useragent import UserAgent
from scrapxd.config import BASE_URL, FILM_URL


log = logging.getLogger(__name__)
ua = UserAgent()
session = requests.Session()

def _fetch_page(url: str, delay: int = 1):
    session.headers["UserAgent"] = ua.random

    if delay > 0:
        sleep(delay)
    
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.content
    
    except requests.exceptions.RequestException as e:
        log.error(f"Request Error - {e}")
        raise

def fetch_film(slug: str, delay: int = 1) -> str:
    url = f"{FILM_URL}{slug}/"

    content = _fetch_page(url, delay)
    return content

def fetch_user(username: str, delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/"

    content = _fetch_page(url, delay)
    return content

def fetch_list(username: str, list_name: str, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/list/{list_name}/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_watchlist(username: str, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/watchlist/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_diary(username: str, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/films/diary/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_reviews(username: str, page_num: int = 1 , delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/films/reviews/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_logs(username: str, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}{username}/films/page/{page_num}"

    content = _fetch_page(url, delay)
    return content

def fetch_popular(page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}films/ajax/popular/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_highest_rated(page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}films/ajax/by/rating/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_by_decade(decade: int, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}films/ajax/popular/decade/{decade}s/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content

def fetch_by_year(year: int, page_num: int = 1, delay: int = 1) -> str:
    url = f"{BASE_URL}films/ajax/popular/year/{year}/page/{page_num}/"

    content = _fetch_page(url, delay)
    return content
