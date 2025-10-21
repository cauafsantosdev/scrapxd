"""
Defines the User model, representing a Letterboxd user and all their associated data.

Provides methods for scraping user profile information, logs, diary entries, reviews, lists, watchlist,
followers, and following. Includes export functionality to CSV and XLSX formats.
"""
import os
import re
import logging
from math import ceil
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
from functools import cached_property
from pydantic import computed_field, ConfigDict
from typing import List, Literal, Optional, Tuple

from .film import Film
from .entry import Entry
from ..config import BASE_URL
from .base import ScraperBase
from ..export import DataExport
from .film_list import FilmList
from .entry_list import EntryList

# Get a Logger instance for this module
log = logging.getLogger(__name__)

class User(ScraperBase, DataExport):
    """
    Attributes:
        username (str): The user's Letterboxd username.
        display_name (str): The user's display name.
        avatar (str): URL to the user's avatar image.
        bio (Optional[str]): The user's biography.
        location (Optional[str]): The user's location.
        total_logs (int): Total number of films logged.
        favourites (FilmList): List of favourite films.
        logs (EntryList): List of all logged films.
        diary (EntryList): List of diary entries.
        reviews (EntryList): List of reviews.
        lists (List[FilmList]): Custom film lists created by the user.
        watchlist (FilmList): The user's watchlist.
        following (List[User]): Users this user is following.
        total_follows (int): Number of users this user is following.
        followers (List[User]): Users following this user.
        total_followers (int): Number of followers.

    Methods:
        to_csv(output_dir): Exports all tabular data to CSV files.
        to_xlsx(output_dir): Exports all tabular data to XLSX files.
    """
    username: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        """
        Returns the username as the string representation of the User.
        """
        return self.username

    def __repr__(self):
        """
        Returns a formal string representation of the User object for debugging.
        """
        return f"User(username='{self.username}')"
    
    def __eq__(self, other):
        """
        Determines if two User objects are equal by comparing their usernames.

        Args:
            other (User): Another User object.

        Returns:
            bool: True if usernames match, False otherwise.
        """
        if isinstance(other, User):
            return self.username == other.username
        return NotImplemented

    def __hash__(self):
        """
        Provides a hash for the User object, based on its unique username.

        Returns:
            int: Hash of the username.
        """
        return hash(self.username)
    
    @computed_field
    @cached_property
    def display_name(self) -> str:
        """
        Returns the user's display name, scraped from their profile.

        Returns:
            str: The user's display name.
        """
        return self._parse_display_name()

    @computed_field
    @cached_property
    def avatar(self) -> str:
        """
        Returns the user's avatar URL, scraped from their profile.

        Returns:
            str: URL to the user's avatar image.
        """
        return self._parse_avatar()

    @computed_field
    @cached_property
    def bio(self) -> Optional[str]:
        """
        Returns the user's biography, scraped from their profile.

        Returns:
            Optional[str]: The user's biography, or None if not available.
        """
        return self._parse_bio()

    @computed_field
    @cached_property
    def location(self) -> Optional[str]:
        """
        Returns the user's location, scraped from their profile.

        Returns:
            Optional[str]: The user's location, or None if not available.
        """
        return self._parse_location()

    @computed_field
    @cached_property
    def total_logs(self) -> int:
        """
        Returns the total number of films watched by the user, scraped from their profile.

        Returns:
            int: Total number of films watched.
        """
        return self._parse_number_of_logs()
    
    @computed_field
    @cached_property
    def favourites(self) -> FilmList:
        """
        Returns the user's four favourite films list, scraped from their profile.
        
        Returns:
            FilmList: The user's favourite films.
        """
        return self._parse_favourites()
    
    @computed_field
    @cached_property
    def logs(self) -> EntryList:
        """
        Returns the list of films watched by the user, scraped from their profile.

        Returns:
            EntryList: The user's watched films log.
        """
        return self._parse_logs()
    
    @computed_field
    @cached_property
    def diary(self) -> EntryList:
        """
        Returns the user's diary entries, scraped from their profile.

        Returns:
            EntryList: The user's diary entries.
        """
        return self._parse_user_diary()
    
    @computed_field
    @cached_property
    def reviews(self) -> EntryList:
        """
        Returns the user's reviews, scraped from their profile.

        Returns:
            EntryList: The user's reviews.
        """
        return self._parse_user_reviews()
    
    @computed_field
    @cached_property
    def lists(self) -> List[FilmList]:
        """
        Returns the custom film lists created by the user, scraped from their profile.

        Returns:
            List[FilmList]: The user's custom film lists.
        """
        return self._parse_user_lists()
    
    @computed_field
    @cached_property
    def watchlist(self) -> FilmList:
        """
        Returns the user's watchlist, scraped from their profile.

        Returns:
            FilmList: The user's watchlist.
        """
        return self._parse_watchlist()
    
    @computed_field
    @cached_property
    def following(self) -> List["User"]:
        """
        Returns the list of users this user is following, scraped from their profile.

        Returns:
            List[User]: Users this user is following.
        """
        return self._parse_follows()

    @computed_field
    @cached_property
    def total_follows(self) -> int:
        """
        Returns the total number of users this user is following, scraped from their profile.

        Returns:
            int: Number of users followed.
        """
        return self._parse_follow_count()

    @computed_field
    @cached_property
    def followers(self) -> List["User"]:
        """
        Returns the list of users following this user, scraped from their profile.

        Returns:
            List[User]: Users following this user.
        """
        return self._parse_followers()

    @computed_field
    @cached_property
    def total_followers(self) -> int:
        """
        Returns the total number of followers for this user, scraped from their profile.

        Returns:
            int: Number of followers.
        """
        return self._parse_follower_count()

    def _parse_display_name(self) -> str:
        """
        Scrapes and returns the display name from the user's profile page.

        Returns:
            str: The display name.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            display_span = self._safe_find(soup, "span", class_="displayname tooltip")
            return str(display_span.string)
        except AttributeError:
            log.warning(f"Could not parse display name for user '{self.username}'.")
            return ""

    def _parse_avatar(self) -> str:
        """
        Scrapes and returns the avatar image URL from the user's profile page.

        Returns:
            str: URL to the avatar image.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            avatar_div = self._safe_find(soup, "div", class_="profile-avatar")
            img = self._safe_find(avatar_div, "img")

            return img.get("src")
        except AttributeError:
            log.warning(f"Could not parse avatar URL for user '{self.username}'.")
            return ""
    
    def _parse_bio(self) -> Optional[str]:
        """
        Scrapes and returns the user's biography from their profile page.

        Returns:
            Optional[str]: The biography text, or None if not available.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            meta_description = self._safe_find(soup, "meta", property="og:description")
            description_text = meta_description.get("content")

            if "Bio:" in description_text:
                return description_text.split("Bio: ")[-1]
            
            return None
        except AttributeError:
            log.warning(f"Could not parse bio for user '{self.username}'.")
            return None

    def _parse_location(self) -> Optional[str]:
        """
        Scrapes and returns the user's location from their profile page.

        Returns:
            str: The user's location string.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            location_div = self._safe_find(soup, "div", class_="metadatum -has-label js-metadatum")  

            if location_div:
                location_span = self._safe_find(location_div, "span", class_="label")
                return str(location_span.string)
            
            return None
        except AttributeError:
            log.warning(f"Could not parse location for user '{self.username}'.")
            return None
    
    def _parse_number_of_logs(self) -> int:
        """
        Scrapes and returns the number of films logged by the user from their profile page.

        Returns:
            int: The total number of films logged.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            statistic_header = self._safe_find(soup, "h4", class_="profile-statistic statistic")
            number = self._safe_find(statistic_header, "span", class_="value")
            return int(number.string.replace(",", ""))
        except (AttributeError, ValueError):
            log.warning(f"Could not parse number of logs for user '{self.username}'.")
            return 0

    def _parse_favourites(self) -> Optional[FilmList]:
        """
        Scrapes and returns the user's list of favourite films from their profile page.

        Returns:
            FilmList: The favourite films list of the user.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            favourites_li = self._safe_find_all(soup, "li", class_="posteritem favourite-production-poster-container") 

            if favourites_li:
                user_favourites = []

                for favourite in favourites_li:
                    div = self._safe_find(favourite, "div")
                    slug = div.get("data-item-slug")

                    user_favourites.append(Film(slug=slug))

                return FilmList(username = self.username,
                                title = f"{self.username}'s favourites",
                                number_of_films = len(user_favourites),
                                films = user_favourites)
            
            return None
        except AttributeError:
            log.warning(f"Could not parse favourites for user '{self.username}'.")
            return None

    def _parse_slugs(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts film slugs from a BeautifulSoup object containing film poster divs.

        Args:
            soup (BeautifulSoup): Parsed HTML of the page.

        Returns:
            List[str]: List of film slugs found on the page.
        """
        try:
            film_li = self._safe_find_all(soup, "li", class_="griditem")
            if film_li:
                film_divs = [self._safe_find(item, "div", class_="react-component") for item in film_li]
            else:
                film_divs = self._safe_find_all(soup, "div", class_="react-component figure")

            if not film_divs:
                return []
            
            slug_list = [div.get("data-item-slug") for div in film_divs if div]
            return slug_list
        except Exception as e:
            log.warning(f"Could not parse film slugs: {e}")
            return []
        
    def _parse_slugs_with_rating(self, soup: BeautifulSoup) -> Optional[List[Tuple[str, float]]]:
        """
        Extracts film slugs and their ratings from a BeautifulSoup object containing poster containers.

        Args:
            soup (BeautifulSoup): Parsed HTML of the page.

        Returns:
            Optional[List[Tuple[str, float]]]: List of (slug, rating) pairs found on the page.
        """
        try:
            films_li = self._safe_find_all(soup, "li", class_="griditem")

            if not films_li:
                return []
            
            film_list = []
            for item in films_li:
                try:
                    film_div = self._safe_find(item, "div", class_="react-component")
                    if not film_div:
                        continue
                    
                    slug = film_div.get("data-item-slug")

                    rating = None
                    rating_span = item.find("span", class_=re.compile(r"\brated-\d+\b"))
                    if rating_span:
                        raw_rating_class = rating_span.get("class")[3]
                        if raw_rating_class:
                            rating_value = raw_rating_class.replace("rated-", "")
                            if rating_value.isdigit():
                                rating = int(rating_value) / 2

                    film_list.append((slug, rating))
                except (AttributeError, IndexError, TypeError, ValueError) as e:
                    log.warning(f"Could not parse slug or rating for a film item: {e}")
                    continue

            return film_list
        except Exception as e:
            log.warning(f"Could not parse slugs with rating: {e}")
            return []

    def _parse_count(self, soup: BeautifulSoup) -> int:
        """
        Extracts the count of items (logs, diary entries, reviews, or lists) from the user's page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the page.

        Returns:
            int: The count of items found.
        """
        try:
            div = self._safe_find(soup, "div", id="content-nav")
            tooltip = self._safe_find(div, "span", class_="tooltip")

            raw_count = tooltip.get("data-original-title")
            if not raw_count:
                raw_count = tooltip.get("title")

            count_match = re.match(r"\d+", raw_count)
            return int(count_match.group(0))
        except (AttributeError, TypeError, ValueError) as e:
            log.warning(f"Could not parse count for type '{type}' in user '{self.username}': {e}")
            return 0
    
    def _parse_logs(self) -> EntryList:
        """
        Scrapes and returns the user's log entries (watched films), including ratings.

        Returns:
            EntryList: List of logged films with ratings.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_logs, self.username)
            log_count = self._parse_count(soup)
            
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
        except Exception as e:
            log.warning(f"Could not parse logs for user '{self.username}': {e}")
            return EntryList(
                username=self.username,
                title=f"{self.username}'s films",
                number_of_entries=0,
                entries=[]
            )
    
    def _parse_diary_page(self, soup: BeautifulSoup) -> List[Entry]:
        """
        Parses a single diary page and extracts diary entries with date, film slug, rating, and review link.

        Args:
            soup (BeautifulSoup): Parsed HTML of the diary page.

        Returns:
            List[Entry]: List of diary entries found on the page.
        """
        from .film import Film

        diary_page = []
        try:
            rows = self._safe_find_all(soup, "tr", class_="diary-entry-row viewing-poster-container")

            for row in rows:
                try:
                    # Extract date
                    date_pattern = re.compile(r"/([^/]+)/films/diary/for/(\d{4}/\d{2}/\d{2})/")
                    date_anchor = self._safe_find(row, "a", href=date_pattern)
                    date_href = date_anchor.get("href")
                    date_match = date_pattern.search(date_href)
                    date_string = date_match.group(2)
                    entry_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

                    # Extract film slug
                    film_data = self._safe_find(row, "div", class_="react-component figure")
                    slug = film_data.get("data-item-slug")

                    # Extract entry rating
                    rating_span = self._safe_find(row, "span", class_=re.compile("^rating rated-"))
                    raw_rating = rating_span.get("class")[1]
                    rating = int(raw_rating[6:]) / 2

                    # Extract review (if available)
                    review_anchor = self._safe_find(row, "a", class_="has-icon icon-review icon-16 tooltip")
                    review = None
                    if review_anchor:
                        review_url = review_anchor.get("href")
                        review = f"{BASE_URL}{review_url[1:]}"

                    entry = Entry(
                        film=Film(slug=slug),
                        watched_date=entry_date,
                        rating=rating,
                        review=review
                    )
                    diary_page.append(entry)
                except Exception as e:
                    log.warning(f"Could not parse a diary entry for user '{self.username}': {e}")

        except Exception as e:
            log.error(f"Could not parse a diary page for user '{self.username}': {e}")

        return diary_page

    def _parse_user_diary(self) -> EntryList:
        """
        Scrapes and returns all diary entries for the user, handling pagination.

        Returns:
            EntryList: All diary entries for the user.
        """
        try:
            first_page_soup = self._get_soup(self.fetcher.fetch_diary, self.username)
            entry_count = self._parse_count(first_page_soup)
            diary = [entry for entry in self._parse_diary_page(first_page_soup)]

            if entry_count > 50:
                page_count = ceil(entry_count / 50)
                for page in range(2, page_count + 1):
                    try:
                        soup = self._get_soup(self.fetcher.fetch_diary, self.username, page)
                        diary.extend(self._parse_diary_page(soup))
                    except Exception as e:
                        log.warning(f"Could not parse diary page {page} for user '{self.username}': {e}")

            return EntryList(username=self.username,
                             title = f"{self.username}'s diary",
                             number_of_entries=entry_count,
                             entries=diary)
        except Exception as e:
            log.error(f"Could not parse user diary for '{self.username}': {e}")
            return []

    def _parse_review_page(self, soup: BeautifulSoup) -> List[Entry]:
        """
        Parses a single review page and extracts reviews with date, film slug, rating, and review text.

        Args:
            soup (BeautifulSoup): Parsed HTML of the review page.

        Returns:
            List[Entry]: List of reviews found on the page.
        """
        review_page = []
        try:
            reviews = self._safe_find_all(soup, "article", class_="production-viewing -viewing viewing-poster-container js-production-viewing")

            for item in reviews:
                try:
                    # Extract date
                    raw_date = self._safe_find(item, "time")
                    date_string = raw_date.get("datetime")
                    review_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

                    # Extract slug
                    film_data = self._safe_find(item, "div", class_="react-component figure")
                    slug = film_data.get("data-item-slug")
                    
                    # Extract rating
                    rating_span = self._safe_find(item, "span", class_=re.compile("^rating -green rated-"))
                    raw_rating = rating_span.get("class")[2]
                    rating = int(raw_rating[6:]) / 2

                    # Extract review text
                    collapsed_text = self._safe_find(item, "div", class_="collapsed-text")
                    if collapsed_text:
                        # collapsed-text div means the text needs to be acessed at it's own URL
                        url_div = self._safe_find(item, "div", class_="body-text -prose -reset js-review-body js-collapsible-text")
                        text_url = url_div.get("data-full-text-url")
                        text_soup = self._get_soup(self.fetcher.fetch_review_text, text_url[1:])
                        paragraphs = self._safe_find_all(text_soup, "p")
                        text = "".join(p.get_text(separator=" ", strip=True) for p in paragraphs)
                    else:
                        paragraph = self._safe_find(item, "p")
                        text = paragraph.get_text(separator=" ", strip=True)

                    review = Entry(
                        film=Film(slug=slug),
                        watched_date=review_date,
                        rating=rating,
                        review=text
                    )
                    review_page.append(review)
                except Exception as e:
                    log.warning(f"Could not parse a review for user '{self.username}': {e}")

        except Exception as e:
            log.error(f"Could not parse review page for user '{self.username}': {e}")

        return review_page

    def _parse_user_reviews(self) -> EntryList:
        """
        Scrapes and returns all reviews for the user, handling pagination.

        Returns:
            EntryList: All reviews for the user.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_reviews, self.username)
            review_count = self._parse_count(soup)
            reviews = [entry for entry in self._parse_review_page(soup)]

            if review_count > 12:
                page_count = ceil(review_count / 12)
                for page in range(2, page_count + 1):
                    try:
                        soup = self._get_soup(self.fetcher.fetch_reviews, self.username, page)
                        reviews.extend(self._parse_review_page(soup))
                    except Exception as e:
                        log.warning(f"Could not parse review page {page} for user '{self.username}': {e}")

            return EntryList(username=self.username,
                             title = f"{self.username}'s reviews",
                             number_of_entries=review_count,
                             entries=reviews)
        except Exception as e:
            log.error(f"Could not parse user reviews for '{self.username}': {e}")
            return []

    def _parse_film_list(self, soup: BeautifulSoup, title_url: str) -> Optional[FilmList]:
        """
        Parses a film list page and extracts the list title, number of films, and all films in the list.

        Args:
            soup (BeautifulSoup): Parsed HTML of the film list page.
            title_url (str): The URL slug for the list.

        Returns:
            FilmList: The parsed film list object, or None if parsing fails.
        """
        try:
            first_page_soup = soup

            # Extract list title
            title_h1 = self._safe_find(soup, "h1", class_="title-1 prettify")
            if not title_h1:
                return None
            title = str(title_h1.string)

            # Extract the total number of films in the list
            list_description = self._safe_find(soup, "meta", attrs={"name": "description"})
            if not list_description:
                return None
            description_content = list_description.get("content")
            count_match = re.search(r'(\d+)\s+films', description_content)
            if not count_match:
                return None
            total_films = int(count_match.group(1))
            
            # Extracts slugs and handles pagination
            slug_list = []
            page_count = ceil(total_films / 105)
            for page in range(1, page_count + 1):
                try:
                    if page > 1:
                        soup = self._get_soup(self.fetcher.fetch_list, self.username, title_url, page)

                    if not soup:
                        log.info(f"Stopping pagination for list '{title_url}' at page {page} as no more content was found.")
                        break

                    films_li = self._safe_find_all(soup, "li", class_="posteritem")
                    for film in films_li:
                        try:
                            div = self._safe_find(film, "div", class_="react-component")
                            slug = div.get("data-item-slug")
                            if slug:
                                slug_list.append(slug)
                        except Exception as e:
                            log.warning(f"Could not parse a film item in list '{title}' for '{self.username}': {e}")
                except Exception as e:
                    log.warning(f"Could not parse list page {page} for '{self.username}': {e}")

            # Creates Film objects for all slugs parsed
            films = [Film(slug=slug) for slug in slug_list]

            # Some film lists are ranked/numbered by the user
            is_numbered = self._safe_find(first_page_soup, "li", class_="poster-container numbered-list-item")
            if is_numbered:
                films = {i: v for i, v in enumerate(films, start=1)}

            return FilmList(username=self.username, 
                            title=title, 
                            number_of_films=total_films, 
                            films=films)
        except Exception as e:
            log.error(f"Could not parse film list for '{self.username}': {e}")
            return None

    def _parse_list_page(self, soup: BeautifulSoup) -> List[FilmList]:
        """
        Parses a page containing multiple film lists and extracts each FilmList.

        Args:
            soup (BeautifulSoup): Parsed HTML of the lists page.

        Returns:
            List[FilmList]: List of FilmList objects found on the page.
        """
        try:
            list_divs = self._safe_find_all(soup, "div", class_="listitem js-listitem")
            lists_on_page = []

            if not list_divs:
                return []

            for film_list_div in list_divs:
                try:
                    list_anchor = self._safe_find(film_list_div, "a", class_="poster-list-link")
                    if not list_anchor:
                        continue
                    
                    list_href = list_anchor.get("href")
                    if not list_href:
                        continue

                    match = re.search(r'/list/([^/]+)', list_href)
                    if not match:
                        continue

                    list_slug = match.group(1)

                    list_soup = self._get_soup(self.fetcher.fetch_list, self.username, list_slug)

                    if list_soup:
                        parsed_list = self._parse_film_list(list_soup, list_slug)
                        if parsed_list:
                            lists_on_page.append(parsed_list)
                except Exception as e:
                    log.warning(f"Could not parse a single film list item for '{self.username}': {e}")

            return lists_on_page
        except Exception as e:
            log.error(f"Could not parse the main user lists page for '{self.username}': {e}")
            return []

    def _parse_user_lists(self) -> List[FilmList]:
        """
        Scrapes and returns all custom film lists created by the user, handling pagination.

        Returns:
            List[FilmList]: All FilmList objects created by the user.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user_lists, self.username)
            has_lists = self._safe_find(soup, "div", class_="list-summary-list -marginblockstart")

            if not has_lists:
                return []

            list_count = self._parse_count(soup)
            user_lists = [film_list for film_list in self._parse_list_page(soup)]

            if list_count > 12:
                page_count = ceil(list_count / 12)
                for page in range(2, page_count + 1):
                    try:
                        soup = self._get_soup(self.fetcher.fetch_user_lists, self.username, page)
                        user_lists.extend(self._parse_list_page(soup))
                    except Exception as e:
                        log.warning(f"Could not parse user list page {page} for '{self.username}': {e}")

            return user_lists
        except Exception as e:
            log.error(f"Could not parse user lists for '{self.username}': {e}")
            return []

    def _parse_watchlist(self) -> FilmList:
        """
        Scrapes and returns the user's watchlist, handling pagination.

        Returns:
            FilmList: The user's watchlist as a FilmList object.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_watchlist, self.username)
            
            count_span = self._safe_find(soup, "span", class_="js-watchlist-count")
            raw_count = str(count_span.string)
            count_match = re.match(r"\d+", raw_count)
            film_count = int(count_match.group(0))

            watchlist_slugs = [slug for slug in self._parse_slugs(soup)]

            if film_count > 28:
                page_count = ceil(film_count / 28)
                for page in range(2, page_count + 1):
                    try:
                        soup = self._get_soup(self.fetcher.fetch_watchlist, self.username, page)
                        slugs = self._parse_slugs(soup)
                        if slugs:
                            watchlist_slugs.extend(slugs)
                    except Exception as e:
                        log.warning(f"Could not parse watchlist page {page} for '{self.username}': {e}")

            return FilmList(
                username=self.username,
                title=f"{self.username}'s Watchlist",
                number_of_films=film_count,
                films=[Film(slug=slug) for slug in watchlist_slugs]
            )
        except Exception as e:
            log.error(f"Could not parse watchlist for '{self.username}': {e}")
            return FilmList(username=self.username,
                            title=f"{self.username}'s Watchlist",
                            number_of_films=0, 
                            films=[])

    def _parse_follow_count(self) -> int:
        """
        Scrapes and returns the number of users this user is following.

        Returns:
            int: Total number of users followed.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            statistic_headers = self._safe_find_all(soup, "h4", class_="profile-statistic statistic")
            following_header = statistic_headers[3]
            total_follows = self._safe_find(following_header, "span", class_="value")
            return int(total_follows.string.replace(",", ""))
        except Exception as e:
            log.error(f"Could not parse follow count for '{self.username}': {e}")
            return 0

    def _parse_follows(self) -> List["User"]:
        """
        Scrapes and returns the list of users this user is following, handling pagination.

        Returns:
            List[User]: List of User objects this user is following.
        """
        follows = []
        try:
            for i in range(1, ceil(self.total_follows/25)+1):
                try:
                    soup = self._get_soup(self.fetcher.fetch_follows, self.username, i)
                    user_anchors = self._safe_find_all(soup, "a", class_="avatar -a40")

                    if user_anchors:
                        usernames = [anchor.get("href").replace("https://letterboxd.com", "").replace("/", "") 
                                     for anchor in user_anchors]
                        follows.extend([User(username=u) for u in usernames])
                except Exception as e:
                    log.warning(f"Could not parse follows page {i} for '{self.username}': {e}")

        except Exception as e:
            log.error(f"Could not parse follows for '{self.username}': {e}")
        return follows

    def _parse_follower_count(self) -> int:
        """
        Scrapes and returns the number of followers for this user.

        Returns:
            int: Total number of followers.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_user, self.username)
            statistic_headers = self._safe_find_all(soup, "h4", class_="profile-statistic statistic")
            followers_header = statistic_headers[4]
            total_followers = self._safe_find(followers_header, "span", class_="value")
            return int(total_followers.string.replace(",", ""))
        except Exception as e:
            log.error(f"Could not parse follower count for '{self.username}': {e}")
            return 0

    def _parse_followers(self) -> List["User"]:
        """
        Scrapes and returns the list of users following this user, handling pagination.

        Returns:
            List[User]: List of User objects following this user.
        """
        followers = []
        try:
            for i in range(1, ceil(self.total_followers/25)+1):
                try:
                    soup = self._get_soup(self.fetcher.fetch_followers, self.username, i)
                    user_anchors = self._safe_find_all(soup, "a", class_="avatar -a40")

                    if user_anchors:
                        usernames = [anchor.get("href").replace("https://letterboxd.com", "").replace("/", "") 
                                     for anchor in user_anchors]
                        followers.extend([User(username=u) for u in usernames])
                except Exception as e:
                    log.warning(f"Could not parse followers page {i} for '{self.username}': {e}")

        except Exception as e:
            log.error(f"Could not parse followers for '{self.username}': {e}")
        return followers
    
    def to_csv(self, output_dir: str = None):
        """
        Exports all of the user's tabular data (watchlist, logs, reviews, etc.)
        to separate CSV files inside a specified directory.

        Args:
            output_dir (str, optional): The directory to save the files in.
                                        Defaults to a new directory named after the username.
        """
        if output_dir is None:
            output_dir = self.username
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        log.info(f"Exporting user data to directory: '{output_dir}'")

        export_tasks = {
            "favourites": self.favourites,
            "watchlist": self.watchlist,
            "logs": self.logs,
            "reviews": self.reviews,
            "diary": self.diary,
            "lists": self.lists
        }

        for name, data_object in export_tasks.items():
            try:
                if name == "lists":
                    for film_list in data_object:
                        sanitized_title = re.sub(r'[\\/:"*?<>|\s]+', '_', film_list.title)
                        filepath = os.path.join(output_dir, f"{self.username}_{sanitized_title}.csv")
                        log.info(f"Exporting {film_list.title} list to {filepath}...")
                        film_list.to_csv(filepath=filepath)
                else:
                    filepath = os.path.join(output_dir, f"{self.username}_{name}.csv")
                    log.info(f"Exporting {name} to {filepath}...")
                    data_object.to_csv(filepath=filepath)
            
            except Exception as e:
                log.error(f"Failed to export {name} for user {self.username}: {e}")

    def to_xlsx(self, output_dir: str = None):
        """
        Exports all of the user's tabular data (watchlist, logs, reviews, etc.)
        to separate XLSX files inside a specified directory.

        Args:
            output_dir (str, optional): The directory to save the files in.
                                        Defaults to a new directory named after the username.
        """
        if output_dir is None:
            output_dir = self.username

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        log.info(f"Exporting user data to directory: '{output_dir}'")

        export_tasks = {
            "favourites": self.favourites,
            "watchlist": self.watchlist,
            "logs": self.logs,
            "reviews": self.reviews,
            "diary": self.diary,
            "lists": self.lists
        }

        for name, data_object in export_tasks.items():
            try:
                if name == "lists":
                    for _, film_list in enumerate(data_object):
                        sanitized_title = re.sub(r'[\\/:"*?<>|]+', '_', film_list.title)
                        filepath = os.path.join(output_dir, f"{self.username}_list_{sanitized_title}.xlsx")
                        log.info(f"Exporting {film_list.title} list to {filepath}...")
                        film_list.to_xlsx(filepath=filepath)
                else:
                    filepath = os.path.join(output_dir, f"{self.username}_{name}.xlsx")
                    log.info(f"Exporting {name} to {filepath}...")
                    data_object.to_xlsx(filepath=filepath)

            except Exception as e:
                log.error(f"Failed to export {name} for user {self.username}: {e}")