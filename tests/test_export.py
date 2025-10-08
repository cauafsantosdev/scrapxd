"""
Integration tests for the user data export functionality (to_csv and to_xlsx).

This suite verifies that the User model can correctly export all its associated
data lists (watchlist, logs, reviews, diary, and custom lists) into valid
CSV and XLSX files with the correct content.
"""
import pytest
import os
import csv
import openpyxl
from datetime import date
from scrapxd.models.film import Film
from scrapxd.models.entry import Entry
from scrapxd.models.film_list import FilmList
from scrapxd.models.entry_list import EntryList
from scrapxd.models.user import User


@pytest.fixture(scope="module")
def main_user_for_export():
    """
    Provides a fully populated User instance for export testing.
    """
    # Film objects
    film1 = Film(slug="close-up")
    film1.year = 1990
    film1.director = ["Abbas Kiarostami"]

    film2 = Film(slug="contempt")
    film2.year = 1963
    film2.director = ["Jean-Luc Godard"]

    film3 = Film(slug="largent-1983")
    film3.year = 1983
    film3.director = ["Robert Bresson"]

    # Entry objects for logs, diary, and reviews
    entry1 = Entry(film=film1, username="cinephile", watched_date=date(2024, 1, 10), rating=5.0, review="A masterpiece.")
    entry2 = Entry(film=film2, username="cinephile", watched_date=date(2024, 2, 15), rating=4.5, review="Iconic and cool.")

    # Lists
    all_entries = [entry1, entry2]
    review_entries = [e for e in all_entries if e.review]
    
    logs_list = EntryList(username="cinephile", title="Logs", number_of_entries=len(all_entries), entries=all_entries)
    reviews_list = EntryList(username="cinephile", title="Reviews", number_of_entries=len(review_entries), entries=review_entries)
    watchlist = FilmList(username="cinephile", title="Watchlist", number_of_films=1, films=[film3])
    custom_list = FilmList(username="cinephile", title="My Favorites", number_of_films=2, films=[film1, film2])

    # Main user object
    user = User(username="cinephile")
    user.logs = logs_list
    user.diary = logs_list  # Using same for simplicity
    user.reviews = reviews_list
    user.watchlist = watchlist
    user.lists = [custom_list]

    return user

def test_user_to_csv_export(main_user_for_export, tmp_path):
    """
    Tests the to_csv export functionality for the User model.
    It verifies that:
    1. The correct CSV files are created in the specified directory.
    2. The files are not empty.
    3. The headers are written correctly.
    4. The data in the rows corresponds to the mock data.
    """
    # tmp_path provides a temporary directory path
    output_dir = tmp_path / "csv_export"
    main_user_for_export.to_csv(output_dir=str(output_dir))
    
    # 1. Check if all expected files were created
    watchlist_path = output_dir / "cinephile_watchlist.csv"
    logs_path = output_dir / "cinephile_logs.csv"
    reviews_path = output_dir / "cinephile_reviews.csv"
    diary_path = output_dir / "cinephile_diary.csv"
    custom_list_path = output_dir / "cinephile_My_Favorites.csv"

    assert watchlist_path.exists()
    assert logs_path.exists()
    assert reviews_path.exists()
    assert diary_path.exists()
    assert custom_list_path.exists()

    # 2. Verify content of a sample file
    with open(watchlist_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        data = list(reader)

        # 3. Verify headers
        assert "fetcher" not in headers
        assert "slug" in headers
        assert "year" in headers

        # 4. Verify row data
        assert len(data) == 1
        assert data[0]["slug"] == "largent-1983"
        assert data[0]["year"] == "1983"

def test_user_to_xlsx_export(main_user_for_export, tmp_path):
    """
    Tests the to_xlsx export functionality for the User model.
    It verifies that:
    1. The correct XLSX files are created.
    2. The files are valid and can be opened with openpyxl.
    3. The headers and data content are correct.
    """
    # tmp_path provides a temporary directory path
    output_dir = tmp_path / "xlsx_export"
    main_user_for_export.to_xlsx(output_dir=output_dir)

    # 1. Check if a sample file was created
    logs_path = output_dir / "cinephile_logs.xlsx"
    assert logs_path.exists()

    # 2. Open the generated XLSX file to verify its content
    workbook = openpyxl.load_workbook(logs_path)
    sheet = workbook.active

    # 3. Verify headers and content
    headers = [cell.value for cell in sheet[1]]
    assert "fetcher" not in headers
    assert "film_slug" in headers 
    assert "rating" in headers
    assert "review" in headers

    first_data_row = [cell.value for cell in sheet[2]]
    data_dict = dict(zip(headers, first_data_row))

    assert data_dict["film_slug"] == "close-up"
    assert data_dict["rating"] == 5.0 
    assert data_dict["review"] == "A masterpiece."