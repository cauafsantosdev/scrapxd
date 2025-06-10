import requests
from bs4 import BeautifulSoup


headers = {"User-Agent": "Mozilla/5.0"}

URL = "https://letterboxd.com/films/ajax/popular/page/2/"
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")

films = soup.find_all("div", class_="really-lazy-load poster film-poster linked-film-poster")

for film in films:
    slug = film.get("data-film-slug")
    print(slug)

"""PROFILE_URL = "https://letterboxd.com/methdrinkerr/"
profile = requests.get(PROFILE_URL, headers=headers)

soup = BeautifulSoup(profile.content, "html.parser")
total_films = soup.find("a", href="/methdrinkerr/films/")
total_films = total_films.find("span", class_="value")
total_films = int(total_films.string)

user_film_pages = int(total_films / 72)

for i in range(1, user_film_pages+1):
    url = f"https://letterboxd.com/methdrinkerr/films/page/{i}/"
    page = requests.get(url, headers=headers)

    user_film_soup = BeautifulSoup(page.content, "html.parser")
    user_films = user_film_soup.find_all("div", class_="really-lazy-load poster film-poster linked-film-poster")

    for film in user_films:
        slug = film.get("data-film-slug")
        
        film_url = f"https://letterboxd.com/film/{slug}/"
        film_page = requests.get(film_url, headers=headers)

        film_soup = BeautifulSoup(film_page.content, "html.parser")

        title = film_soup.find("span", class_="name js-widont prettify")
        print(title.string)"""
