"""
This module provides classes and functions for analyzing film and entry lists,
including statistics, attribute frequency, similarity comparisons, rating analysis,
and discovery timelines. It is designed to support film-related data models and
user logs, offering tools for both descriptive and comparative analytics.
"""
import logging
from datetime import date
from statistics import mean
from pydantic import BaseModel
from functools import cached_property
from collections import Counter, defaultdict
from typing import List, Tuple, Union, Optional, Dict

from .config import DECADES, MONTHS, WEEKDAYS


log = logging.getLogger(__name__)

class ComparisonResults(BaseModel):
    """
    Stores the results of a comparison between two film or entry lists,
    including similarity scores, agreements, common attributes, and statistics.
    """
    film_similarity_score: float = 0.0
    directors_similarity_score: float = 0.0
    genres_similarity_score: float = 0.0
    actors_similarity_score: float = 0.0
    year_similarity_score: float = 0.0
    top_director_agreement: List[Tuple[str, str, bool]] = []
    top_actor_agreement: List[Tuple[str, str, bool]] = []
    top_genre_agreement: List[Tuple[str, str, bool]] = []
    common_films: List = []
    common_directors: List[str] = []
    common_actors: List[str] = []
    common_genres: List[str] = []
    decade_distribution: Dict[str, Union[str, int, Tuple[int, int]]] = {}
    average_year_comparison: Dict[str, Optional[int]] = {}
    average_runtime_comparison: Dict[str, Optional[int]] = {}
    rating_comparison: Dict[str, Union[float, Dict[str, Union[str, float]]]] = {}

