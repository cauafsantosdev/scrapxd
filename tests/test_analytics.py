"""
Tests for the FilmAnalytics and EntryAnalytics classes from the scrapxd.analytics module.

This test suite uses pytest fixtures to create mock data representing film and entry lists,
and then runs a series of assertions to validate the correctness of each analytics method.
"""
import pytest
from datetime import date
from scrapxd.models.film import Film
from scrapxd.models.entry import Entry
from scrapxd.models.film_list import FilmList
from scrapxd.models.entry_list import EntryList


@pytest.fixture(scope="module")
def mock_films():
    """
    Provides a list of mock Film objects for testing.
    """
    film1 = Film(slug="film-a")
    film1.director = ["Director A"]
    film1.actors = ["Actor 1", "Actor 2"]
    film1.genre = ["Drama", "Thriller"]
    film1.year = 2000
    film1.runtime = 120
    film1.avg_rating = 4.1

    film2 = Film(slug="film-b")
    film2.director = ["Director B"]
    film2.actors = ["Actor 2", "Actor 3"]
    film2.genre = ["Comedy", "Drama"]
    film2.year = 2010
    film2.runtime = 90
    film2.avg_rating = 3.2

    film3 = Film(slug="film-c")
    film3.director = ["Director A"]
    film3.actors = ["Actor 4"]
    film3.genre = ["Sci-Fi"]
    film3.year = 2020
    film3.runtime = 150
    film3.avg_rating = 4.8
    
    return [film1, film2, film3]

@pytest.fixture(scope="module")
def mock_film_list(mock_films):
    """
    Provides a FilmList instance populated with mock films.
    """
    return FilmList(
        username="testuser",
        title="Test Film List",
        number_of_films=len(mock_films),
        films=mock_films
    )

@pytest.fixture(scope="module")
def mock_entries(mock_films):
    """
    Provides a list of mock Entry objects for testing.
    """
    film1, film2, film3 = mock_films
    
    entry1 = Entry(film=film1, watched_date=date(2023, 1, 15), rating=4.5)
    entry2 = Entry(film=film2, watched_date=date(2023, 1, 20), rating=3.0)
    entry3 = Entry(film=film3, watched_date=date(2023, 2, 10), rating=5.0)
    # Rewatch entry for film1
    entry4 = Entry(film=film1, watched_date=date(2024, 5, 5), rating=4.0)
    
    return [entry1, entry2, entry3, entry4]

@pytest.fixture(scope="module")
def mock_entry_list(mock_entries):
    """
    Provides an EntryList instance populated with mock entries.
    """
    return EntryList(
        username="testuser",
        title="Test Diary",
        number_of_entries=len(mock_entries),
        entries=mock_entries
    )

class TestFilmAnalytics:
    """
    Test suite for the FilmAnalytics mixin class.
    """

    def test_get_top_directors(self, mock_film_list):
        """
        Tests that top directors are correctly counted and sorted.
        """
        top_directors = mock_film_list.get_top_directors()
        assert top_directors[0] == ("Director A", 2)
        assert top_directors[1] == ("Director B", 1)
        
        # Test with top_n limit
        assert len(mock_film_list.get_top_directors(top_n=1)) == 1

    def test_get_top_actors(self, mock_film_list):
        """
        Tests that top actors are correctly counted and sorted.
        """
        top_actors = mock_film_list.get_top_actors()
        assert top_actors[0] == ("Actor 2", 2)
        assert len(mock_film_list.get_top_actors(top_n=2)) == 2

    def test_get_top_genres(self, mock_film_list):
        """
        Tests that top genres are correctly counted and sorted.
        """
        top_genres = mock_film_list.get_top_genres()
        assert top_genres[0] == ("Drama", 2)
        assert ("Sci-Fi", 1) in top_genres

    def test_average_runtime(self, mock_film_list):
        """
        Tests the calculation of the average film runtime.
        """
        # (120 + 90 + 150) / 3 = 120
        assert mock_film_list.average_runtime == 120.0

    def test_shortest_and_longest_film(self, mock_film_list):
        """
        Tests the identification of the shortest and longest films.
        """
        assert mock_film_list.shortest_film.slug == "film-b"
        assert mock_film_list.longest_film.slug == "film-c"

    def test_average_year(self, mock_film_list):
        """
        Tests the calculation of the average film release year.
        """
        # (2000 + 2010 + 2020) / 3 = 2010
        assert mock_film_list.average_year == 2010

    def test_get_unseen_films(self, mock_film_list, mock_entries):
        """
        Tests filtering for films not present in a user's logs.
        """
        # Create a smaller log that has only seen film-a
        partial_log = EntryList(username="otheruser", title="Partial Log", number_of_entries=1, entries=[mock_entries[0]])
        
        unseen = mock_film_list.get_unseen_films(partial_log)
        unseen_slugs = {film.slug for film in unseen}
        
        assert "film-a" not in unseen_slugs
        assert "film-b" in unseen_slugs
        assert "film-c" in unseen_slugs
        
    def test_empty_list_analytics(self):
        """
        Tests that analytics methods handle empty lists correctly.
        """
        empty_list = FilmList(username="empty", title="Empty", number_of_films=0, films=[])
        assert empty_list.get_top_directors() == []
        assert empty_list.average_runtime == 0.0
        assert empty_list.average_year == 0

