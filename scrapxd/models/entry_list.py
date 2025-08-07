from pydantic import BaseModel
from typing import List, Optional
from .entry import Entry


class EntryList(BaseModel):
    username: str
    title: str
    number_of_entries: int
    entries: List[Entry]

    def __str__(self):
        return f"{self.title} ({self.number_of_entries} {'reviews' if 'reviews' in self.title else 'entries'})"
    
    def __repr__(self):
        return f"{self.title} ({self.number_of_entries} {'reviews' if 'reviews' in self.title else 'entries'})"
    
    def get_films(self, limit: Optional[int] = None):
        if limit is None:
            limit = len(self.entries)

        for i in range(min(limit, len(self.films))):
            entry = self.entries[i]

            if isinstance(entry.film, str):
                entry.get_film_details()

        return self.entries
    
    def search_film(self, slug: str):
        for entry in self.entries:
            if isinstance(entry.film, str) and entry.film == slug:
                return entry
            elif entry.film.slug == slug:
                return entry
            
        return None