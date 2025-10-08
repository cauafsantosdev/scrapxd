"""
Defines the Entry model, representing a single film entry (log, review, diary entry)
scraped from Letterboxd.

Includes metadata such as username, watched date, rating, and review.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

from .film import Film


class Entry(BaseModel):
    """
    Represents a single film entry scraped from Letterboxd, including metadata
    such as username, watched date, rating, and review.
    """
    film: Film
    username: Optional[str] = None
    watched_date: Optional[date] = None
    rating: Optional[float] = None
    review: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        """
        Returns a human-readable string representation of the entry,
        including watched date, film slug, and rating if available.
        """
        parts = []

        if self.watched_date:
            parts.append(f"{self.watched_date}:")
            
        parts.append(self.film.slug)
        
        if self.rating:
            return f"- {self.rating} stars"
        
        return " ".join(parts)
        
    def __repr__(self):
        """
        Returns a formal string representation of the Entry object for debugging,
        showing all attributes including optional ones.
        """
        return (
            f"Entry(film={repr(self.film)}, "
            f"username={repr(self.username)}, "
            f"watched_date={repr(self.watched_date)}, "
            f"rating={repr(self.rating)}, "
            f"review={repr(self.review)})"
        )