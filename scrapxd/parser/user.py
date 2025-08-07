import re
from bs4 import BeautifulSoup
from math import ceil
from typing import List, Literal
from datetime import date
import scrapxd.fetcher as f
from scrapxd.config import BASE_URL
from ..models import User, Film, Entry, EntryList, UserList
from scrapxd.parser.film import parse_film_basic


def _parse_username(soup: BeautifulSoup) -> str:
    content = soup.find("section", class_="profile-header js-profile-header -is-not-mini-nav")

    if content:
        return content.get("data-person")
    
    else:
        content = soup.find("section", class_="profile-header js-profile-header -is-mini-nav")
        return content.get("data-person")

def _parse_slugs(soup: BeautifulSoup) -> List[str]:
    film_divs = soup.find_all("div", class_="really-lazy-load poster film-poster linked-film-poster")

    if film_divs:
        slug_list = []

        for div in film_divs:
            slug = div.get("data-film-slug")
            slug_list.append(slug)

        return slug_list
    
    else:
        return None
    
def _parse_slugs_with_rating(soup: BeautifulSoup) -> List[str] | None:
    film_li = soup.find_all("li", class_="poster-container")

    if film_li:
        film_list = []

        for item in film_li:
            film_div = item.find("div", class_="really-lazy-load poster film-poster linked-film-poster")
            slug = film_div.get("data-film-slug")

            rating_span = item.find("span", class_=re.compile("^rating -micro -darker rated-"))
            raw_rating = rating_span.get("class")[3]
            rating = int(raw_rating[6:]) / 2

            film_list.append([slug, rating])

        return film_list
    
    else:
        return None

def _parse_films(slugs: list) -> List[Film]:
    films = []

    for slug in slugs:
        film_data = f.fetch_film(slug, 20)
        film = parse_film_basic(film_data)
        films.append(film)

    return films

def _parse_count(soup: BeautifulSoup, type: Literal["Watched", "Diary", "Reviews", "Lists"]) -> int:
    if type == "Lists":
        div = soup.find("div", id="content-nav")
        content = div.find("span", class_="tooltip")

    else:
        content = soup.find("a", class_="tooltip", string=type)

    raw_count = content.get("title")
    match = re.match(r"\d+", raw_count)
    return int(match.group(0))

def _parse_diary_page(soup: BeautifulSoup) -> List[Entry]:
    diary_page = []

    rows = soup.find_all("tr", class_="diary-entry-row viewing-poster-container")

    for row in rows:
        date_pattern = re.compile(r"/([^/]+)/films/diary/for/(\d{4}/\d{2}/\d{2})/")
        date_link = row.find("a", href=date_pattern)
        href = date_link.get("href")
        match = date_pattern.search(href)
        date_string = match.group(2)
        entry_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

        film_data = row.find("td", class_="td-actions film-actions has-menu hide-when-logged-out")
        slug = film_data.get("data-film-slug")

        rating_span = row.find("span", class_=re.compile("^rating rated-"))
        raw_rating = rating_span.get("class")[1]
        rating = int(raw_rating[6:]) / 2

        review_link = row.find("a", class_="has-icon icon-review icon-16 tooltip")
        
        if review_link:
            review_url = review_link.get("href")
            review = f"{BASE_URL}{review_url[1:]}"

        entry = Entry(film = slug, 
                    watched_date = entry_date, 
                    rating = rating, 
                    review = review if review_link else None)

        diary_page.append(entry)

    return diary_page

def _parse_review_page(soup: BeautifulSoup) -> List[Entry]:
    review_page = []

    reviews = soup.find_all("article", class_="production-viewing -viewing viewing-poster-container js-production-viewing")

    for item in reviews:
        raw_date = item.find("time")
        date_string = raw_date.get("datetime")
        review_date = date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))

        film_data = item.find("div", class_="really-lazy-load poster film-poster linked-film-poster")
        slug = film_data.get("data-film-slug")
        
        rating_span = item.find("span", class_=re.compile("^rating -green rated-"))
        raw_rating = rating_span.get("class")[2]
        rating = int(raw_rating[6:]) / 2

        check = item.find("div", class_="collapsed-text")

        if check:
            url_div = item.find("div", class_="body-text -prose -reset js-review-body js-collapsible-text")
            text_url = url_div.get("data-full-text-url")
            text_soup = f.fetch_review_text(text_url[1:], 5)

            text = []
            paragraphs = text_soup.find_all("p")

            for p in paragraphs:
                text.append(p.get_text(separator=" ", strip=True))

            text = "".join(text)

        else:
            paragraph = item.find("p")
            text = paragraph.get_text(separator=" ", strip=True)

        review = Entry(film = slug,
                    watched_date = review_date,
                    rating = rating,
                    review = text
        )

        review_page.append(review)

    return review_page

