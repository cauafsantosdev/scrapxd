from datetime import date
from pydantic import BaseModel
from typing import Optional
from .film import Film


class Entry(BaseModel):
    film: Film | str
    watched_date: Optional[date] = None
    rating: Optional[float] = None
    review: Optional[str] = None

    def __str__(self):
        if self.watched_date and self.rating:
            return f"{self.watched_date}: {self.film} - {self.rating} stars"
        
        elif self.watched_date:
            return f"{self.watched_date}: {self.film}"
        
        elif self.rating:
            return f"{self.film} - {self.rating} stars"
        
        else:
            return f"{self.film}"
        
    def __repr__(self):
        if self.watched_date and self.rating:
            return f"{self.watched_date}: {self.film} - {self.rating} stars"
        
        elif self.watched_date:
            return f"{self.watched_date}: {self.film}"
        
        elif self.rating:
            return f"{self.film} - {self.rating} stars"
        
        else:
            return f"{self.film}"
        
    def get_film_details(self):
        from scrapxd.fetcher import fetch_film
        from scrapxd.parser.film import parse_film

        if isinstance(self.film, str):
            soup = fetch_film(self.film)
            film = parse_film(soup)
            self.film = film

        return self.film