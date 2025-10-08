"""
Defines ScraperBase, the base model for all scraper classes in Scrapxd.

Provides common utility methods for HTML parsing, logging, and caching,
including safe wrappers for BeautifulSoup's find/find_all and a generic
cached soup fetcher.
"""
import logging
from typing import Optional
from bs4 import BeautifulSoup
from pydantic import BaseModel
from functools import lru_cache

from ..fetcher import Fetcher, fetcher as default_fetcher

# Get a logger instance for this module
log = logging.getLogger(__name__)

class ScraperBase(BaseModel):
    """
    A base model for all scraper classes, providing common utility methods.
    """
    fetcher: Fetcher = default_fetcher

    model_config = {
        "arbitrary_types_allowed": True
    }

    def _safe_find(self, element, *args, **kwargs):
        """A wrapper for the .find() method that logs a warning if the element is not found."""
        found_element = element.find(*args, **kwargs)

        if not found_element:
            log.warning(f"Could not find element with args: {args}, kwargs: {kwargs}")

        return found_element
    
    def _safe_find_all(self, element, *args, **kwargs):
        """A wrapper for the .find_all() method that logs a warning if the element is not found."""
        found_elements = element.find_all(*args, **kwargs)

        if not found_elements:
            log.warning(f"Could not find any element with args: {args}, kwargs: {kwargs}")
        else:    
            log.info(f"Found {len(found_elements)} elements with args: {args}, kwargs: {kwargs} successfuly")

        return found_elements

    @lru_cache(maxsize=128)
    def _get_soup(self, fetch_function, *args) -> Optional[BeautifulSoup]:
        """
        Generic helper to fetch and cache soup objects using a specific fetcher function.
        The cache is keyed by the function and its arguments.
        """
        func_name = fetch_function.__name__
        log.debug(f"Requesting page using '{func_name}' with args {args}")
        
        soup = fetch_function(*args)

        if soup:
            log.debug(f"Soup for '{func_name}' fetched successfully.")
        else:
            log.warning(f"Failed to fetch soup for '{func_name}' with args {args}.")
            
        return soup