class FilmAnalytics:
    """
    Provides analytics and statistics for a list of films, such as top directors,
    genres, average runtime, and similarity comparisons.
    """
    def __init__(self):
        pass

    @cached_property
    def _film_list(self) -> Optional[List["Film"]]:
        """
        A cached property that returns the list of films from the object,
        handling different attribute names.
        """
        try:
            if hasattr(self, 'films') and self.films:
                return list(self.films.values()) if isinstance(self.films, dict) else self.films
            elif hasattr(self, 'entries') and self.entries:
                return [entry.film for entry in self.entries]
        except:
            identifier = getattr(self, 'title', getattr(self, 'username', getattr(self, 'query', 'unknown')))
            log.warning(f"Error accessing film list for {identifier}.")
            return None

    def _get_attr_list(self, film_list: List["Film"], attr: str):
        """
        Extracts a flat list of attribute values from all films in the list.

        Args:
            film_list (List[Film]): List of film objects.
            attr (str): Attribute name to extract.

        Returns:
            List of attribute values.
        """
        attr_list = []
        for film in film_list:
            try:
                attribute_value = getattr(film, attr, None)
                
                if attribute_value is not None:
                    if isinstance(attribute_value, list):
                        attr_list.extend(attribute_value)
                    else:
                        attr_list.append(attribute_value)

            except Exception as e:
                log.warning(f"Error accessing attribute '{attr}' for film '{film.slug}': {e}")
                continue
        
        return attr_list

    def _attribute_counter(self, attr: str) -> List[Tuple[str, int]]:
        """
        Counts the occurrences of items in a specified attribute across a list of films.

        Args:
            attr (str): The name of the film attribute to count (e.g., "director", "genre").
            
        Returns:
            A list of tuples with the item and its count, e.g., [('David Lynch', 5), ...].
        """
        if not self._film_list:
            return []
        
        all_items = self._get_attr_list(self._film_list, attr)
        if not all_items:
            log.warning(f"No items found for attribute '{attr}'.")
            return []

        return Counter(all_items).most_common()

    @cached_property
    def _top_directors(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of directors, sorted by frequency."""
        return self._attribute_counter("director")

    def get_top_directors(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent directors in the film list.

        Args:
            top_n (int, optional): Number of top directors to return.

        Returns:
            List of tuples (director name, count).
        """
        all_directors = self._top_directors
        if top_n and top_n > len(all_directors):
            top_n = len(all_directors)
        return all_directors[:top_n] if top_n else all_directors

    @cached_property
    def _top_actors(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of actors, sorted by frequency."""
        return self._attribute_counter("actors")

    def get_top_actors(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent actors in the film list.

        Args:
            top_n (int, optional): Number of top actors to return.

        Returns:
            List of tuples (actor name, count).
        """
        all_actors = self._top_actors
        if top_n and top_n > len(all_actors):
            top_n = len(all_actors)
        return all_actors[:top_n] if top_n else all_actors

    @cached_property
    def _top_genres(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of genres, sorted by frequency."""
        return self._attribute_counter("genre")

    def get_top_genres(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent genres in the film list.

        Args:
            top_n (int, optional): Number of top genres to return.

        Returns:
            List of tuples (genre name, count).
        """
        all_genres = self._top_genres
        if top_n and top_n > len(all_genres):
            top_n = len(all_genres)
        return all_genres[:top_n] if top_n else all_genres

    @cached_property
    def _top_countries(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of countries, sorted by frequency."""
        return self._attribute_counter("country")

    def get_top_countries(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent countries in the film list.

        Args:
            top_n (int, optional): Number of top countries to return.

        Returns:
            List of tuples (country name, count).
        """
        all_countries = self._top_countries
        if top_n and top_n > len(all_countries):
            top_n = len(all_countries)
        return all_countries[:top_n] if top_n else all_countries

    @cached_property
    def _top_languages(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of languages, sorted by frequency."""
        return self._attribute_counter("language")

    def get_top_languages(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent languages in the film list.

        Args:
            top_n (int, optional): Number of top languages to return.

        Returns:
            List of tuples (language name, count).
        """
        all_languages = self._top_languages
        if top_n and top_n > len(all_languages):
            top_n = len(all_languages)
        return all_languages[:top_n] if top_n else all_languages

    @cached_property
    def _top_decades(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of decades, sorted by frequency."""
        if not self._film_list: 
            return []
        all_decades = [f"{(film.year // 10) * 10}s" for film in self._film_list if film.year]
        return Counter(all_decades).most_common()

    def get_top_decades(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent decades based on film release years.

        Args:
            top_n (int, optional): Number of top decades to return.

        Returns:
            List of tuples (decade, count).
        """
        all_decades = self._top_decades
        if top_n and top_n > len(all_decades):
            top_n = len(all_decades)
        return all_decades[:top_n] if top_n else all_decades

    @cached_property
    def _top_years(self) -> List[Tuple[str, int]]:
        """A cached property for the full list of years, sorted by frequency."""
        return self._attribute_counter("year")

    def get_top_years(self, top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Returns the most frequent years based on film release years.

        Args:
            top_n (int, optional): Number of top years to return.

        Returns:
            List of tuples (year, count).
        """
        all_years = self._top_years
        if top_n and top_n > len(all_years):
            top_n = len(all_years)
        return all_years[:top_n] if top_n else all_years

    @cached_property
    def average_runtime(self) -> float:
        """
        Calculates the average runtime of all films.

        Returns:
            Average runtime as a float, or 0.0 if no runtimes are available.
        """
        if not self._film_list:
            return 0.0

        all_runtimes = [film.runtime for film in self._film_list if film.runtime]
        if not all_runtimes:
            log.warning("No runtimes available to calculate average.")
            return 0.0
        
        return mean(all_runtimes)

    @cached_property
    def shortest_film(self) -> Optional["Film"]:
        """
        Returns the film with the shortest runtime.

        Returns:
            Film object with the shortest runtime, or None if not available.
        """
        if not self._film_list:
            return None
        
        all_runtimes = [(film, film.runtime) for film in self._film_list if film.runtime]
        if not all_runtimes:
            log.warning("No runtimes available to determine shortest film.")
            return None

        return min(all_runtimes, key=lambda x: x[1])[0]

    @cached_property
    def longest_film(self) -> Optional["Film"]:
        """
        Returns the film with the longest runtime.

        Returns:
            Film object with the longest runtime, or None if not available.
        """
        if not self._film_list:
            return None
        
        all_runtimes = [(film, film.runtime) for film in self._film_list if film.runtime]
        if not all_runtimes:
            log.warning("No runtimes available to determine longest film.")
            return None

        return max(all_runtimes, key=lambda x: x[1])[0]

    @cached_property
    def average_year(self) -> int:
        """
        Calculates the average release year of films in the list.
        
        Films with no parsed year are ignored in the calculation.
        
        Returns:
            int: The average year, or 0 if no films have a valid year.
        """
        if not self._film_list:
            return 0

        all_years = [film.year for film in self._film_list if film.year is not None]
        if not all_years:
            log.warning("No valid years available to calculate average.")
            return 0
        
        return int(mean(all_years))

    @cached_property
    def average_rating(self) -> float:
        """
        Calculates the average rating of all films.

        Returns:
            Average rating as a float, or 0.0 if no ratings are available.
        """
        if not self._film_list:
            return 0.0

        all_ratings = [film.rating for film in self._film_list if film.rating]
        if not all_ratings:
            log.warning("No ratings available to calculate average.")
            return 0.0
        
        return mean(all_ratings)

    def get_unseen_films(self, user_logs: "EntryList") -> List["Film"]:
        """
        Returns films that have not been seen by the user.

        Args:
            user_logs (EntryList): List of user entries.

        Returns:
            List of unseen Film objects.
        """
        if not self._film_list:
            return []

        seen_slugs = set(entry.film.slug for entry in user_logs.entries)
        if not seen_slugs:
            return self._film_list

        unseen_films = [film for film in self._film_list if film.slug not in seen_slugs]
        if not unseen_films:
            log.info("All films have been seen by the user.")
    
        return unseen_films
    
    def _compare_attributes(self, main_list: List["Film"], compared_list: List["Film"], attr: str) -> float:
        """
        Compares two lists of films by a given attribute and returns the similarity ratio.

        Args:
            main_list (List[Film]): First list of films.
            compared_list (List[Film]): Second list of films.
            attr (str): Attribute name to compare.

        Returns:
            Similarity ratio as a float.
        """
        main_unique_attrs = set(self._get_attr_list(main_list, attr))        
        compared_unique_attrs = set(self._get_attr_list(compared_list, attr))
        if not main_unique_attrs or not compared_unique_attrs:
            return 0.0

        attr_intersection = main_unique_attrs.intersection(compared_unique_attrs)        
        attr_union = main_unique_attrs.union(compared_unique_attrs)
        if not attr_intersection or not attr_union:
            return 0.0
            
        return round(len(attr_intersection) / len(attr_union), 2)
    
    def _get_top_attributes(self, compared_list: Union["FilmList", "EntryList", "FilmSearch"], 
                               attr: str) -> List[Tuple[str, str, bool]]:
        """
        Gets the top attribute from both lists and checks if they agree.

        Args:
            compared_list: Another analytics object.
            attr (str): Attribute name.

        Returns:
            List containing top attribute from both lists and agreement boolean.
        """
        func_name = f"get_top_{attr}"

        main_method = getattr(self, func_name, None)     
        compared_method = getattr(compared_list, func_name, None)
        if not main_method or not compared_method:
            return []
        
        top_attr_main = main_method(1)
        top_attr_compared = compared_method(1)

        if not top_attr_main or not top_attr_compared:
            log.warning(f"Could not retrieve top {attr} from one of the lists.")
            return []
        
        return [top_attr_main, top_attr_compared, 
                True if top_attr_main == top_attr_compared else False]
    
    def _get_unique_attributes(self, main_list: List["Film"], compared_list: List["Film"], 
                               attr: Optional[str]) -> List[Tuple[str, str, bool]]:
        """
        Returns the intersection of unique attributes between two film lists.

        Args:
            main_list (List[Film]): First list of films.
            compared_list (List[Film]): Second list of films.
            attr (Optional[str]): Attribute name, or None for direct comparison.

        Returns:
            List of common attributes.
        """
        if attr:
            unique_attrs_main = set(self._get_attr_list(main_list, attr))
            unique_attrs_compared = set(self._get_attr_list(compared_list, attr))         
        else:
            unique_attrs_main = set(main_list)
            unique_attrs_compared = set(compared_list)
        
        if not unique_attrs_main or not unique_attrs_compared:
            log.warning("No unique attributes found for comparison.")
            return []
        
        intersection = unique_attrs_main.intersection(unique_attrs_compared)
        if not intersection:
            log.warning("No common attributes found between the two lists.")
            return []
        
        return list(intersection)

    def _get_common_films_with_ratings(self, other_list: "EntryList") -> Dict[str, Dict[str, float]]:
        """
        Finds common films between two entry lists and returns their ratings.

        Args:
            other_list (EntryList): Another entry list object.

        Returns:
            Dictionary mapping film slug to ratings from both lists.
        """
        self_ratings = {
            entry.film.slug: entry.rating
            for entry in self._entry_list if entry.film and entry.rating
        }
        if not self_ratings:
            return {}
        
        common_films_ratings = {}
        for other_entry in other_list._entry_list:
            if other_entry.film and other_entry.rating and other_entry.film.slug in self_ratings:
                slug = other_entry.film.slug
                common_films_ratings[slug] = {
                    "self_rating": self_ratings[slug],
                    "other_rating": other_entry.rating
                }
                
        return common_films_ratings

    def _get_rating_agreement_on_common_films(self, other_list: "EntryList") -> Optional[Dict[str, Union[float, str]]]:
        """
        Analyzes rating agreement for films present in both entry lists.

        Args:
            other_list (EntryList): Another entry list object.

        Returns:
            Dictionary with average rating difference and most disagreed film.
        """
        common_films = self._get_common_films_with_ratings(other_list)
        if not common_films:
            return {}

        differences = {
            slug: abs(ratings["self_rating"] - ratings["other_rating"])
            for slug, ratings in common_films.items()
        }
        if not differences:
            return {}
        
        most_disagreed_slug = max(differences, key=differences.get)
        average_difference = mean(differences.values())

        return {
            "average_rating_difference": round(average_difference, 1),
            "most_disagreed_film": {
                "slug": most_disagreed_slug,
                "self_rating": common_films[most_disagreed_slug]["self_rating"],
                "other_rating": common_films[most_disagreed_slug]["other_rating"],
            }
        }

    def compare_with(self, other_list: Union["FilmList", "EntryList", "FilmSearch"]) -> ComparisonResults:
        """
        Compares the current film list with another list and returns various similarity metrics.

        Args:
            other_list: Another FilmList, EntryList, or FilmSearch object.

        Returns:
            ComparisonResults: An object containing the results of the comparison.
        """
        main_list = self._film_list
        compared_list = other_list._film_list

        if not main_list or not compared_list:
            return ComparisonResults(
                film_similarity_score=0.0,
                directors_similarity_score=0.0,
                genres_similarity_score=0.0,
                actors_similarity_score=0.0,
                year_similarity_score=0.0,
                top_director_agreement=[],
                top_actor_agreement=[],
                top_genre_agreement=[],
                common_films=[],
                common_directors=[],
                common_actors=[],
                common_genres=[],
                decade_distribution={},
                average_year_comparison={},
                average_runtime_comparison={},
                rating_comparison={}
            )
                    
        # film similarity
        film_similarity_score = self._compare_attributes(main_list, compared_list, "slug")
        
        # director similarity
        directors_similarity_score = self._compare_attributes(main_list, compared_list, "director")

        # genre similarity
        genres_similarity_score = self._compare_attributes(main_list, compared_list, "genre")

        # actors similarity
        actors_similarity_score = self._compare_attributes(main_list, compared_list, "actors")

        # year similarity
        year_similarity_score = self._compare_attributes(main_list, compared_list, "year")

        # most present director
        top_director_agreement = self._get_top_attributes(other_list, "directors")
        
        # most present actor
        top_actor_agreement = self._get_top_attributes(other_list, "actors")
        
        # most present genre
        top_genre_agreement = self._get_top_attributes(other_list, "genres")
        
        # common films
        common_films = self._get_unique_attributes(main_list, compared_list, None)

        # common directors
        common_directors = self._get_unique_attributes(main_list, compared_list, "director")

        # common actors
        common_actors = self._get_unique_attributes(main_list, compared_list, "actors")

        # common genres
        common_genres = self._get_unique_attributes(main_list, compared_list, "genre")

        # decade distribution
        main_decade_dist_list = self.get_top_decades()
        compared_decade_dist_list = other_list.get_top_decades()

        decade_distribution = {}
        if main_decade_dist_list and compared_decade_dist_list:
            main_decade_dict = dict(main_decade_dist_list)
            compared_decade_dict = dict(compared_decade_dist_list)

            decade_distribution = {
                "self_top_decade": main_decade_dist_list[0][0],
                "other_top_decade": compared_decade_dist_list[0][0]
            }
            
            decade_comparison = {
                decade: [main_decade_dict.get(decade, 0), compared_decade_dict.get(decade, 0)]
                for decade in DECADES
            }
            decade_distribution.update(decade_comparison)

        # average year
        main_avg_year = self.average_year
        compared_avg_year = other_list.average_year

        year_difference = None
        if main_avg_year > 0 and compared_avg_year > 0:
            year_difference = abs(main_avg_year - compared_avg_year)

        average_year_comparison = {
            "self_avg_year": main_avg_year,
            "other_avg_year": compared_avg_year,
            "difference": year_difference
        }

        # average runtime
        main_avg_runtime = self.average_runtime
        compared_avg_runtime = other_list.average_runtime

        runtime_difference = None
        if main_avg_runtime > 0 and compared_avg_runtime > 0:
            runtime_difference = abs(main_avg_runtime - compared_avg_runtime)

        average_runtime_comparison = {
            "self_avg_runtime": round(main_avg_runtime, 2),
            "other_avg_runtime": round(compared_avg_runtime, 2),
            "difference": round(runtime_difference, 2) if runtime_difference else None
        }

        if hasattr(self, "entries") and hasattr(other_list, "entries"):
            rating_comparison = self._get_rating_agreement_on_common_films(other_list)
        else:
            rating_comparison = {}

        return ComparisonResults(
            film_similarity_score=film_similarity_score,
            directors_similarity_score=directors_similarity_score,
            genres_similarity_score=genres_similarity_score,
            actors_similarity_score=actors_similarity_score,
            year_similarity_score=year_similarity_score,
            top_director_agreement=top_director_agreement,
            top_actor_agreement=top_actor_agreement,
            top_genre_agreement=top_genre_agreement,
            common_films=common_films,
            common_directors=common_directors,
            common_actors=common_actors,
            common_genres=common_genres,
            decade_distribution=decade_distribution,
            average_year_comparison=average_year_comparison,
            average_runtime_comparison=average_runtime_comparison,
            rating_comparison=rating_comparison
        )

class EntryAnalytics(FilmAnalytics):
    """
    Provides analytics for a list of film entries, including ratings by attribute,
    positive/negative ratio, correlation, and watch history.
    """
    def __init__(self):
        super().__init__()

    @cached_property
    def _entry_list(self) -> Optional[List]:
        """A cached property that returns the list of entries from the object."""
        try:
            return self.entries
        except:
            log.warning(f"Error accessing entry list for {self.title}.")
            return None
        
    def _ratings_by_attribute(self, attr: str) -> List[Tuple[str, float]]:
        """
        Calculates the average rating for each unique value of a given film attribute.

        Args:
            attr (str): Attribute name.

        Returns:
            List of tuples (attribute value, average rating).
        """
        if not self._entry_list:
            return []

        ratings_per_item = defaultdict(list)

        for entry in self._entry_list:
            if entry.rating is None:
                continue

            attribute_values = getattr(entry.film, attr, [])
            if not attribute_values:
                continue

            for item in attribute_values:
                ratings_per_item[item].append(entry.rating)

        if not ratings_per_item:
            return []

        avg_ratings = [(item, mean(ratings)) for item, ratings in ratings_per_item.items()]
        avg_ratings.sort(key=lambda x: x[1], reverse=True)

        return avg_ratings

    @cached_property
    def average_entry_rating(self) -> float:
        """
        Calculates the average rating across all entries.

        Returns:
            Average rating as a float, or 0.0 if no ratings.
        """
        if not self._entry_list:
            return 0.0

        all_ratings = [entry.rating for entry in self._entry_list if entry.rating]
        if not all_ratings:
            return 0.0
        
        return mean(all_ratings)

    @cached_property
    def _rating_by_genre(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of genres, sorted by average rating."""
        return self._ratings_by_attribute("genre")

    def get_rating_by_genre(self, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each genre.

        Args:
            top_n (int): Number of top genres to return.

        Returns:
            List of tuples (genre, average rating).
        """
        all_ratings = self._rating_by_genre
        if top_n and top_n > len(all_ratings):
            top_n = len(all_ratings)
        return all_ratings[:top_n] if top_n else all_ratings

    @cached_property
    def _rating_by_director(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of directors, sorted by average rating."""
        return self._ratings_by_attribute("director")

    def get_rating_by_director(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each director.

        Args:
            top_n (int): Number of top directors to return.

        Returns:
            List of tuples (director, average rating).
        """
        all_ratings = self._rating_by_director
        if top_n and top_n > len(all_ratings):
            top_n = len(all_ratings)
        return all_ratings[:top_n] if top_n else all_ratings
    
    @cached_property
    def _rating_by_actor(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of actors, sorted by average rating."""
        return self._ratings_by_attribute("actors")

    def get_rating_by_actor(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each actor.

        Args:
            top_n (int): Number of top actors to return.

        Returns:
            List of tuples (actor, average rating).
        """
        all_ratings = self._rating_by_actor
        if top_n and top_n > len(all_ratings):
            top_n = len(all_ratings)
        return all_ratings[:top_n] if top_n else all_ratings
    
    @cached_property
    def _rating_by_language(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of languages, sorted by average rating."""
        return self._ratings_by_attribute("language")

    def get_rating_by_language(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each language.

        Args:
            top_n (int): Number of top languages to return.

        Returns:
            List of tuples (language, average rating).
        """
        all_ratings = self._rating_by_language
        if top_n and top_n > len(all_ratings):
            top_n = len(all_ratings)
        return all_ratings[:top_n] if top_n else all_ratings

    @cached_property
    def _rating_by_country(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of countries, sorted by average rating."""
        return self._ratings_by_attribute("country")

    def get_rating_by_country(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each country.

        Args:
            top_n (int): Number of top countries to return.

        Returns:
            List of tuples (country, average rating).
        """
        all_ratings = self._rating_by_country
        if top_n and top_n > len(all_ratings):
            top_n = len(all_ratings)
        return all_ratings[:top_n] if top_n else all_ratings

    @cached_property
    def _rating_by_decade(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of decades, sorted by average rating."""
        ratings_by_year = self._ratings_by_attribute("year")
        decades = {decade: [] for decade in DECADES}
        
        for year, avg_rating in ratings_by_year:
            decade_str = f"{(int(year) // 10) * 10}s"
            if decade_str in decades:
                # This logic is a bit flawed as it extends with a float, not a list. Correcting it.
                # Assuming the original intent was to average the averages.
                decades[decade_str].append(avg_rating)

        return sorted([(key, mean(value)) for key, value in decades.items() if value], key=lambda x: x[1], reverse=True)

    def get_rating_by_decade(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each decade.

        Args:
            top_n (int): Number of top decades to return.

        Returns:
            List of tuples (decade, average rating).
        """
        all_ratings = self._rating_by_decade
        if top_n > len(all_ratings) or not top_n:
            top_n = len(all_ratings)
        return all_ratings[:top_n]

    @cached_property
    def _rating_by_year(self) -> List[Tuple[str, float]]:
        """A cached property for the full list of years, sorted by average rating."""
        return self._ratings_by_attribute("year")

    def get_rating_by_year(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Returns the average rating for each year.

        Args:
            top_n (int): Number of top years to return.

        Returns:
            List of tuples (year, average rating).
        """
        all_ratings = self._rating_by_year
        if top_n > len(all_ratings) or not top_n:
            top_n = len(all_ratings)
        return all_ratings[:top_n]

    def get_positive_to_negative_ratio(self, threshold: float = 3) -> Dict[str, Union[int, float]]:
        """
        Calculates the ratio of positive to negative ratings.

        Args:
            threshold (float): Minimum rating considered positive.

        Returns:
            Dictionary with counts and ratio.
        """
        if not self._entry_list:
            return {"positive": 0, "negative": 0, "ratio": None}

        all_ratings = [entry.rating for entry in self._entry_list if entry.rating]

        if not all_ratings:
            return {"positive": 0, "negative": 0, "ratio": None}

        positive_count = sum(1 for rating in all_ratings if rating >= threshold)
        negative_count = len(all_ratings) - positive_count

        if negative_count == 0:
            ratio = float('inf') if positive_count > 0 else None
        else:
            ratio = positive_count / negative_count

        return {
            "positive": positive_count,
            "negative": negative_count,
            "ratio": ratio
        }
    
    @cached_property
    def rating_correlation(self) -> float:
        """
        Calculates the Spearman correlation between user ratings and average film ratings.

        Returns:
            Correlation coefficient as a float.
        """
        try:
            from scipy.stats import spearmanr
        except ImportError:
            log.error("scipy is required for correlation calculation. Please install it running `pip install scrapxd[analytics]`.")
            return 0.0
        
        if not self._entry_list:
            return 0.0
        
        user_ratings = [entry.rating for entry in self._entry_list if entry.rating is not None]
        avg_ratings = [entry.film.avg_rating for entry in self._entry_list if entry.film.avg_rating is not None]

        if len(user_ratings) != len(avg_ratings) or len(user_ratings) < 2:
            return 0.0

        correlation, _ = spearmanr(user_ratings, avg_ratings)
        return correlation

    @cached_property
    def most_watched_month(self) -> Tuple[str, int]:
        """
        Returns the month with the most watched films.

        Returns:
            Tuple (month name, count).
        """
        if not self._entry_list:
            return ("", 0)

        entry_months = [entry.watched_date.month for entry in self._entry_list if entry.watched_date]
        if not entry_months:
            return ("", 0)

        most_common_month_num, count = Counter(entry_months).most_common(1)[0]
        return (MONTHS[most_common_month_num], count)

    @cached_property
    def most_watched_year(self) -> Tuple[int, int]:
        """
        Returns the year with the most watched films.

        Returns:
            Tuple (year, count).
        """
        if not self._entry_list:
            return (0, 0)

        entry_years = [entry.watched_date.year for entry in self._entry_list if entry.watched_date]
        if not entry_years:
            return (0, 0)

        return Counter(entry_years).most_common(1)[0]

    @cached_property
    def most_frequent_watch_day(self) -> Tuple[str, int]:
        """
        Returns the weekday with the most watched films.

        Returns:
            Tuple (weekday name, count).
        """
        if not self._entry_list:
            return ("", 0)

        entry_weekdays = [entry.watched_date.weekday() for entry in self._entry_list if entry.watched_date]
        if not entry_weekdays:
            return ("", 0)

        most_common_day_num, count = Counter(entry_weekdays).most_common(1)[0]
        return (WEEKDAYS[most_common_day_num], count)

    def get_first_watch_of(self, film: Union["Film", str]) -> Optional["Entry"]:
        """
        Returns the first entry for a given film.

        Args:
            film (Film or str): Film object or slug.

        Returns:
            Entry object or None.
        """
        from .models import Film

        if not self._entry_list:
            return None

        slug_to_find = film.slug if isinstance(film, Film) else film
        entries_with_film = [entry for entry in self._entry_list if entry.film.slug == slug_to_find and entry.watched_date]

        if not entries_with_film:
            return None
        
        return min(entries_with_film, key=lambda x: x.watched_date)

    @cached_property
    def rewatches(self) -> List[Tuple["Film", int]]:
        """
        Returns films that have been watched more than once.

        Returns:
            List of tuples (Film, watch count).
        """
        from .models import Film

        if not self._entry_list:
            return []

        all_watches = [entry.film.slug for entry in self._entry_list if entry.film]
        if not all_watches:
            return []

        watch_count = Counter(all_watches)
        return [(Film(slug=film_slug), count) for film_slug, count in watch_count.items() if count > 1]
    
    def get_first_film_by_director(self, director_name: str) -> Optional["Entry"]:
        """
        Returns the first film watched of a given director.

        Args:
            director_name (str): Name of the director.

        Returns:
            Entry object of the director's first film watched.
        """
        if not self._entry_list:
            return None

        director_watches = [entry for entry in self._entry_list if entry.watched_date 
                            and entry.film.director and director_name in entry.film.director]
        
        if not director_watches:
            return None
        
        return min(director_watches, key=lambda x:x.watched_date)
    
    def get_first_film_by_actor(self, director_name: str) -> Optional["Entry"]:
        """
        Returns the first film watched of a given actor.

        Args:
            actor_name (str): Name of the actor.

        Returns:
            Entry object of the actor's first film watched.
        """
        if not self._entry_list:
            return None

        actor_watches = [entry for entry in self._entry_list if entry.watched_date 
                            and entry.film.actors and director_name in entry.film.actors]
        
        if not actor_watches:
            return None
        
        return min(actor_watches, key=lambda x:x.watched_date)
        
    @cached_property
    def director_discovery_timeline(self) -> List[Tuple[str, date]]:
        """
        Returns the timeline of first watches for each director.

        Returns:
            List of tuples (director name, date).
        """
        if not self._entry_list:
            return []

        all_watches = [(entry.film.director, entry.watched_date) for entry in self._entry_list
                    if entry.film.director and entry.watched_date]
        if not all_watches:
            return []
        
        directors_timeline = {}
        
        # Iterate in chronological order to simplify logic
        for directors, entry_date in sorted(all_watches, key=lambda x: x[1]):
            for director in directors:
                if director not in directors_timeline:
                    directors_timeline[director] = entry_date

        return list(directors_timeline.items())
    
    @cached_property
    def actor_discovery_timeline(self) -> List[Tuple[str, date]]:
        """
        Returns the timeline of first watches for each actor.

        Returns:
            List of tuples (actor name, date).
        """
        if not self._entry_list:
            return []

        all_watches = [(entry.film.actors, entry.watched_date) for entry in self._entry_list
                    if entry.film.actors and entry.watched_date]
        if not all_watches:
            return []
        
        actors_timeline = {}
        
        # Iterate in chronological order to simplify logic
        for actors, entry_date in sorted(all_watches, key=lambda x: x[1]):
            for actor in actors:
                if actor not in actors_timeline:
                    actors_timeline[actor] = entry_date

        return list(actors_timeline.items())