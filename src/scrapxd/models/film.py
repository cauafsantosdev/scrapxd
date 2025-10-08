"""
This module defines the Pydantic model for a single film from Letterboxd.

The Film class is designed to be instantiated with just a film's `slug`
and will lazily fetch and parse all other details from the Letterboxd website
upon first access, caching the results for efficiency.
"""
import re
import json
import logging
from math import floor
from datetime import date
from functools import cached_property
from pydantic import computed_field, ConfigDict
from typing import List, Dict, Optional, Any, Literal

from .base import ScraperBase


# Get a logger instance for this module
log = logging.getLogger(__name__)

class Film(ScraperBase):
    """
    Represents a single film on Letterboxd, with lazy-loaded attributes.

    This class is the core data model for a film. Upon initialization with a `slug`,
    it can retrieve all other film details (e.g., title, year, cast, genres) by
    scraping the corresponding Letterboxd page.

    Attributes are exposed as properties that fetch data on first access and then
    cache the result for subsequent calls, ensuring that network requests are
    minimized.

    Attributes:
        slug (str): The unique identifier for the film in Letterboxd URLs.
        id (int): The TMDb (The Movie Database) ID of the film.
        poster (str): The URL of the film poster.
        synopsis (str): The synopsis of the film.
        tagline (Optional[str]): The tagline of the film.
        title (str): The title of the film.
        original_title (Optional[str]): The original non-English title of the film.
        alternative_titles (Optional[List[str]]): Alternative titles in various languages.
        year (int): The release year of the film.
        runtime (int): The runtime of the film in minutes.
        director (List[str]): List of the film's directors.
        genre (List[str]): List of the film's genres.
        nanogenres (List[str]): List of the film's specific nanogenres, if available.
        themes (List[str]): List of the film's themes, if available.
        country (List[str]): List of the film's countries of origin.
        language (List[str]): List of the film's spoken languages.
        studio (List[str]): List of the film's production studios.
        cast (Dict[str, str]): Dictionary mapping actor names to their character roles.
        actors (List[str]): List of actor names.
        characters (List[str]): List of character names.
        crew (Dict[str, str | List[str]]): Dictionary mapping crew roles to the person(s) who filled them.
        avg_rating (float): The average Letterboxd rating for the film.
        total_logs (int): The total number of times the film has been logged by Letterboxd users.
    """
    slug: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    
    def __eq__(self, other):
        """
        Determines if two Film objects are equal by comparing their slugs.
        
        Args:
            other (Film): Another Film object.

        Returns:
            bool: True if slugs match, False otherwise.
        """
        if isinstance(other, Film):
            return self.slug == other.slug
        return NotImplemented

    def __hash__(self):
        """
        Provides a hash for the Film object, based on its unique slug.
        
        Returns:
            int: Hash of the slug.
        """
        return hash(self.slug)

    @computed_field
    @cached_property
    def id(self) -> int:
        """
        Returns the TMDb (The Movie Database) ID of the film.

        Returns:
            int: The TMDb ID.
        """
        return self._parse_id()
    
    @computed_field
    @cached_property
    def poster(self) -> str:
        """
        Returns the URL of the film poster.

        Returns:
            str: The poster image URL.
        """
        return self._parse_poster()
    
    @computed_field
    @cached_property
    def synopsis(self) -> str:
        """
        Returns the synopsis of the film.

        Returns:
            str: The film synopsis.
        """
        return self._parse_synopsis()
    
    @computed_field
    @cached_property
    def tagline(self) -> Optional[str]:
        """
        Returns the tagline of the film.

        Returns:
            Optional[str]: The film tagline, or None if not available.
        """
        return self._parse_tagline()
    
    @computed_field
    @cached_property
    def title(self) -> str:
        """
        Returns the title of the film.

        Returns:
            str: The film title.
        """
        return self._parse_title()
    
    @computed_field
    @cached_property
    def original_title(self) -> Optional[str]:
        """
        Returns the original non-English title of the film.

        Returns:
            Optional[str]: The original title, or None if not available.
        """
        return self._parse_original_title()
    
    @computed_field
    @cached_property
    def alternative_titles(self) -> Optional[List[str]]:
        """
        Returns the alternative titles of the film in various languages.

        Returns:
            Optional[List[str]]: List of alternative titles, or None if not available.
        """
        return self._parse_alternative_titles()
    
    @computed_field
    @cached_property
    def year(self) -> int:
        """
        Returns the release year of the film.

        Returns:
            int: The release year.
        """
        return self._parse_year()
    
    @computed_field
    @cached_property
    def runtime(self) -> int:
        """
        Returns the runtime of the film in minutes.

        Returns:
            int: The runtime in minutes.
        """
        return self._parse_runtime()
    
    @computed_field
    @cached_property
    def director(self) -> List[str]:
        """
        Returns a list of the film's directors.

        Returns:
            List[str]: Directors of the film.
        """
        return self._parse_director()

    @computed_field
    @cached_property
    def genre(self) -> List[str]:
        """
        Returns a list of the film's genres.

        Returns:
            List[str]: Genres of the film.
        """
        return self._parse_genre()

    @computed_field
    @cached_property
    def nanogenres(self) -> List[str]:
        """
        Returns a list of the film's specific nanogenres, if available.

        Returns:
            List[str]: Nanogenres of the film.
        """
        return self._parse_nanogenres()

    @computed_field
    @cached_property
    def themes(self) -> List[str]:
        """
        Returns a list of the film's themes, if available.

        Returns:
            List[str]: Themes of the film.
        """
        return self._parse_themes()

    @computed_field
    @cached_property
    def country(self) -> List[str]:
        """
        Returns a list of the film's countries of origin.

        Returns:
            List[str]: Countries of origin.
        """
        return self._parse_tab_details("Country")
    
    @computed_field
    @cached_property
    def language(self) -> List[str]:
        """
        Returns a list of the film's spoken languages.

        Returns:
            List[str]: Spoken languages.
        """
        return self._parse_tab_details("Language")
    
    @computed_field
    @cached_property
    def studio(self) -> List[str]:
        """
        Returns a list of the film's production studios.

        Returns:
            List[str]: Production studios.
        """
        return self._parse_tab_details("Studio")

    @computed_field
    @cached_property
    def cast(self) -> Dict[str, str]:
        """
        Returns a dictionary mapping actor names to their character roles.

        Returns:
            Dict[str, str]: Mapping of actor names to character roles.
        """
        return self._parse_cast()
    
    @computed_field
    @cached_property
    def actors(self) -> List[str]:
        """
        Returns a list of actor names, derived from the main cast data.

        Returns:
            List[str]: Actor names.
        """
        return list(self.cast.keys())
    
    @computed_field
    @cached_property
    def characters(self) -> List[str]:
        """
        Returns a list of character names, derived from the main cast data.

        Returns:
            List[str]: Character names.
        """
        return list(self.cast.values())

    @computed_field
    @cached_property
    def crew(self) -> Dict[str, str | List[str]]:
        """
        Returns a dictionary mapping crew roles to the person(s) who filled them.

        Returns:
            Dict[str, str | List[str]]: Mapping of crew roles to people.
        """
        return self._parse_crew()

    @computed_field
    @cached_property
    def avg_rating(self) -> float:
        """
        Returns the average Letterboxd rating for the film.

        Returns:
            float: The average rating.
        """
        return self._parse_avg_rating()

    @computed_field
    @cached_property
    def total_logs(self) -> int:
        """
        Returns the total number of times the film has been logged by Letterboxd users.

        Returns:
            int: The total log count.
        """
        return self._parse_total_logs()

    def _parse_id(self) -> Optional[int]:
        """
        Parses the TMDb (The Movie Database) ID from the film's Letterboxd page.

        Returns:
            Optional[int]: The TMDb ID, or None if not found or parsing fails.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            tmdb_anchor = self._safe_find(soup, "a", class_="micro-button track-event", href=re.compile(r'^https://www\.themoviedb\.org/movie/'))
            id_url = tmdb_anchor.get("href")

            return int(id_url.replace("https://www.themoviedb.org/movie/", "").replace("/", ""))
        
        except (AttributeError, TypeError, ValueError):
            log.warning(f"Could not parse TMDb ID for slug '{self.slug}'.")
            return None
        
    def _parse_poster(self) -> Optional[str]:
        """
        Parses the film poster URL from the film's Letterboxd page.

        Returns:
            Optional[str]: The poster image URL, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            poster_div = self._safe_find(soup, "div", class_="poster film-poster")
            poster_img = self._safe_find(poster_div, "img")

            return poster_img.get("src")
        
        except AttributeError:
            log.warning(f"Could not parse poster for slug '{self.slug}'.")
            return None

    def _parse_synopsis(self) -> Optional[str]:
        """
        Parses the film synopsis from the film's Letterboxd page.

        Returns:
            Optional[str]: The film synopsis, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            synopsis_div = self._safe_find(soup, "div", class_="truncate")
            synopsis = self._safe_find(synopsis_div, "p")

            return str(synopsis.string).strip().replace('\n', '')
        
        except AttributeError:
            log.warning(f"Could not parse synopsis for slug '{self.slug}'.")
            return None

    def _parse_tagline(self) -> Optional[str]:
        """
        Parses the film's tagline from the film's Letterboxd page.

        Returns:
            Optional[str]: The film tagline, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            tagline_h4 = self._safe_find(soup, "h4", class_="tagline")

            return str(tagline_h4.string).strip().replace('\xa0', ' ')
        
        except AttributeError:
            log.warning(f"Could not parse tagline for slug '{self.slug}'.")
            return None    

    def _parse_title(self) -> Optional[str]:
        """
        Parses the film's main title from the film's Letterboxd page.

        Returns:
            Optional[str]: The film title, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            title_span = self._safe_find(soup, "span", class_="name js-widont prettify")
            return str(title_span.string).strip().replace('\xa0', ' ')
        
        except AttributeError:
            log.warning(f"Could not parse title for slug '{self.slug}'.")
            return None
        
    def _parse_original_title(self) -> Optional[str]:
        """
        Parses the film's original non-English title from the film's Letterboxd page.

        Returns:
            Optional[str]: The original title, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            title_span = self._safe_find(soup, "h2", class_="originalname")
            return str(title_span.string).strip().replace('\xa0', ' ')
        
        except AttributeError:
            log.warning(f"Could not parse original title for slug '{self.slug}'.")
            if self.title:
                return self.title
            return None
        
    def _parse_alternative_titles(self) -> Optional[List[str]]:
        """
        Parses the film's alternative titles in various languages from the film's Letterboxd page.

        Returns:
            Optional[List[str]]: List of alternative titles, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            list_div = self._safe_find(soup, "div", class_="text-indentedlist")
            titles_p = self._safe_find(list_div, "p")
            return [str(titles_p.string)]
        
        except AttributeError:
            log.warning(f"Could not parse alternative titles for slug '{self.slug}'.")
            return None

    def _parse_year(self) -> Optional[int]:
        """
        Parses the film's release year from the film's Letterboxd page.

        Returns:
            Optional[int]: The release year, or None if not found or parsing fails.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            date_span = self._safe_find(soup, "span", class_="releasedate")
            year = self._safe_find(date_span, "a")

            return int(year.string)
        
        except (AttributeError, TypeError, ValueError):
            log.warning(f"Could not parse year for slug '{self.slug}'.")
            return None

    def _parse_runtime(self) -> Optional[int]:
        """
        Parses the film's runtime in minutes from the film's Letterboxd page.

        Returns:
            Optional[int]: The runtime in minutes, or None if not found or parsing fails.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            footer_p = self._safe_find(soup, "p", class_="text-link text-footer")
            raw_text = str(footer_p.text).strip()
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
        
    def _parse_director(self) -> List[str]:
        """
        Parses the director(s) of the film from the film's Letterboxd page.

        Returns:
            List[str]: List of director names (may be empty if not found).
        """
        directors_list = []

        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            contributor_anchors = self._safe_find_all(soup, "a", class_="contributor")

            for director in contributor_anchors:
                name = self._safe_find(director, "span", class_="prettify")
                directors_list.append(str(name.string))

            return directors_list
        
        except AttributeError:
            log.warning(f"Could not parse directors for slug '{self.slug}'.")
            return directors_list

    def _parse_genre(self) -> List[str]:
        """
        Parses the genres of the film from the "Genres" tab on the film's Letterboxd page.

        Returns:
            List[str]: List of genre names (may be empty if not found).
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            genres_tab = self._safe_find(soup, "div", id="tab-genres")
            tab_paragraphs = self._safe_find_all(genres_tab, "p")

            # Checks if there's only one genre for the film
            is_unique = genres_tab.find("span", string="Genre")

            if not is_unique:
                genre_anchors = self._safe_find_all(tab_paragraphs[0], "a")
                return [str(genre.string) for genre in genre_anchors]
            
            else:
                genre_anchor = self._safe_find(tab_paragraphs[0], "a")
                return [str(genre_anchor.string)]
            
        except (AttributeError, IndexError):
            log.warning(f"Could not parse genres for slug '{self.slug}'.")
            return []
        
    def _parse_nanogenres(self) -> Optional[List[str]]:
        """
        Parses the nanogenres of the film from their dedicated page, if available.

        Returns:
            Optional[List[str]]: List of nanogenres, or None if not found.
        """
        try:
            nano_soup = self._get_soup(self.fetcher.fetch_nanogenres, self.slug)
            nano_section = self._safe_find_all(nano_soup, "section", class_="section genre-group")

            if not nano_section:
                return None
            
            return [str(nano.find("span", class_="label").string) for nano in nano_section]

        except AttributeError:
            log.warning(f"Could not parse nanogenres for slug '{self.slug}'.")
            return None
        
    def _parse_themes(self) -> Optional[List[str]]:
        """
        Parses the themes of the film from the "Genres" tab, if available.

        Returns:
            Optional[List[str]]: List of themes, or None if not found.
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            genres_tab = self._safe_find(soup, "div", id="tab-genres")
            tab_paragraphs = self._safe_find_all(genres_tab, "p")

            is_unique = genres_tab.find("span", string="Theme")
            is_multiple = genres_tab.find("span", string="Themes")

            if is_multiple:
                theme_anchors = self._safe_find_all(tab_paragraphs[1], "a")
                return [str(theme.string) for theme in theme_anchors if str(theme.string) != "Show All…"]
            
            elif is_unique:
                theme_anchor = self._safe_find(tab_paragraphs[1], "a")
                return [str(theme_anchor.string)]
            
            else:
                return None
            
        except (AttributeError, IndexError):
             log.warning(f"Could not parse themes for slug '{self.slug}'.")
             return None
        
    def _parse_tab_details(self, type: Literal["Studio", "Country", "Language"]) -> List[str]:
        """
        Parses details (studio, country, or language) from the "Details" tab on the film's Letterboxd page.

        Args:
            type (Literal["Studio", "Country", "Language"]): The detail type to parse.

        Returns:
            List[str]: List of detail values (may be empty if not found).
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            tab_details = self._safe_find(soup, "div", id="tab-details")
            detail_paragraphs = self._safe_find_all(tab_details, "p")

            # Checks if there's only one item for specified type
            is_unique = tab_details.find("span", string=type)

            # Types always appear in the same order on "Details" tab
            type_idx = {"Studio": 0, "Country": 1, "Language": 2}
            idx = type_idx[type]

            # Handles special case of multiple languages,
            # where one is Primary and the others are Spoken
            if type == "Language" and not is_unique:
                primary = str(self._safe_find(detail_paragraphs[idx], "a").string)
                details = [primary]

                spoken = self._safe_find_all(detail_paragraphs[idx+1], "a")
                details += [str(detail.string) for detail in spoken if str(detail.string) != primary]
                return details

            # Multiple items
            elif not is_unique:
                anchors = self._safe_find_all(detail_paragraphs[idx], "a")
                return [str(detail.string).strip() for detail in anchors]
            
            # One item
            else:
                detail_anchor = self._safe_find(detail_paragraphs[idx], "a")

            return [str(detail_anchor.string).strip()]
        
        except (AttributeError, TypeError, IndexError):
            log.warning(f"Could not parse '{type}' from details tab for slug '{self.slug}'.")
            return []
        
    def _parse_actor_anchors(self) -> List:
        """
        Finds and returns all actor link elements from the cast list on the film's Letterboxd page.

        Returns:
            List: List of BeautifulSoup anchor elements for actors (may be empty if not found).
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            cast_list = self._safe_find(soup, "div", class_="cast-list text-sluglist")
            return self._safe_find_all(cast_list, "a", class_="text-slug tooltip")
        
        except AttributeError:
            log.warning(f"Could not find cast list div for slug '{self.slug}'.")
            return []
        
    def _parse_cast(self) -> Dict[str, str]:
        """
        Parses the film's cast list, mapping actor names to their character roles.

        Returns:
            Dict[str, str]: Mapping of actor names to character roles (may be empty if not found).
        """
        cast = {}
        try:
            actor_anchors = self._parse_actor_anchors()

            for actor in actor_anchors:
                name = str(actor.string)
                character = actor.get("data-original-title")

                cast[name] = character.replace(" (uncredited)", "") if character else "(Unnamed)"

            return cast
        
        except AttributeError:
            log.warning(f"Could not parse cast for slug '{self.slug}'.")
            return cast

    def _parse_crew(self) -> Dict[str, List[str]]:
        """
        Parses the film's crew from the "Crew" tab on the film's Letterboxd page.

        Returns:
            Dict[str, List[str]]: Mapping of crew roles to lists of people (may be empty if not found).
        """
        crew = {}
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            crew_tab = self._safe_find(soup, "div", id="tab-crew")
            role_span = self._safe_find_all(crew_tab, "span", class_="crewrole -full")
            crew_paragraphs = self._safe_find_all(crew_tab, "p")

            for i, role in enumerate(role_span):
                role_name = str(role.string)
                person_anchors = self._safe_find_all(crew_paragraphs[i], "a")

                persons = [str(person.string) for person in person_anchors]

                crew[role_name] = persons

            return crew
        
        except (AttributeError, IndexError):
            log.warning(f"Could not parse crew for slug '{self.slug}'.")
            return crew
        
    def _script_to_json(self) -> Dict[str, Any]:
        """
        Extracts and cleans the JSON-LD data block from the film's Letterboxd page.

        Returns:
            Dict[str, Any]: Parsed JSON-LD data (may be empty if not found or parsing fails).
        """
        try:
            soup = self._get_soup(self.fetcher.fetch_film, self.slug)
            script = self._safe_find(soup, "script", type="application/ld+json")
            raw_json = script.string
            # Clean up the JSON string by removing CDATA comments.
            cleaned_json = raw_json.strip().replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
            return json.loads(cleaned_json)

        except (AttributeError, json.JSONDecodeError):
            log.warning(f"Could not find or parse JSON-LD script for slug '{self.slug}'.")
            return {}
        
    def _parse_avg_rating(self) -> Optional[float]:
        """
        Parses the average Letterboxd rating for the film from the JSON-LD data block.

        Returns:
            Optional[float]: The average rating, or None if not found or parsing fails.
        """
        try:
            script_data = self._script_to_json()
            return float(script_data["aggregateRating"]['ratingValue'])
        
        except (KeyError, TypeError):
            log.warning(f"Could not parse average rating for slug '{self.slug}'. JSON-LD script may be missing or malformed.")
            return None

    def _parse_total_logs(self) -> Optional[int]:
        """
        Parses the total number of logs for the film from the JSON-LD data block.

        Returns:
            Optional[int]: The total log count, or None if not found or parsing fails.
        """
        try:
            script_data = self._script_to_json()
            return int(script_data["aggregateRating"]['ratingCount'])
        
        except (KeyError, TypeError):
            log.warning(f"Could not parse total logs for slug '{self.slug}'. JSON-LD script may be missing or malformed.")
            return None
        
    def get_popular_reviews(self, limit: int = 5, offset: int = 0) -> List["Entry"]:
        """
        Returns a list of popular reviews for the film.

        Args:
            limit (int): Maximum number of reviews to return.
            offset (int): Starting index for reviews.

        Returns:
            List[Entry]: List of popular Entry objects (reviews) for the film.
        """
        return self._parse_popular_reviews(limit, offset)
    
    def _parse_popular_reviews(self, limit: int = 5, offset: int = 0) -> List["Entry"]:
        """
        Parses popular reviews for the film from its reviews pages.

        Args:
            limit (int): Maximum number of reviews to return.
            offset (int): Starting index for reviews.

        Returns:
            List[Entry]: List of Entry objects representing popular reviews.
        """
        from .entry import Entry

        reviews = []

        start_index = offset
        end_index = offset + limit - 1

        starting_page = floor(start_index / 12) + 1
        ending_page = floor(end_index / 12) + 1

        for page_num in range(starting_page, ending_page + 1):
            soup = self._get_soup(self.fetcher.fetch_film_reviews, self.slug, page_num)

            slice_start = 0
            if page_num == starting_page:
                slice_start = start_index % 12

            slice_end = 12
            if page_num == ending_page:
                slice_end = (end_index % 12) + 1

            review_divs = self._safe_find_all(soup, "div", class_="listitem")

            if review_divs:
                for i in range(slice_start, slice_end):
                    div = review_divs[i]

                    avatar_anchor = self._safe_find(div, "a", class_="avatar -a40")
                    username = avatar_anchor.get("href").replace("/", "")

                    time_attr = self._safe_find(div, "time")
                    date_string = time_attr.get("datetime")
                    review_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

                    film_data = self._safe_find(div, "div", class_="react-component figure")
                    slug = film_data.get("data-item-slug")
                    
                    rating_span = self._safe_find(div, "span", class_=re.compile("^rating -green rated-"))
                    raw_rating = rating_span.get("class")[2]
                    rating = int(raw_rating[6:]) / 2

                    collapsed_text = self._safe_find(div, "div", class_="collapsed-text")

                    if collapsed_text:
                        url_div = self._safe_find(div, "div", class_="body-text -prose -reset js-review-body js-collapsible-text")
                        text_url = url_div.get("data-full-text-url")
                        text_soup = self._get_soup(self.fetcher.fetch_review_text, text_url[1:])
                        paragraphs = self._safe_find_all(text_soup, "p")

                    else:
                        paragraphs = self._safe_find_all(div, "p")

                    text = []
                    for p in paragraphs:
                            text.append(p.get_text(separator=" ", strip=True))

                    text = "".join(text)

                    reviews.append(Entry(username=username,
                                         film=Film(slug=slug),
                                         watched_date=review_date,
                                         rating=rating,
                                         review=text))   
        
        return reviews            