class TestEntryAnalytics:
    """
    Test suite for the EntryAnalytics mixin class, extending FilmAnalytics.
    """

    def test_average_entry_rating(self, mock_entry_list):
        """
        Tests the calculation of the average user rating from entries.
        """
        # (4.5 + 3.0 + 5.0 + 4.0) / 4 = 4.125
        assert mock_entry_list.average_entry_rating == 4.125

    def test_get_rating_by_genre(self, mock_entry_list):
        """
        Tests the calculation of average rating per genre.
        """
        ratings = mock_entry_list.get_rating_by_genre()
        ratings_dict = {genre: avg for genre, avg in ratings}
        
        assert ratings_dict["Sci-Fi"] == 5.0  # Only film-c
        # Drama: film-a (4.5, 4.0), film-b (3.0) -> (4.5 + 4.0 + 3.0) / 3 = 3.833...
        assert round(ratings_dict["Drama"], 2) == 3.83
        # Thriller: film-a (4.5, 4.0) -> (4.5 + 4.0) / 2 = 4.25
        assert ratings_dict["Thriller"] == 4.25

    def test_get_rating_by_actor(self, mock_entry_list):
        """
        Tests the calculation of average rating per actor.
        """
        ratings = mock_entry_list.get_rating_by_actor()
        ratings_dict = {actor: avg for actor, avg in ratings}

        assert ratings_dict["Actor 4"] == 5.0 # film-c, rating 5.0
        assert ratings_dict["Actor 3"] == 3.0 # film-b, rating 3.0
        # Actor 2 is in film-a (ratings 4.5, 4.0) and film-b (rating 3.0)
        # Average = (4.5 + 4.0 + 3.0) / 3 = 3.833...
        assert round(ratings_dict["Actor 2"], 2) == 3.83
        # Actor 1 is in film-a (ratings 4.5, 4.0) -> (4.5 + 4.0) / 2 = 4.25
        assert ratings_dict["Actor 1"] == 4.25

    def test_rating_correlation(self, mock_entry_list):
        """
        Tests the Spearman correlation between user ratings and average film ratings.
        """
        # User Ratings: [4.5, 3.0, 5.0, 4.0] -> for film-a, film-b, film-c, film-a
        # Avg Ratings:  [4.1, 3.2, 4.8, 4.1]
        # A positive correlation is expected as higher user ratings correspond to higher avg ratings.
        correlation = mock_entry_list.rating_correlation
        assert correlation > 0.5
        assert correlation < 1.0

    def test_get_positive_to_negative_ratio(self, mock_entry_list):
        """
        Tests the ratio of positive to negative ratings.
        """
        # With threshold 3.5, 1 negative (3.0) and 3 positives (4.5, 5.0, 4.0)
        ratio = mock_entry_list.get_positive_to_negative_ratio(threshold=3.5)
        assert ratio["positive"] == 3
        assert ratio["negative"] == 1
        assert ratio["ratio"] == 3.0

    def test_most_watched_month_and_year(self, mock_entry_list):
        """
        Tests identification of the most active month and year.
        """
        # January 2023 has 2 entries
        assert mock_entry_list.most_watched_month == ("January", 2)
        # 2023 has 3 entries
        assert mock_entry_list.most_watched_year == (2023, 3)

    def test_get_rewatches(self, mock_entry_list):
        """
        Tests the identification of rewatched films.
        """
        rewatches = mock_entry_list.rewatches
        assert len(rewatches) == 1
        film, count = rewatches[0]
        assert film.slug == "film-a"
        assert count == 2

    def test_get_first_watch_of(self, mock_entry_list):
        """
        Tests finding the earliest watch entry for a specific film.
        """
        first_watch = mock_entry_list.get_first_watch_of("film-a")
        assert first_watch.watched_date == date(2023, 1, 15)

    def test_director_discovery_timeline(self, mock_entry_list):
        """
        Tests the creation of a director discovery timeline.
        """
        timeline = mock_entry_list.director_discovery_timeline
        timeline_dict = {director: day for director, day in timeline}
        
        # First watch of Director A was on 2023-01-15
        assert timeline_dict["Director A"] == date(2023, 1, 15)
        # First watch of Director B was on 2023-01-20
        assert timeline_dict["Director B"] == date(2023, 1, 20)

    def test_empty_entry_list_analytics(self):
        """
        Tests that EntryAnalytics methods handle empty lists correctly.
        """
        empty_list = EntryList(username="empty", title="Empty", number_of_entries=0, entries=[])
        assert empty_list.average_entry_rating == 0.0
        assert empty_list.get_rating_by_genre() == []
        assert empty_list.rewatches == []
        assert empty_list.rating_correlation == 0.0