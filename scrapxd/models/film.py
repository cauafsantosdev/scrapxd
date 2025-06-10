from pydantic import BaseModel
from typing import List, Dict


class Film(BaseModel):
    slug: str
    title: str
    year: int
    runtime: int
    director: str
    genres: List[str] = []
    nanogenres: List[str] = []
    themes: List[str] = []
    countries: List[str] = []
    languages: List[str] = []
    cast: List[str] = []
    crew: Dict[str, str] = []
    avg_rating: int
    total_logs: int

    def __str__(self):
        return f"{self.title} ({self.year})"