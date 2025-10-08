"""
Defines constants and configuration values for Scrapxd, including base URLs,
supported genres, decades, months, and weekdays for use in scraping and analytics.
"""

# The base URL for Letterboxd
BASE_URL = "https://letterboxd.com/"
# The base URL for individual film pages
FILM_URL = "https://letterboxd.com/film/"

# List of supported film genres on Letterboxd
GENRES = ["action", "adventure", "animation", "comedy", "crime",
        "documentary", "drama", "family", "fantasy", "history",
        "horror", "music", "mystery", "romance", "science-fiction",
        "thriller", "tv-movie", "war", "western"]

# List of decades for filtering films by release period
DECADES = ["1880s", "1890s", "1900s", "1910s", "1920s",
            "1930s", "1940s", "1950s", "1960s", "1970s",
            "1980s", "1990s", "2000s", "2010s", "2020s"]

# Mapping of month numbers to month names
MONTHS = {1: "January", 2: "February", 3: "March", 4: "April",
          5: "May", 6: "June", 7: "July", 8: "August",
          9: "September", 10: "October", 11: "November", 12: "December"}

# List of weekday names
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]