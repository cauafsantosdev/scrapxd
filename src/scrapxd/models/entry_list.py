"""
Defines the EntryList model for Scrapxd, representing a list of film entries (logs, reviews, diary, etc.)
scraped from Letterboxd. 

Includes metadata, analytics, export functionality, and search utilities.
"""
from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import List, Union, TYPE_CHECKING

from .entry import Entry
from ..analytics import EntryAnalytics
from ..export import DataExport


class EntryList(BaseModel, EntryAnalytics, DataExport):
    """
    Represents a list of film entries scraped from Letterboxd, including metadata,
    analytics, export functionality, and search utilities.
    """
    username: str
    title: str
    number_of_entries: int
    entries: List[Entry]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        """Returns a human-readable string representation of the entry list."""
        return f"{self.title} ({self.number_of_entries} {'reviews' if 'reviews' in self.title else 'entries'})"
    
    def __repr__(self):
        """Returns a formal string representation of the EntryList object for debugging."""
        return (
            f"EntryList(title='{self.title}', username='{self.username}', "
            f"number_of_entries={self.number_of_entries}, "
            f"entries=[{', '.join(repr(e) for e in self.entries[:3])}"
            f"{', ...' if len(self.entries) > 3 else ''}])"
        )
    
    def search_film(self, film: Union[str, "Film"]) -> List[Entry]:
        """
        Searches for entries matching a given film (by slug or Film object).

        Args:
            film (str or Film): The film slug or Film object to search for.

        Returns:
            List[Entry]: Entries matching the given film.
        """
        from .film import Film
        
        film_entries = []
        
        if isinstance(film, Film):
            film = film.slug

        for entry in self.entries:
            if entry.film.slug == film:
                film_entries.append(entry)
            
        return film_entries
    
    def search_date(self, given_date: date) -> List[Entry]:
        """
        Searches for entries watched on a specific date.

        Args:
            given_date (date): The date to search for.

        Returns:
            List[Entry]: Entries watched on the given date.
        """
        entries_on_date = []

        for entry in self.entries:
            if entry.watched_date == given_date:
                entries_on_date.append(entry)

        return entries_on_date
    
    def search_in_range(self, start_date: date, end_date: date) -> List[Entry]:
        """
        Searches for entries watched on a range of dates.

        Args:
            start_date (date): The starting date of the searching range.
            end_date (date): The ending date of the searching range.

        Returns:
            List[Entry]: Entries watched on the date range.
        """
        entries_on_range = []

        for entry in self.entries:
            if start_date <= entry.watched_date <= end_date:
                entries_on_range.append(entry)

        return entries_on_range
    
    def search_year(self, year: int) -> List["Film"]:
        """
        Searches for entries with films of a specific year.

        Args:
            year (int): The year to search for.

        Returns:
            List[Entry]: Entries with films released on the given year.
        """
        entries_of_year = []

        for entry in self.entries:
            if entry.film.year == year:
                entries_of_year.append(entry)

        return entries_of_year
    
    def search_decade(self, decade: str) -> List[Entry]:
        """
        Searches for entries with films of a specific decade.

        Args:
            decade (str): The decade to search for.
    
        Returns:
            List[Entry]: Entries with films released on the given decade.
        """
        entries_of_decade = []

        for entry in self.entries:
            film_decade = f"{(entry.film.year // 10) * 10}s" if entry.film.year else None
            if film_decade == decade:
                entries_of_decade.append(entry)

        return entries_of_decade
    
    def search_rating(self, rating: float) -> List[Entry]:
        """
        Searches for entries with a specific rating.

        Args:
            rating (float): The rating to search for.

        Returns:
            List[Entry]: Entries with the given rating.
        """
        entries_with_rating = []

        for entry in self.entries:
            if entry.rating == rating:
                entries_with_rating.append(entry)

        return entries_with_rating
    
    def search_director(self, director: str) -> List[Entry]:
        """
        Searches for entries with a specific director.

        Args:
            director (str): The director to search for.

        Returns:
            List[Entry]: Entries with the given director.
        """
        entries_with_director = []

        for entry in self.entries:
            if director in entry.film.director :
                entries_with_director.append(entry)

        return entries_with_director
    
    def search_actor(self, actor: str) -> List[Entry]:
        """
        Searches for entries with a specific actor.

        Args:
            actor (str): The actor to search for.

        Returns:
            List[Entry]: Entries with the given actor.
        """
        entries_with_actor = []

        for entry in self.entries:
            if actor in entry.film.actors :
                entries_with_actor.append(entry)

        return entries_with_actor
    
    def search_country(self, country: str) -> List["Film"]:
        """
        Searches for entries with films of a specific country.

        Args:
            country (str): The country to search for.

        Returns:
            List[Entry]: Entries with a film of the given country.
        """
        country_entries = []

        for entry in self.entry:
            if country in entry.film.country:
                country_entries.append(entry)

        return country_entries
    
    def search_language(self, language: str) -> List[Entry]:
        """
        Searches for entries where a specific language is spoken on the film.

        Args:
            language (str): The language to search for.

        Returns:
            List[Entry]: Entries where the given language is spoken on the film.
        """
        entries_with_language = []

        for entry in self.entries:
            if language in entry.film.language:
                entries_with_language.append(entry)

        return entries_with_language