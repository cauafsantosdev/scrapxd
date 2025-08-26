"""
This module defines the Pydantic model for a single film from Letterboxd.

The Film class is designed to be instantiated with just a film's `slug`
and will lazily fetch and parse all other details from the Letterboxd website
upon first access, caching the results for efficiency.
"""

import re
import json
import logging
from functools import cached_property
from bs4 import BeautifulSoup
from pydantic import BaseModel, computed_field
from typing import List, Dict, Optional, Any, Literal, Union
from scrapxd.fetcher import Fetcher, fetcher as default_fetcher

# Get a logger instance for this module
log = logging.getLogger(__name__)

class Film(BaseModel):
    """
    Represents a single film on Letterboxd, with lazy-loaded attributes.

    This class is the core data model for a film. Upon initialization with a `slug`,
    it can retrieve all other film details (e.g., title, year, cast, genres) by
    scraping the corresponding Letterboxd page.

    Attributes are exposed as properties that fetch data on first access and then
    cache the result for subsequent calls, ensuring that network requests are
    minimized.

    Attributes:
        slug (str): The unique identifier for the film in Letterboxd URLs
                    (e.g., "barbie" for the film "Barbie").
    """
    slug: str
    fetcher: Fetcher = default_fetcher

    _soup: Optional[BeautifulSoup] = None
    _nano_soup: Optional[BeautifulSoup] = None

    class Config:
        extra = 'allow'

    def __str__(self):
        """Provides an informal, human-readable string representation of the film."""
        return f"{self.title} ({self.year})"
    
    def __repr__(self):
        """
        Provides an official, unambiguous string representation of the film,
        including title and year if they have already been computed and cached.
        """
        parts = [f"slug='{self.slug}'"]

        # Adds extra info ONLY if it's in cache.
        if 'title' in self.__dict__:
            parts.append(f"title='{self.title}'")
        
        if 'year' in self.__dict__:
            parts.append(f"year={self.year}")

        return f"Film({', '.join(parts)})"
    
    def _get_soup(self) -> BeautifulSoup:
        """
        Fetches the main film page's HTML and caches it as a BeautifulSoup object.

        This method ensures the main page is downloaded only once per Film instance.
        Subsequent calls will return the cached object instantly.

        Returns:
            BeautifulSoup: The parsed HTML of the main film page.
        """
        # Log network activity at DEBUG level
        if self._soup is None:
            log.debug(f"Requesting main page for slug: '{self.slug}'")
            self._soup = self.fetcher.fetch_film(self.slug)
            log.debug(f"Soup for {self.slug}'s main page has been fetched and cached.")

        return self._soup
    
    def _get_nano_soup(self) -> BeautifulSoup:
        """
        Fetches the film's "nanogenres" page HTML and caches it.

        This method ensures the nanogenres page is downloaded only once per instance.

        Returns:
            BeautifulSoup: The parsed HTML of the nanogenres page.
        """
        if self._nano_soup is None:
            log.debug(f"Requesting nanogenres page for slug: '{self.slug}'")
            self._nano_soup = self.fetcher.fetch_nanogenres(self.slug)
            log.debug(f"Soup for {self.slug}'s nanogenres page has been fetched and cached.")
        
        return self._nano_soup
        
    @computed_field
    @cached_property
    def id(self) -> int:
        """The TMDb (The Movie Database) ID of the film."""
        return self._parse_id()
    
    @computed_field
    @cached_property
    def title(self) -> str:
        """The title of the film."""
        return self._parse_title()
    
    @computed_field
    @cached_property
    def year(self) -> int:
        """The release year of the film."""
        return self._parse_year()
    
    @computed_field
    @cached_property
    def runtime(self) -> int:
        """The runtime of the film in minutes."""
        return self._parse_runtime()
    
    @computed_field
    @cached_property
    def director(self) -> List[str]:
        """A list of the film's directors."""
        return self._parse_director()

    @computed_field
    @cached_property
    def genre(self) -> List[str]:
        """A list of the film's genres."""
        return self._parse_genre()

    @computed_field
    @cached_property
    def nanogenres(self) -> List[str] | None:
        """A list of the film's specific nanogenres, if available."""
        return self._parse_nanogenres()

    @computed_field
    @cached_property
    def themes(self) -> List[str] | None:
        """A list of the film's themes, if available."""
        return self._parse_themes()

    @computed_field
    @cached_property
    def country(self) -> List[str]:
        """A list of the film's countries of origin."""
        return self._parse_tab_details("Country")
    
    @computed_field
    @cached_property
    def language(self) -> List[str]:
        """A list of the film's spoken languages."""
        return self._parse_tab_details("Language")
    
    @computed_field
    @cached_property
    def studio(self) -> List[str]:
        """A list of the film's production studios."""
        return self._parse_tab_details("Studio")

    @computed_field
    @cached_property
    def cast(self) -> Dict[str, str]:
        """A dictionary mapping actor names to their character roles."""
        return self._parse_cast()
    
    @computed_field
    @cached_property
    def actors(self) -> List[str]:
        """A list of actor names, derived from the main cast data."""
        return list(self.cast.keys())
    
    @computed_field
    @cached_property
    def characters(self) -> List[str]:
        """A list of character names, derived from the main cast data."""
        return list(self.cast.values())

    @computed_field
    @cached_property
    def crew(self) -> Dict[str, str | List[str]]:
        """A dictionary mapping crew roles to the person(s) who filled them."""
        return self._parse_crew()

    @computed_field
    @cached_property
    def avg_rating(self) -> float:
        """The average Letterboxd rating for the film."""
        return self._parse_avg_rating()

    @computed_field
    @cached_property
    def total_logs(self) -> int:
        """The total number of times the film has been logged by Letterboxd users."""
        return self._parse_total_logs()
    
    def _script_to_json(self) -> Dict[str, Any]:
        """Extracts and cleans the JSON-LD data block from the film page."""
        try:
            script = self._get_soup().find("script", type="application/ld+json")
            raw_json = script.string
            # Clean up the JSON string by removing CDATA comments.
            cleaned_json = raw_json.strip().replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
            return json.loads(cleaned_json)

        except (AttributeError, json.JSONDecodeError):
            log.warning(f"Could not find or parse JSON-LD script for slug '{self.slug}'.")
            return {}

    def _parse_tab_details(self, type: Literal["Studio", "Country", "Language"]) -> List[str]:
        """
        Parses content from the "Details" tab, handling various page layouts.
        """
        try:
            content = self._get_soup().find("div", id="tab-details")
            detail_paragraphs = content.find_all("p")

            # Checks if there's only one item for specified type
            check = content.find("span", string=f"{type}")

            # Types always appear in the same order on "Details" tab
            type_idx = {"Studio": 0, "Country": 1, "Language": 2}
            idx = type_idx[type]

            # Handles special case of multiple languages,
            # where one is Primary and the others are Spoken
            if type == "Language" and not check:
                primary = str(detail_paragraphs[idx].find("a").string)
                details = [primary]

                links = detail_paragraphs[idx+1].find_all("a")
                details += [str(detail.string) for detail in links if str(detail.string) != primary]
                return details

            # Multiple items
            elif not check:
                links = detail_paragraphs[idx].find_all("a")
                return [str(detail.string).strip() for detail in links]
            
            # One item
            else:
                link = detail_paragraphs[idx].find("a")

            return [str(link.string).strip()]
        
        except (AttributeError, TypeError, IndexError):
            log.warning(f"Could not parse '{type}' from details tab for slug '{self.slug}'.")
            return []
        
    def _parse_actor_links(self) -> List:
        """Finds and returns all actor link elements from the cast list."""
        try:
            content = self._get_soup().find("div", class_="cast-list text-sluglist")
            return content.find_all("a", class_="text-slug tooltip")
        
        except AttributeError:
            log.warning(f"Could not find cast list div for slug '{self.slug}'.")
            return []

    def _parse_id(self) -> Optional[int]:
        """Parses the TMDb ID from a link on the page."""
        try:
            content = self._get_soup().find("a", class_="micro-button track-event", href=re.compile(r'^https://www\.themoviedb\.org/movie/'))
            id_link = content.get("href")

            return int(id_link.replace("https://www.themoviedb.org/movie/", "").replace("/", ""))
        
        except (AttributeError, TypeError, ValueError):
            log.warning(f"Could not parse TMDb ID for slug '{self.slug}'.")
            return None

    def _parse_title(self) -> Optional[str]:
        """Parses the film's main title."""
        try:
            title_span = self._get_soup().find("span", class_="name js-widont prettify")
            return str(title_span.string)
        
        except AttributeError:
            log.warning(f"Could not parse title for slug '{self.slug}'.")
            return None

    def _parse_director(self) -> List[str]:
        """Parses the director(s)."""
        directors_list = []

        try:
            content = self._get_soup().find_all("a", class_="contributor")

            for director in content:
                name = director.find("span", class_="prettify")
                directors_list.append(str(name.string))

            return directors_list
        
        except AttributeError:
            log.warning(f"Could not parse directors for slug '{self.slug}'.")
            return directors_list

    def _parse_year(self) -> Optional[int]:
        """Parses the release year."""
        try:
            content = self._get_soup().find("span", class_="releasedate")
            year = content.find("a")

            return int(year.string)
        
        except (AttributeError, TypeError, ValueError):
            log.warning(f"Could not parse year for slug '{self.slug}'.")
            return None

    def _parse_runtime(self) -> Optional[int]:
        """Parses the runtime in minutes."""
        try:
            content = self._get_soup().find("p", class_="text-link text-footer")
            raw_text = str(content.text).strip()
            runtime = ""
            
            # Loop through the text to extract the initial digits.
            for c in raw_text:
                if c.isdigit() == False:
                    break
                else:
                    runtime += c

            return int(runtime)
        
        except (AttributeError, ValueError):
            log.warning(f"Could not parse runtime for slug '{self.slug}'.")
            return None

    def _parse_cast(self) -> Dict[str, str]:
        """Parses the film's cast list, mapping actor names to their character roles."""
        cast = {}
        try:
            actor_links = self._parse_actor_links()

            for actor in actor_links:
                name = str(actor.string)
                character = actor.get("title")

                cast[name] = character.replace(" (uncredited)", "") if character else "(Unnamed)"

            return cast
        
        except AttributeError:
            log.warning(f"Could not parse cast for slug '{self.slug}'.")
            return cast

    def _parse_crew(self) -> Dict[str, Union[str, List[str]]]:
        """Parses the film's crew from the "Crew" tab."""
        crew = {}
        try:
            content = self._get_soup().find("div", id="tab-crew")
            roles = content.find_all("span", class_="crewrole -full")
            crew_paragraphs = content.find_all("p")

            for i, role in enumerate(roles):
                role_name = str(role.string)
                person_links = crew_paragraphs[i].find_all("a")

                persons = [str(person.string) for person in person_links]

                crew[role_name] = persons[0] if len(persons) == 1 else persons

            return crew
        
        except (AttributeError, IndexError):
            log.warning(f"Could not parse crew for slug '{self.slug}'.")
            return crew

    def _parse_genre(self) -> List[str]:
        """Parses the genres from the "Genres" tab."""
        try:
            content = self._get_soup().find("div", id="tab-genres")
            content_paragraphs = content.find_all("p")

            # Checks if there's only one genre for the film
            check = content.find("span", string="Genre")

            if not check:
                genre_links = content_paragraphs[0].find_all("a")
                return [str(genre.string) for genre in genre_links]
            
            else:
                genre_link = content_paragraphs[0].find("a")
                return [str(genre_link.string)]
            
        except (AttributeError, IndexError):
            log.warning(f"Could not parse genres for slug '{self.slug}'.")
            return []

    def _parse_themes(self) -> Optional[List[str]]:
        """Parses the themes from the "Genres" tab, if they exist."""
        try:
            content = self._get_soup().find("div", id="tab-genres")
            content_paragraphs = content.find_all("p")

            single_check = content.find("span", string="Theme")
            multi_check = content.find("span", string="Themes")

            if multi_check:
                theme_links = content_paragraphs[1].find_all("a")
                return [str(theme.string) for theme in theme_links if str(theme.string) != "Show All…"]
            
            elif single_check:
                theme_link = content_paragraphs[1].find("a")
                return [str(theme_link.string)]
            
            else:
                return None
        except (AttributeError, IndexError):
             log.warning(f"Could not parse themes for slug '{self.slug}'.")
             return None

    def _parse_nanogenres(self) -> Optional[List[str]]:
        """Parses nanogenres from their dedicated page, if they exist."""
        try:
            content = self._get_nano_soup().find_all("section", class_="section genre-group")

            if not content:
                return None
            
            return [str(nano.find("span", class_="label").string) for nano in content]

        except AttributeError:
            log.warning(f"Could not parse nanogenres for slug '{self.slug}'.")
            return None

    def _parse_avg_rating(self) -> Optional[float]:
        """Parses the average rating from the JSON-LD data block."""
        try:
            data = self._script_to_json()
            return float(data["aggregateRating"]['ratingValue'])
        
        except (KeyError, TypeError):
            log.warning(f"Could not parse average rating for slug '{self.slug}'. JSON-LD script may be missing or malformed.")
            return None

    def _parse_total_logs(self) -> Optional[int]:
        """Parses the total number of logs from the JSON-LD data block."""
        try:
            data = self._script_to_json()
            return int(data["aggregateRating"]['ratingCount'])
        
        except (KeyError, TypeError):
            log.warning(f"Could not parse total logs for slug '{self.slug}'. JSON-LD script may be missing or malformed.")
            return None