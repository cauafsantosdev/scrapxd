"""
Facade module for the Scrapxd library.

This file defines the Scrapxd class, which provides a simplified interface for
fetching user and film data from Letterboxd, as well as searching for films.
It wraps the main models and fetcher, allowing easy access to core features.
"""
from .fetcher import Fetcher
from .models.user import User
from .models.film import Film
from .models.film_search import FilmSearch, FilmSearchResult

class Scrapxd:
    """
    The main entry point for the Scrapxd library.
    
    This class provides a simple interface to fetch User and Film objects,
    and to search for films.
    """
    def __init__(self, delay: float = 0):
        # Creates a single Fetcher instance shared by all objects.
        self.fetcher = Fetcher(delay=delay)

    def get_user(self, username: str) -> User:
        """
        Creates and returns a User object.

        Args:
            username (str): The Letterboxd username.

        Returns:
            User: A User instance ready to be used.
        """
        return User(username=username, fetcher=self.fetcher)

    def get_film(self, slug: str) -> Film:
        """
        Creates and returns a Film object.

        Args:
            slug (str): The film's slug.

        Returns:
            Film: A Film instance ready to be used.
        """
        return Film(slug=slug, fetcher=self.fetcher)
    
    def search_films(self, **kwargs) -> FilmSearchResult:
        """
        Searches for films using the provided keyword arguments.

        Keyword Args (all optional):
            decade (str): Decade of release (e.g., "1990s").
            year (int): Release year. (overrides decade if both provided).
            genre (str or List[str]): Genre(s) to include.
            not_genre (str or List[str]): Genre(s) to exclude.
            order_by (str): Sorting method ("popular" or other supported values).
            limit (int): Maximum number of results to return (default: 10).
            offset (int): Starting index for results (default: 0).

        Returns:
            FilmSearchResult: The result of the film search, containing matching films.
        """
        search_instance = FilmSearch(**kwargs, fetcher=self.fetcher)
        return search_instance.search()