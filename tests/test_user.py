"""
Unit tests for the User model's parsing methods.

This test suite uses local HTML fixture files to test the data extraction logic
of the User class without making any actual network requests. It mocks the
_get_soup method to feed local HTML data to the parsing functions, ensuring
that each attribute is parsed correctly, including pagination logic.
"""
import pytest
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
from scrapxd.models.user import User
from scrapxd.models.entry import Entry
from scrapxd.models.film_list import FilmList
from scrapxd.models.entry_list import EntryList


TEST_USERNAME = "hyumiguel"

@pytest.fixture(scope="module")
def html_fixtures_path():
    """
    Returns the base path to the HTML fixtures directory.
    """
    return Path(__file__).parent / "fixtures" / "html" / "user" / TEST_USERNAME

def load_html_fixture(path: Path) -> BeautifulSoup:
    """
    Helper function to load an HTML file and parse it with BeautifulSoup.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return BeautifulSoup(f.read(), "lxml")

@pytest.fixture(scope="module")
def user_profile_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's main profile page.
    """
    return load_html_fixture(html_fixtures_path / "profile.htm")

@pytest.fixture(scope="module")
def user_films_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's films (logs) page.
    """
    return load_html_fixture(html_fixtures_path / "films_page_1.htm")

@pytest.fixture(scope="module")
def user_diary_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's diary page.
    """
    return load_html_fixture(html_fixtures_path / "diary_page_1.htm")
    
@pytest.fixture(scope="module")
def user_reviews_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's reviews page.
    """
    return load_html_fixture(html_fixtures_path / "reviews_page_1.htm")

@pytest.fixture(scope="module")
def user_watchlist_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's watchlist page.
    """
    return load_html_fixture(html_fixtures_path / "watchlist_page_1.htm")

@pytest.fixture(scope="module")
def user_following_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's following page.
    """
    return load_html_fixture(html_fixtures_path / "following_page_1.htm")

@pytest.fixture(scope="module")
def user_followers_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's followers page.
    """
    return load_html_fixture(html_fixtures_path / "followers_page_1.htm")

@pytest.fixture(scope="module")
def user_lists_index_soup(html_fixtures_path):
    """
    Provides the parsed soup of the user's main lists index page.
    """
    return load_html_fixture(html_fixtures_path / "lists_index_page_1.htm")

@pytest.fixture(scope="module")
def specific_list_page1_soup(html_fixtures_path):
    """
    Provides the parsed soup for page 1 of a specific, multi-page list.
    """
    return load_html_fixture(html_fixtures_path / "list_specific_page_1.htm")

@pytest.fixture(scope="module")
def specific_list_page2_soup(html_fixtures_path):
    """
    Provides the parsed soup for page 2 of a specific, multi-page list.
    """
    return load_html_fixture(html_fixtures_path / "list_specific_page_2.htm")

@pytest.fixture
def mocked_user(mocker, user_profile_soup, user_films_soup, user_diary_soup, user_reviews_soup, user_watchlist_soup, user_following_soup, user_followers_soup):
    """
    Mocks the _get_soup method of the User instance for single-page parsing tests.
    For any page number > 1, it returns None, stopping pagination loops during tests.
    """
    user = User(username=TEST_USERNAME)

    def mock_get_soup(fetch_function, *args):
        page_num = 1
        for arg in args:
            if isinstance(arg, int):
                page_num = arg
                break
        
        if page_num > 1:
            return None

        func_name = fetch_function.__name__
        if func_name == "fetch_user":
            return user_profile_soup
        if func_name == "fetch_logs":
            return user_films_soup
        if func_name == "fetch_diary":
            return user_diary_soup
        if func_name == "fetch_reviews":
            return user_reviews_soup
        if func_name == "fetch_watchlist":
            return user_watchlist_soup
        if func_name == "fetch_follows":
            return user_following_soup
        if func_name == "fetch_followers":
            return user_followers_soup
        return None

    mocker.patch.object(user, '_get_soup', side_effect=mock_get_soup)
    return user

