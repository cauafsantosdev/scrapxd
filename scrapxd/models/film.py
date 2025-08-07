from pydantic import BaseModel
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class Film(BaseModel):
    slug: str
    id: int
    title: str
    year: int
    runtime: int
    director: List[str]

    _genre: Optional[List[str]] = None
    _nanogenres: Optional[List[str]] = None
    _themes: Optional[List[str]] = None
    _country: Optional[List[str]] = None
    _language: Optional[List[str]] = None
    _cast: Optional[Dict[str, str]] = None
    _crew: Optional[Dict[str, str | List[str]]] = None
    _studio: Optional[List[str]] = None
    _avg_rating: Optional[float] = None
    _total_logs: Optional[int] = None

    _soup: Optional[BeautifulSoup] = None
    _nano_soup: Optional[BeautifulSoup] = None

    def __str__(self):
        return f"{self.title} ({self.year})"
    
    def __repr__(self):
        return f"{self.title} ({self.year})"
    
    def __get_soup(self) -> BeautifulSoup:       
        from scrapxd.fetcher import fetch_film

        if self._soup is None:
            self._soup = fetch_film(self.slug)
        
        return self._soup
    
    def __get_nano_soup(self) -> BeautifulSoup:    
        from scrapxd.fetcher import fetch_nanogenres

        if self._nano_soup is None:
            self._nano_soup = fetch_nanogenres(self.slug)
        
        return self._nano_soup
    
    @property
    def genre(self) -> List[str]:
        import scrapxd.parser.film as p
        
        if self._genre is None:
            self._genre = p.parse_genre(self.__get_soup())
        return self._genre

    @property
    def nanogenres(self) -> List[str] | None:
        import scrapxd.parser.film as p
        
        if self._nanogenres is None:
            self._nanogenres = p.parse_nanogenres(self.__get_nano_soup())
        return self._nanogenres

    @property
    def themes(self) -> List[str] | None:
        import scrapxd.parser.film as p
        
        if self._themes is None:
            self._themes = p.parse_themes(self.__get_soup())
        return self._themes

    @property
    def country(self) -> List[str]:
        import scrapxd.parser.film as p
        
        if self._country is None:
            self._country = p.parse_country(self.__get_soup())
        return self._country

    @property
    def language(self) -> List[str]:
        import scrapxd.parser.film as p
        
        if self._language is None:
            self._language = p.parse_language(self.__get_soup())
        return self._language

    @property
    def cast(self) -> Dict[str, str]:
        import scrapxd.parser.film as p
        
        if self._cast is None:
            self._cast = p.parse_cast(self.__get_soup())
        return self._cast

    @property
    def crew(self) -> Dict[str, str | List[str]]:
        import scrapxd.parser.film as p
        
        if self._crew is None:
            self._crew = p.parse_crew(self.__get_soup())
        return self._crew

    @property
    def studio(self) -> List[str]:
        import scrapxd.parser.film as p
        
        if self._studio is None:
            self._studio = p.parse_studio(self.__get_soup())
        return self._studio

    @property
    def avg_rating(self) -> float:
        import scrapxd.parser.film as p
        
        if self._avg_rating is None:
            self._avg_rating = p.parse_avg_rating(self.__get_soup())
        return self._avg_rating

    @property
    def total_logs(self) -> int:
        import scrapxd.parser.film as p
        
        if self._total_logs is None:
            self._total_logs = p.parse_total_logs(self.__get_soup())
        return self._total_logs