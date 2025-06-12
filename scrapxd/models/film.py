from pydantic import BaseModel
from typing import List, Dict


class Film(BaseModel):
    slug: str
    id: int
    title: str
    year: int
    runtime: int
    director: List[str]
    genre: List[str] = []
    nanogenres: List[str] | None = None
    themes: List[str] | None = None
    country: List[str] = []
    language: List[str] = []
    cast: Dict[str, str] = []
    crew: Dict[str, List[str]] = []
    studio: List[str] = None
    avg_rating: float
    total_logs: int

    def __str__(self):
        return f"{self.title} ({self.year})"