@pytest.fixture
def mocked_user_for_pagination(mocker, user_lists_index_soup, specific_list_page1_soup, specific_list_page2_soup):
    """
    A specialized mock for testing the pagination logic of parsing user lists.
    It returns different HTML content based on the page number requested AND the list slug.
    """
    user = User(username=TEST_USERNAME)

    PAGINATED_LIST_SLUG = "pra-nao-esquecer-de-ver"

    def mock_get_soup_for_lists(fetch_function, *args):
        func_name = fetch_function.__name__
        
        if func_name == "fetch_user_lists":
            page_num = args[2] if len(args) > 2 else 1
            if page_num > 1:
                return None

            return user_lists_index_soup
            
        if func_name == "fetch_list":
            list_slug = args[1]
            page_num = args[2] if len(args) > 2 else 1
            
            if list_slug == PAGINATED_LIST_SLUG:
                if page_num == 1:
                    return specific_list_page1_soup
                if page_num == 2:
                    return specific_list_page2_soup
                return None
            else:
                if page_num == 1:
                    return specific_list_page1_soup
                return None
        
        return None
    
    mocker.patch.object(user, '_get_soup', side_effect=mock_get_soup_for_lists)
    return user

class TestUserParsing:
    """
    Test suite for verifying the HTML parsing logic of the User model.
    """
    def test_parse_display_name(self, mocked_user):
        """
        Tests that the user's display name is parsed correctly.
        """
        display_name = mocked_user.display_name
        assert display_name == "hyumiguel"

    def test_parse_avatar(self, mocked_user):
        """
        Tests that the user's avatar URL is parsed correctly.
        """
        avatar_url = mocked_user.avatar
        assert avatar_url.endswith("/avtr-0-220-0-220-crop.jpg")

    def test_parse_bio_and_location(self, mocked_user):
        """
        Tests that the user's bio and location are parsed correctly.
        """
        assert mocked_user.bio == "O cinema é o desejo que temos de ser. Meu blog"
        assert mocked_user.location == "Brasília"

    def test_parse_number_of_logs(self, mocked_user):
        """
        Tests that the total number of logged films is parsed correctly.
        """
        total_logs = mocked_user.total_logs
        assert isinstance(total_logs, int)
        assert total_logs == 914

    def test_parse_favourites(self, mocked_user):
        """
        Tests that the user's four favourite films are parsed.
        """
        favourites = mocked_user.favourites
        assert isinstance(favourites, FilmList)
        assert favourites.number_of_films == 4
        assert favourites.films[0].slug == "sunrise-a-song-of-two-humans"

    def test_parse_logs(self, mocked_user):
        """
        Tests parsing the user's watched films (logs).
        """
        logs = mocked_user.logs
        assert isinstance(logs, EntryList)
        assert logs.number_of_entries == 914
        assert len(logs.entries) == 72
        assert logs.entries[0].film.slug == "weapons-2025"
        assert logs.entries[0].rating == 2

    def test_parse_user_diary(self, mocked_user):
        """
        Tests parsing the user's diary page.
        """
        diary = mocked_user.diary
        assert isinstance(diary, EntryList)
        assert diary.number_of_entries == 595
        first_entry = diary.entries[0]
        assert isinstance(first_entry, Entry)
        assert isinstance(first_entry.watched_date, date)
        assert first_entry.film.slug == "the-hitch-hiker"
        assert first_entry.rating == 4

    def test_parse_user_reviews(self, mocked_user):
        """
        Tests parsing the user's reviews page.
        """
        reviews = mocked_user.reviews
        assert isinstance(reviews, EntryList)
        assert reviews.number_of_entries == 153
        assert len(reviews.entries[0].review) > 50

    def test_parse_watchlist(self, mocked_user):
        """
        Tests parsing the user's watchlist.
        """
        watchlist = mocked_user.watchlist
        assert isinstance(watchlist, FilmList)
        assert watchlist.number_of_films == 697
        assert len(watchlist.films) == 28
        assert watchlist.films[0].slug == "no-5-checked-out"

    def test_parse_following(self, mocked_user):
        """
        Tests parsing the user's following list.
        """
        assert mocked_user.total_follows == 998
        
        following_list = mocked_user.following
        assert isinstance(following_list, list)
        assert len(following_list) == 25
        assert following_list[0].username == "jwuliazz"

    def test_parse_followers(self, mocked_user):
        """
        Tests parsing the user's followers list.
        """
        assert mocked_user.total_followers == 1972
        
        followers_list = mocked_user.followers
        assert isinstance(followers_list, list)
        assert len(followers_list) == 25
        assert followers_list[0].username == "gabriellrosa7"

    def test_parse_user_lists_with_pagination(self, mocked_user_for_pagination):
        """
        Tests the entire process of parsing lists, including handling pagination
        for a specific multi-page list.
        """
        user_lists = mocked_user_for_pagination.lists
        
        assert isinstance(user_lists, list)
        assert len(user_lists) > 0

        specific_list = None
        for film_list in user_lists:
            if film_list.title == "pra não esquecer de ver":
                specific_list = film_list
                break

        assert specific_list is not None
        
        assert specific_list.number_of_films == 601
        assert len(specific_list.films) == 105