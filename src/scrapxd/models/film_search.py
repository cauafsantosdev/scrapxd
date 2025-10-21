"""
Provides models and logic for searching films on Letterboxd.

Includes FilmSearch for building and executing search queries, and FilmSearchResult
for storing the results. Supports filtering by year, decade, genre, and sorting.
"""
import logging
from math import floor
from bs4 import BeautifulSoup
from typing import Optional, Union, List
from pydantic import BaseModel, ConfigDict

from .base import ScraperBase
from .film import Film
from ..analytics import FilmAnalytics
from ..export import DataExport

# Get a logger instance for this module
log = logging.getLogger(__name__)

class FilmSearchResult(BaseModel, FilmAnalytics, DataExport):
    """
    Stores the results of a film search, including the query string,
    total number of films found, and the list of Film objects.
    Provides analytics and export functionality.
    """
    query: str
    total_films_found: Optional[int] = None
    films: List[Film]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FilmSearch(ScraperBase):
    """
    Builds and executes a film search query for Letterboxd.

    Attributes:
        decade (str, optional): Decade of release (e.g., "1990s").
        year (int, optional): Release year.
        genre (str or List[str], optional): Genre(s) to include.
        not_genre (str or List[str], optional): Genre(s) to exclude.
        order_by (str): Sorting method ("popular", "rating", "year", "title", "recent").
        limit (int): Maximum number of results to return (default: 10).
        offset (int): Starting index for results (default: 0).
    """
    decade: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[Union[List[str], str]] = None
    not_genre: Optional[Union[List[str], str]] = None
    order_by: str = "popular"
    limit: int = 10
    offset: int = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __eq__(self, other):
        """
        Determines if two FilmSearch objects are equal by comparing their generated query string.
        """
        if isinstance(other, FilmSearch):
            return self._mount_query() == other._mount_query()
        return NotImplemented

    def __hash__(self):
        """
        Provides a hash for the FilmSearch object, based on its unique generated query string.
        This makes the object hashable and compatible with caching mechanisms.
        """
        return hash(self._mount_query())
    
    def _normalize_to_list(self, value: Union[str, list[str], None]) -> list[str]:
        """
        Converts a string or list to a list of strings. Returns an empty list if value is None.
        """
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value

    def _build_genre_string(self) -> str:
        """
        Builds a genre string for the query, including excluded genres prefixed with '-'.
        """
        genres = self._normalize_to_list(self.genre)
        not_genres = self._normalize_to_list(self.not_genre)

        not_genres_prefixed = [f"-{g}" for g in not_genres]

        all_genre_parts = genres + not_genres_prefixed

        return "+".join(all_genre_parts)

    def _mount_query(self) -> str:
        """
        Constructs the search query string based on the provided filters and sorting.
        """
        query = []

        if self.order_by == "popular":
            query.append("popular")
        
        if self.year:
            query.extend(["year", str(self.year)])
        elif self.decade:
            query.extend(["decade", self.decade])

        genre_string = self._build_genre_string()
        if genre_string:
            query.extend(["genre", genre_string])
        
        if self.order_by != "popular":
            query.extend(["by", self.order_by])
        
        return "/".join(query)

    def _parse_film_page(self, soup: BeautifulSoup, start: int, end: int) -> List[Film]:
        """
        Parses a page of search results and returns a list of Film objects.

        Args:
            soup (BeautifulSoup): Parsed HTML of the page.
            start (int): Start index for slicing results.
            end (int): End index for slicing results.

        Returns:
            List[Film]: List of Film objects found on the page.
        """
        films = []

        films_li = self._safe_find_all(soup, "li", class_="posteritem")

        for i in range(start, end):
            div = self._safe_find(films_li[i], "div", class_="react-component")
            slug = div.get("data-item-slug")
            if slug:
                films.append(Film(slug=slug))
        
        return films

    def search(self) -> FilmSearchResult:
        """
        Executes the search query and returns a FilmSearchResult object.

        Returns:
            FilmSearchResult: The result of the film search, including the query and films found.
        """
        films = []
        query = self._mount_query()

        start_index = self.offset
        end_index = self.offset + self.limit - 1

        starting_page = floor(start_index / 72) + 1
        ending_page = floor(end_index / 72) + 1

        for page_num in range(starting_page, ending_page + 1):
            soup = self._get_soup(self.fetcher.fetch_search, query, page_num)

            slice_start = 0
            if page_num == starting_page:
                slice_start = start_index % 72

            slice_end = 72
            if page_num == ending_page:
                slice_end = (end_index % 72) + 1

            films.extend(self._parse_film_page(soup, slice_start, slice_end))

        return FilmSearchResult(query=query, 
                                total_films_found=len(films),
                                films=films)