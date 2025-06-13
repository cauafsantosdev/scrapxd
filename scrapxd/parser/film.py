import re
import json
from scrapxd.fetcher import fetch_nanogenres
from scrapxd.models.film import Film
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Literal


def _script_to_json(soup: BeautifulSoup) -> Dict[str, Any]:
    script = soup.find("script", type="application/ld+json")
    raw_json = script.string
    cleaned_json = raw_json.strip().replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    data = json.loads(cleaned_json)

    return data

def _parse_tab_details(soup: BeautifulSoup, type: Literal["Studio", "Country", "Language"]) -> List[str]:
    content = soup.find("div", id="tab-details")
    detail_paragraphs = content.find_all("p")

    check = content.find("span", string=f"{type}")

    type_idx = {"Studio": 0, "Country": 1, "Language": 2}
    idx = type_idx[type]

    if type == "Language" and not check:
        primary = str(detail_paragraphs[idx].find("a").string)
        details = [primary]

        links = detail_paragraphs[idx+1].find_all("a")
        details += [str(detail.string) for detail in links if str(detail.string) != primary]
        return details

    elif not check:
        links = detail_paragraphs[idx].find_all("a")
        return [str(detail.string).strip() for detail in links]
    
    else:
        link = detail_paragraphs[idx].find("a")
        return [str(link.string).strip()]
    
def _parse_actor_links(soup: BeautifulSoup) -> BeautifulSoup:
    content = soup.find("div", class_="cast-list text-sluglist")
    return content.find_all("a", class_="text-slug tooltip")

def parse_film(soup: BeautifulSoup) -> Film:
    slug = parse_slug(soup)
    id = parse_id(soup)
    title = parse_title(soup)
    year = parse_year(soup)
    runtime = parse_runtime(soup)
    director = parse_director(soup)
    genre = parse_genre(soup)
    nanogenres = parse_nanogenres(soup)
    themes = parse_themes(soup)
    country = parse_country(soup)
    language = parse_language(soup)
    cast = parse_cast(soup)
    crew = parse_crew(soup)
    studio = parse_studio(soup)
    avg_rating = parse_avg_rating(soup)
    total_logs = parse_total_logs(soup)

    return Film(
            slug = slug,
            id = id,
            title = title,
            year = year,
            runtime = runtime,
            director = director,
            genre = genre,
            nanogenres = nanogenres,
            themes = themes,
            country = country,
            language = language,
            cast = cast,
            crew = crew,
            studio = studio,
            avg_rating = avg_rating,
            total_logs = total_logs
            )

def parse_slug(soup: BeautifulSoup) -> str:
    content = soup.find("div", class_="really-lazy-load poster film-poster")
    return content.get("data-film-slug")

def parse_id(soup: BeautifulSoup) -> int:
    content = soup.find("a", class_="micro-button track-event", href=re.compile(r'^https://www\.themoviedb\.org/movie/'))
    id_link = content.get("href")
    film_id = int(id_link.replace("https://www.themoviedb.org/movie/", "").replace("/", ""))

    return film_id

def parse_title(soup: BeautifulSoup) -> str:
    title = soup.find("span", class_="name js-widont prettify")
    return str(title.string)

def parse_director(soup: BeautifulSoup) -> List[str]:
    content = soup.find_all("a", class_="contributor")
    
    directors_list = []

    for director in content:
        name = director.find("span", class_="prettify")
        directors_list.append(str(name.string))

    return directors_list

def parse_year(soup: BeautifulSoup) -> int:
    content = soup.find("span", class_="releasedate")
    year = content.find("a")
    return int(year.string)

def parse_runtime(soup: BeautifulSoup) -> int:
    content = soup.find("p", class_="text-link text-footer")
    raw_text = str(content.text).strip()
    runtime = ""
    
    for c in raw_text:
        if c.isdigit() == False:
            break
        else:
            runtime += c

    return int(runtime)

def parse_cast(soup: BeautifulSoup) -> Dict[str, str]:
    actor_links = _parse_actor_links(soup)

    cast = {}

    for actor in actor_links:
        name = str(actor.string)
        character = actor.get("title").replace(" (uncredited)", "")

        cast[name] = character

    return cast

def parse_actors(soup: BeautifulSoup) -> List[str]:
    return [str(actor.string) for actor in _parse_actor_links(soup)]

def parse_characters(soup: BeautifulSoup) -> List[str]:
    return [actor.get("title").replace(" (uncredited)", "") for actor in _parse_actor_links(soup)]

def parse_crew(soup: BeautifulSoup) -> Dict[str, str | List[str]]:
    content = soup.find("div", id="tab-crew")
    roles = content.find_all("span", class_="crewrole -full")
    crew_paragraphs = content.find_all("p")

    crew = {}
    
    for i, role in enumerate(roles):
        role_name = str(role.string)
        person_links = crew_paragraphs[i].find_all("a")

        persons = [str(person.string) for person in person_links]

        crew[role_name] = persons[0] if len(persons) == 1 else persons

    return crew

def parse_studio(soup: BeautifulSoup) -> List[str]:
    return _parse_tab_details(soup, "Studio")

def parse_country(soup: BeautifulSoup) -> List[str]:
    return _parse_tab_details(soup, "Country")

def parse_language(soup: BeautifulSoup) -> List[str]:
    return _parse_tab_details(soup, "Language")

def parse_genre(soup: BeautifulSoup) -> List[str]:
    content = soup.find("div", id="tab-genres")
    content_paragraphs = content.find_all("p")

    check = content.find("span", string="Genre")

    if not check:
        genre_links = content_paragraphs[0].find_all("a")
        return [str(genre.string) for genre in genre_links]
            
    else:
        genre_link = content_paragraphs[0].find("a")
        return [str(genre_link.string)]

def parse_themes(soup: BeautifulSoup) -> List[str] | None:
    content = soup.find("div", id="tab-genres")
    content_paragraphs = content.find_all("p")

    single_check = content.find("span", string="Theme")
    multi_check = content.find("span", string="Themes")

    if multi_check and not single_check:
        theme_links = content_paragraphs[1].find_all("a")
        return [str(theme.string) for theme in theme_links if str(theme.string) != "Show All…"]
    
    elif single_check and not multi_check:
        theme_link = content_paragraphs[1].find("a")
        return [str(theme_link.string)]
    
    else:
        return None

def parse_nanogenres(soup: BeautifulSoup) -> List[str] | None:
    slug = parse_slug(soup)
    nano_soup = fetch_nanogenres(slug)
    
    content = nano_soup.find_all("section", class_="section genre-group")

    if content:
        nanogenres = []

        for nanogenre in content:
            label = nanogenre.find("span", class_="label")
            nanogenres.append(str(label.string))
        
        return nanogenres
    
    else:
        return None

def parse_avg_rating(soup: BeautifulSoup) -> float:
    data = _script_to_json(soup)

    return float(data["aggregateRating"]['ratingValue'])

def parse_total_logs(soup: BeautifulSoup) -> int:
    data = _script_to_json(soup)

    return int(data["aggregateRating"]['ratingCount'])