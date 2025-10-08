"""
Unit tests for the Film model's parsing methods.

This test suite uses a local HTML fixture file for "Mulholland Drive" to test
the data extraction logic of the Film class. By mocking the _get_soup method,
it ensures that all parsing properties work correctly without making actual network requests.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from scrapxd.models.film import Film

TEST_FILM_SLUG = "mulholland-drive"

@pytest.fixture(scope="module")
def film_html_path():
    """
    Returns the path to the film's HTML fixture file.
    """
    filename = "MulhollandDrive_2001_DavidLynch.htm"
    return Path(__file__).parent / "fixtures" / "html" / "film" / filename

@pytest.fixture(scope="module")
def film_soup(film_html_path):
    """
    Provides the parsed soup of the film's main page.
    """
    with open(film_html_path, 'r', encoding='utf-8') as f:
        return BeautifulSoup(f.read(), "lxml")

@pytest.fixture
def mocked_film(mocker, film_soup):
    """
    Mocks the _get_soup method of a Film instance for "Mulholland Drive".
    This fixture intercepts network calls and returns the local HTML content instead.
    """
    film = Film(slug=TEST_FILM_SLUG)
    mocker.patch.object(film, '_get_soup', return_value=film_soup)
    
    return film

class TestFilmParsing:
    """
    Test suite for verifying the HTML parsing logic of the Film model.
    """
    def test_basic_attributes(self, mocked_film):
        """
        Tests fundamental attributes like title, year, and director.
        """
        assert mocked_film.title == "Mulholland Drive"
        assert mocked_film.year == 2001
        assert "David Lynch" in mocked_film.director

    def test_synopsis_and_tagline(self, mocked_film):
        """
        Tests that the synopsis and tagline are parsed correctly.
        """
        assert "Blonde Betty Elms has only just arrived in Hollywood" in mocked_film.synopsis
        assert mocked_film.tagline == "A love story in the city of dreams."

    def test_runtime_and_id(self, mocked_film):
        """
        Tests parsing of the film's runtime and TMDb ID.
        """
        assert mocked_film.runtime == 147
        assert mocked_film.id == 1018

    def test_genre_and_country(self, mocked_film):
        """
        Tests that genre and country lists are correctly extracted.
        """
        assert "Thriller" in mocked_film.genre
        assert "Mystery" in mocked_film.genre
        assert "Drama" in mocked_film.genre
        assert "USA" in mocked_film.country
        assert "France" in mocked_film.country

    def test_cast_parsing(self, mocked_film):
        """
        Tests that the main cast (actor: character) is parsed into a dictionary.
        """
        cast = mocked_film.cast
        assert isinstance(cast, dict)
        assert "Naomi Watts" in cast
        assert cast["Naomi Watts"] == "Betty Elms / Diane Selwyn"
        assert "Laura Harring" in cast
        assert cast["Laura Harring"] == "Rita / Camilla Rhodes"
        
        # Also test the derived properties `actors` and `characters`
        assert "Justin Theroux" in mocked_film.actors
        assert "Adam" in mocked_film.characters

    def test_crew_parsing(self, mocked_film):
        """
        Tests that the crew dictionary is parsed correctly.
        """
        crew = mocked_film.crew
        assert isinstance(crew, dict)
        assert "David Lynch" in crew["Writer"]
        assert "Angelo Badalamenti" in crew["Composer"]
        assert "Peter Deming" in crew["Cinematography"]

    def test_rating_and_logs(self, mocked_film):
        """
        Tests parsing of the average rating and total log count from the JSON-LD script.
        """
        assert isinstance(mocked_film.avg_rating, float)
        assert mocked_film.avg_rating == 4.26
        
        assert isinstance(mocked_film.total_logs, int)
        assert mocked_film.total_logs == 987917