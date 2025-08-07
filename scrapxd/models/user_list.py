from pydantic import BaseModel
from typing import List, Dict, Optional
from scrapxd.models.film import Film


class UserList(BaseModel):
    username: str
    title: str
    number_of_films: int
    films: List[Film | str] | Dict[int, Film | str]

    def __str__(self):
        return f"{self.title} ({self.number_of_films} films)"

    def __repr__(self):
        return f"{self.title} ({self.number_of_films} films)"

    def get_film(self, slug: str) -> Film | None:
        from scrapxd.fetcher import fetch_film
        from scrapxd.parser.film import parse_film

        if isinstance(self.films, list):
            try:
                idx = self.films.index(slug)
                soup = fetch_film(slug)
                film = parse_film(soup)
                self.films[idx] = film
                return film
            except ValueError:
                return None

        elif isinstance(self.films, dict):
            for key, value in self.films.items():
                if value == slug:
                    soup = fetch_film(slug)
                    film = parse_film(soup)
                    self.films[key] = film
                    return film
        
        return None

    def get_films(self, limit: Optional[int] = None):
        from scrapxd.fetcher import fetch_film
        from scrapxd.parser.film import parse_film

        if limit is None:
            limit = len(self.films)

        if isinstance(self.films, list):
            for i in range(min(limit, len(self.films))):
                slug = self.films[i]

                if isinstance(slug, Film):
                    continue
                else:
                    soup = fetch_film(slug)
                    film = parse_film(soup)
                    self.films[i] = film

        else:
            for i in range(1, min(limit, len(self.films)) + 1):
                slug = self.films[i]

                if isinstance(slug, Film):
                    continue
                else:
                    soup = fetch_film(slug)
                    film = parse_film(soup)
                    self.films[i] = film

        return self.films