"""
Unit tests for the FilmSearch model's query building and result parsing.

This suite tests two key functionalities of the FilmSearch class:
1. The `_mount_query` method, ensuring that search parameters are correctly
   formatted into a valid Letterboxd URL slug.
2. The `search` method, verifying that the class can correctly parse a local
   HTML fixture file representing a search result page.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from scrapxd.models.film_search import FilmSearch
from scrapxd.models.film_search import FilmSearchResult


@pytest.fixture(scope="module")
def search_result_soup():
    """
    Provides the parsed soup of a film search result page from a local file.
    """
    filename = "crime_drama_notsciencefiction_1960s.htm"
    path = Path(__file__).parent / "fixtures" / "html" / "search" / filename
    with open(path, 'r', encoding='utf-8') as f:
        return BeautifulSoup(f.read(), "lxml")

@pytest.mark.parametrize("params, expected_query", [
    (
        {"decade": "1990s", "genre": "sci-fi"},
        "popular/decade/1990s/genre/sci-fi"
    ),
    (
        {"year": 2023, "order_by": "rating"},
        "year/2023/by/rating"
    ),
    (
        {"genre": ["crime", "drama"], "not_genre": "action"},
        "popular/genre/crime+drama+-action"
    ),
    (
        {"order_by": "release"},
        "by/release"
    ),
    (
        {},
        "popular"
    )
])
def test_mount_query(params, expected_query):
    """
    Tests the _mount_query method to ensure it builds correct URL query strings.
    This test is parameterized to check various combinations of search filters.
    """
    search_instance = FilmSearch(**params)
    assert search_instance._mount_query() == expected_query

def test_search_parsing(mocker, search_result_soup):
    """
    Tests the `search` method by feeding it a local HTML file.
    It verifies that the FilmSearchResult is correctly populated with films
    parsed from the fixture.
    """
    search_params = {
        "decade": "1960s",
        "genre": ["crime", "drama"],
        "not_genre": "science-fiction",
        "limit": 12
    }
    search_instance = FilmSearch(**search_params)

    mocker.patch.object(search_instance, '_get_soup', return_value=search_result_soup)

    result = search_instance.search()

    assert isinstance(result, FilmSearchResult)

    expected_query = "popular/decade/1960s/genre/crime+drama+-science-fiction"
    assert result.query == expected_query

    assert result.total_films_found == 12
    assert len(result.films) == 12

    film_slugs = [film.slug for film in result.films]
    assert "breathless" in film_slugs
    assert "pierrot-le-fou" in film_slugs