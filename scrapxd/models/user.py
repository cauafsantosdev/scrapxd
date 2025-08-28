import re
import logging
from math import ceil
from datetime import date
from bs4 import BeautifulSoup
from pydantic import BaseModel, computed_field
from functools import lru_cache, cached_property
from typing import List, Literal, Optional, Tuple
from .film import Film
from .entry import Entry
from .user_list import UserList
from .entry_list import EntryList
from scrapxd.config import BASE_URL
from scrapxd.fetcher import Fetcher, fetcher as default_fetcher


log = logging.getLogger(__name__)

class User(BaseModel):
    username: str
    fetcher: Fetcher = default_fetcher

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"User(username='{self.username}')"

    @lru_cache()
    def _get_soup(self, fetch_function, *args) -> Optional[BeautifulSoup]:
        """
        Generic helper to fetch and cache soup objects using a specific fetcher function.
        The cache is keyed by the function and its arguments.
        """
        func_name = fetch_function.__name__
        log.debug(f"Requesting page for '{self.username}' using '{func_name}' with args {args}")

        soup = fetch_function(*args)

        if soup:
            log.debug(f"Soup for '{func_name}' fetched successfully.")
        else:
            log.warning(f"Failed to fetch soup for '{func_name}' with args {args}.")

        return soup

    @computed_field
    @cached_property
    def total_logs(self) -> int:
        return self._parse_number_of_logs()
    
    @computed_field
    @cached_property
    def favourites(self) -> UserList:
        return self._parse_favourites()
    
    @computed_field
    @cached_property
    def logs(self) -> EntryList:
        return self._parse_logs()
    
    @computed_field
    @cached_property
    def diary(self) -> EntryList:
        return self._parse_user_diary()
    
    @computed_field
    @cached_property
    def reviews(self) -> EntryList:
        return self._parse_user_reviews()
    
    @computed_field
    @cached_property
    def lists(self) -> List[UserList]:
        return self._parse_user_lists()
    
    @computed_field
    @cached_property
    def watchlist(self) -> UserList:
        return self._parse_watchlist()
    
    def _parse_number_of_logs(self) -> int:
        soup = self._get_soup(self.fetcher.fetch_user, self.username)
        statistic_header = soup.find("h4", class_="profile-statistic statistic")
        number = statistic_header.find("span", class_="value")
        return int(number.string)

    def _parse_favourites(self) -> UserList | None:
        soup = self._get_soup(self.fetcher.fetch_user, self.username)
        favourites_li = soup.find_all("li", class_="poster-container favourite-film-poster-container") 

        if favourites_li:
            user_favourites = []

            for favourite in favourites_li:
                div = favourite.find("div")
                slug = div.get("data-film-slug")

                user_favourites.append(Film(slug=slug))

            return UserList(username = self.username,
                            title = f"{self.username}'s favourites",
                            number_of_films = len(user_favourites),
                            films = user_favourites)
        
        return None

    def _parse_slugs(self, soup: BeautifulSoup) -> List[str]:
        film_divs = soup.find_all("div", class_="really-lazy-load poster film-poster linked-film-poster")

        if film_divs:
            slug_list = []

            for div in film_divs:
                slug = div.get("data-film-slug")
                slug_list.append(slug)

            return slug_list
        
        else:
            return []
        
    def _parse_slugs_with_rating(self, soup: BeautifulSoup) -> Optional[List[Tuple[str, float]]]:
        films_li = soup.find_all("li", class_="poster-container")

        if films_li:
            film_list = []

            for item in films_li:
                film_div = item.find("div", class_="really-lazy-load poster film-poster linked-film-poster")
                slug = film_div.get("data-film-slug")

                rating_span = item.find("span", class_=re.compile("^rating -micro -darker rated-"))
                raw_rating = rating_span.get("class")[3]
                rating = int(raw_rating[6:]) / 2

                film_list.append([slug, rating])

            return film_list
        
        else:
            return []

    def _parse_count(self, soup: BeautifulSoup, type: Literal["Watched", "Diary", "Reviews", "Lists"]) -> int:
        if type == "Lists":
            div = soup.find("div", id="content-nav")
            tooltip = div.find("span", class_="tooltip")

        else:
            tooltip = soup.find("a", class_="tooltip", string=type)

        raw_count = tooltip.get("title")
        count_match = re.match(r"\d+", raw_count)
        return int(count_match.group(0))
    
    def _parse_logs(self) -> EntryList:
        soup = self._get_soup(self.fetcher.fetch_logs, self.username)
        log_count = self._parse_count(soup, "Watched")
        
        user_logs = [i for i in self._parse_slugs_with_rating(soup)]

        if log_count > 72:
            page_count = ceil(log_count / 72)

            for i in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_logs, self.username, i)
                slugs = self._parse_slugs_with_rating(soup)

                user_logs.extend(slugs)

        return EntryList(username = self.username,
                        title = f"{self.username}'s films",
                        number_of_entries = log_count,
                        entries = [Entry(film=Film(slug=i[0]), rating=i[1]) for i in user_logs])

    def _parse_diary_page(self, soup: BeautifulSoup) -> List[Entry]:
        diary_page = []

        rows = soup.find_all("tr", class_="diary-entry-row viewing-poster-container")

        for row in rows:
            date_pattern = re.compile(r"/([^/]+)/films/diary/for/(\d{4}/\d{2}/\d{2})/")
            date_anchor = row.find("a", href=date_pattern)
            date_href = date_anchor.get("href")
            date_match = date_pattern.search(date_href)
            date_string = date_match.group(2)
            entry_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

            film_data = row.find("td", class_="td-actions film-actions has-menu hide-when-logged-out")
            slug = film_data.get("data-film-slug")

            rating_span = row.find("span", class_=re.compile("^rating rated-"))
            raw_rating = rating_span.get("class")[1]
            rating = int(raw_rating[6:]) / 2

            review_anchor = row.find("a", class_="has-icon icon-review icon-16 tooltip")
            
            if review_anchor:
                review_url = review_anchor.get("href")
                review = f"{BASE_URL}{review_url[1:]}"

            entry = Entry(film = slug, 
                        watched_date = entry_date, 
                        rating = rating, 
                        review = review if review_anchor else None)

            diary_page.append(entry)

        return diary_page
    
    def _parse_user_diary(self) -> List[Entry]:
        first_page_soup = self._get_soup(self.fetcher.fetch_diary, self.username)

        entry_count = self._parse_count(first_page_soup, "Diary")
        diary = [entry for entry in self._parse_diary_page(first_page_soup)]

        if entry_count > 50:
            page_count = ceil(entry_count / 50)

            for page in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_diary, self.username, page)
                diary.extend(self._parse_diary_page(soup))
        
        return diary

    def _parse_review_page(self, soup: BeautifulSoup) -> List[Entry]:
        review_page = []

        reviews = soup.find_all("article", class_="production-viewing -viewing viewing-poster-container js-production-viewing")

        for item in reviews:
            raw_date = item.find("time")
            date_string = raw_date.get("datetime")
            review_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

            film_data = item.find("div", class_="really-lazy-load poster film-poster linked-film-poster")
            slug = film_data.get("data-film-slug")
            
            rating_span = item.find("span", class_=re.compile("^rating -green rated-"))
            raw_rating = rating_span.get("class")[2]
            rating = int(raw_rating[6:]) / 2

            collapsed_text = item.find("div", class_="collapsed-text")

            if collapsed_text:
                url_div = item.find("div", class_="body-text -prose -reset js-review-body js-collapsible-text")
                text_url = url_div.get("data-full-text-url")
                text_soup = self._get_soup(self.fetcher.fetch_review_text, text_url[1:])

                text = []
                paragraphs = text_soup.find_all("p")

                for p in paragraphs:
                    text.append(p.get_text(separator=" ", strip=True))

                text = "".join(text)

            else:
                paragraph = item.find("p")
                text = paragraph.get_text(separator=" ", strip=True)

            review = Entry(film = Film(slug=slug),
                        watched_date = review_date,
                        rating = rating,
                        review = text
            )

            review_page.append(review)

        return review_page
    
    def _parse_user_reviews(self) -> List[Entry]:
        soup = self._get_soup(self.fetcher.fetch_reviews, self.username)
        review_count = self._parse_count(soup, "Reviews")

        reviews = [entry for entry in self._parse_review_page(soup)]

        if review_count > 12:
            page_count = ceil(review_count / 12)

            for page in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_reviews, self.username, page)
                reviews.extend(self._parse_review_page(soup))
        
        return reviews

    def _parse_film_list(self, soup: BeautifulSoup, title_url: str) -> UserList:
        title_h1 = soup.find("h1", class_="title-1 prettify")
        title = str(title_h1.string)

        list_description = soup.find("meta", attrs={"name": "description"})
        description_content = list_description.get("content")
        count_match = re.search(r'(\d+)\s+films', description_content)
        total_films = int(count_match.group(1))

        films = [slug for slug in self._parse_slugs(soup)]

        if total_films > 100:
            page_count = ceil(total_films / 100)

            for page in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_list, self.username, title_url, page)
                films.extend(self._parse_slugs(soup))

        films = [Film(slug=slug) for slug in films]

        is_numbered = soup.find("li", class_="poster-container numbered-list-item")
        if is_numbered:
            films = {i:v for i, v in enumerate(films, start=1)}

        return UserList(username = self.username,
                        title = title,
                        number_of_films = total_films,
                        films = films)

    def _parse_list_page(self, soup: BeautifulSoup) -> Optional[List[UserList]]:
        lists_section = soup.find_all("section", class_="list js-list -overlapped -summary")

        if lists_section:
            lists_on_page = []

            for film_list in lists_section:
                list_anchor = film_list.find("a", class_="list-link")
                list_href = list_anchor.get("href")
                title_match = re.match(r'^list/([^/]+)/$', list_href)
                
                list_soup = self._get_soup(self.fetcher.fetch_list, self.username, title_match)

                lists_on_page.append(self._parse_film_list(list_soup, title_match))
            
            return lists_on_page
        
        return []
    
    def _parse_user_lists(self) -> Optional[List[UserList]]:
        soup = self._get_soup(self.fetcher.fetch_user_lists, self.username)
        has_lists = soup.find("section", class_="list-set")

        if not has_lists:
            return []

        list_count = self._parse_count(soup, "Lists")

        user_lists = [film_list for film_list in self._parse_list_page(soup)]

        if list_count > 12:
            page_count = ceil(list_count / 12)

            for page in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_user_lists, self.username, page)
                user_lists.extend(self._parse_list_page(self._get_soup(page)))

        return user_lists
        
    def _parse_watchlist(self) -> UserList:
        soup = self._get_soup(self.fetcher.fetch_watchlist, self.username)

        count_span = soup.find("span", class_="js-watchlist-count")
        raw_count = str(count_span.string)
        count_match = re.match(r"\d+", raw_count)
        film_count = int(count_match.group(0))

        watchlist_slugs = [slug for slug in self._parse_slugs(soup)]

        if film_count > 28:
            page_count = ceil(film_count / 28)

            for page in range(2, page_count + 1):
                soup = self._get_soup(self.fetcher.fetch_watchlist, self.username, page)
                slugs = self._parse_slugs(soup)

                if slugs:
                    watchlist_slugs.extend(slugs)

        return UserList(username = self.username,
                        title = f"{self.username}'s Watchlist",
                        number_of_films = film_count,
                        films = [Film(slug=slug) for slug in watchlist_slugs])