def _parse_film_list(soup: BeautifulSoup) -> UserList:
    name_span = soup.find("span", itemprop="name")
    username = str(name_span.string)

    title_h1 = soup.find("h1", class_="title-1 prettify")
    title = str(title_h1.string)

    list_description = soup.find("meta", attrs={"name": "description"})
    print(list_description)
    description_content = list_description.get("content")
    print(description_content)
    match = re.search(r'(\d+)\s+films', description_content)
    print(match)
    total_films = int(match.group(1))

    films = [slug for slug in _parse_slugs(soup)]

    if total_films > 100:
        page_count = ceil(total_films / 100)

        for i in range(2, page_count + 1):
            page_soup = f.fetch_list(username, title, i, 5)
            slugs = _parse_slugs(page_soup)
            films.extend(slugs)

    numbered = soup.find("li", class_="poster-container numbered-list-item")

    if numbered:
        films = {i:v for i, v in enumerate(films, start=1)}

    return UserList(username = username,
                    title = title,
                    number_of_films = total_films,
                    films = films)

def _parse_list_page(soup: BeautifulSoup) -> List[UserList] | None:
    lists = soup.find_all("section", class_="list js-list -overlapped -summary")

    if lists:
        page_lists = []

        for film_list in lists:
            list_link = film_list.find("a", class_="list-link")
            href = list_link.get("href")
            match = re.match(r'^/([^/]+)/list/([^/]+)/$', href)

            list_soup = f.fetch_list(match.group(1), match.group(2), delay=10)
            page_lists.append(_parse_film_list(list_soup))
        
        return page_lists
    
    return None

def parse_user(soup: BeautifulSoup) -> User:
    pass

def parse_number_of_logs(soup: BeautifulSoup) -> int:
    content = soup.find("h4", class_="profile-statistic statistic")
    number = content.find("span", class_="value")
    return int(number.string)

def parse_favourites(soup: BeautifulSoup) -> UserList | None:
    content = soup.find_all("li", class_="poster-container favourite-film-poster-container") 

    if content:
        body = soup.find(body)
        username = body.get("data-owner")

        user_favourites = []

        for favourite in content:
            div = favourite.find("div")
            slug = div.get("data-film-slug")

            html = f.fetch_film(slug, 10)
            film = parse_film_basic(html)

            user_favourites.append(film)

        return UserList(username = username,
                        title = f"{username}'s favourites",
                        number_of_films = len(user_favourites),
                        films = user_favourites)
    
    return None

def parse_logs(soup: BeautifulSoup) -> EntryList:
    username = _parse_username(soup)
    log_count = _parse_count(soup, "Watched")
    
    user_logs = [i for i in _parse_slugs_with_rating(soup)]

    if log_count > 72:
        page_count = ceil(log_count / 72)

        for i in range(2, page_count + 1):
            page_soup = f.fetch_logs(username, i , 5)
            slugs = _parse_slugs_with_rating(page_soup)

            user_logs.extend(slugs)

    return EntryList(username = username,
                    title = f"{username}'s films",
                    number_of_entries = log_count,
                    entries = [Entry(film=i[0], rating=i[1]) for i in user_logs])
    
def parse_watchlist(soup: BeautifulSoup) -> UserList:
    content = soup.find("span", class_="js-watchlist-count")
    raw_count = str(content.string)
    match = re.match(r"\d+", raw_count)
    film_count = int(match.group(0))

    username = _parse_username(soup)
    watchlist_slugs = [slug for slug in _parse_slugs(soup)]

    if film_count > 28:
        page_count = ceil(film_count / 28)

        for page in range(2, page_count + 1):
            page_soup = f.fetch_watchlist(username, page, 15)
            slugs = _parse_slugs(page_soup)

            if slugs:
                watchlist_slugs.extend(slugs)

    return UserList(username = username,
                    title = f"{username}'s Watchlist",
                    number_of_films = film_count,
                    films = watchlist_slugs)

def parse_user_diary(soup: BeautifulSoup) -> List[Entry]:
    entry_count = _parse_count(soup, "Diary")
    diary = [entry for entry in _parse_diary_page(soup)]

    if entry_count > 50:
        page_count = ceil(entry_count / 50)
        username = _parse_username(soup)

        for page in range(2, page_count + 1):
            page_soup = f.fetch_diary(username, page, 15)
            diary_page = _parse_diary_page(page_soup)
            
            diary.extend(diary_page)
    
    return diary

def parse_user_reviews(soup: BeautifulSoup) -> List[Entry]:
    review_count = _parse_count(soup, "Reviews")

    reviews = [entry for entry in _parse_review_page(soup)]

    if review_count > 12:
        page_count = ceil(review_count / 12)
        username = _parse_username(soup)

        for page in range(2, page_count + 1):
            page_soup = f.fetch_reviews(username, page, 15)
            review_page = _parse_review_page(page_soup)
            
            reviews.extend(review_page)
    
    return reviews

def parse_user_lists(soup: BeautifulSoup) -> List[UserList] | None:
    check = soup.find("section", class_="list-set")

    if not check:
        return None

    list_count = _parse_count(soup, "Lists")
    list_count = 13

    user_lists = [film_list for film_list in _parse_list_page(soup)]

    if list_count > 12:
        page_count = ceil(list_count / 12)

        body = soup.find("body")
        username = body.get("data-owner")

        for i in range(2, page_count + 1):
            page_soup = f.fetch_user_lists(username, i, 10)
            user_lists.extend(_parse_list_page(page_soup))

    return user_lists