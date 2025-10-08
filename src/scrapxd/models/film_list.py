"""
Defines the FilmList model, representing a list of films scraped from Letterboxd.

Includes metadata, analytics, export functionality and search utilities. The films 
attribute supports both list and dict representations, depending on the scraping context.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Union

from .film import Film
from ..analytics import FilmAnalytics
from ..export import DataExport


class FilmList(BaseModel, FilmAnalytics, DataExport):
    """
    Represents a list of films scraped from Letterboxd, including metadata and analytics.
    The films attribute may be a list or a dict, depending on the scraping context.
    """
    username: str
    title: str
    number_of_films: int
    films: Union[List[Film], Dict[int, Film]]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        """Provides an informal, human-readable string representation of the film list."""
        return f"{self.title} ({self.number_of_films} films)"

    def __repr__(self):
        """Provides a formal string representation of the FilmList object for debugging."""
        return (
            f"FilmList(title='{self.title}', username='{self.username}', "
            f"number_of_films={self.number_of_films})"
        )
    
    @property
    def films_list(self) -> List[Film]:
        """
        Returns the films as a list, regardless of the internal representation.
        """
        if isinstance(self.films, dict):
            return list(self.films.values())
        return self.films
    
    def search_film(self, film: Union[str, Film]) -> Optional[Film]:
        """
        Searches for films matching a given film (by slug or Film object).

        Args:
            film (str or Film): The film slug or Film object to search for.

        Returns:
            Optional[Film]: The film, if available.
        """                
        if isinstance(film, Film):
            film = film.slug

        for film in self.films_list:
            if film.slug == film:
                return film
            
        return None
    
    def search_year(self, year: int) -> List[Film]:
        """
        Searches for films released on a specific year.

        Args:
            year (int): The year to search for.

        Returns:
            List[Film]: Films released on the given year.
        """
        films_on_year = []

        for film in self.films_list:
            if film.year == year:
                films_on_year.append(film)

        return films_on_year
    
    def search_decade(self, decade: str) -> List[Film]:
        """
        Searches for films released on a specific decade.

        Args:
            decade (str): The decade to search for.
    
        Returns:
            List[Film]: Film released on the given decade.
        """
        films_on_decade = []

        for film in self.films_list:
            film_decade = f"{(film.year // 10) * 10}s" if film.year else None
            if film_decade == decade:
                films_on_decade.append(film)

        return films_on_decade
    
    def search_avg_rating(self, rating: float) -> List[Film]:
        """
        Searches for films with a minimum avg rating.

        Args:
            rating (float): The minimum rating to search for.

        Returns:
            List[Film]: Film withing rating range.
        """
        films_in_rating_range = []

        for film in self.films_list:
            if film.avg_rating >= rating:
                films_in_rating_range.append(film)

        return films_in_rating_range
    
    def search_director(self, director: str) -> List[Film]:
        """
        Searches for film with a specific director.

        Args:
            director (str): The director to search for.

        Returns:
            List[Film]: Films with the given director.
        """
        films_with_director = []

        for film in self.films:
            if director in film.director:
                films_with_director.append(film)

        return films_with_director
    
    def search_actor(self, actor: str) -> List[Film]:
        """
        Searches for films with a specific actor.

        Args:
            actor (str): The actor to search for.

        Returns:
            List[Film]: Films with the given actor.
        """
        films_with_actor = []

        for film in self.films_list:
            if actor in film.actors:
                films_with_actor.append(film)

        return films_with_actor
    
    def search_country(self, country: str) -> List[Film]:
        """
        Searches for films of a specific country.

        Args:
            country (str): The country to search for.

        Returns:
            List[Film]: Films of the given country.
        """
        country_films = []

        for film in self.films_list:
            if country in film.country:
                country_films.append(film)

        return country_films
    
    def search_language(self, language: str) -> List[Film]:
        """
        Searches for films where a specific language is spoken.

        Args:
            language (str): The language to search for.

        Returns:
            List[Film]: Films where the given language is spoken.
        """
        films_with_language = []

        for film in self.films_list:
            if language in film.language:
                films_with_language.append(film)

        return films_with_language