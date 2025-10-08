
# scrapxd: The Library for Letterboxd Data

[![PyPI Version](https://img.shields.io/pypi/v/scrapxd.svg)](https://pypi.org/project/scrapxd/)
[![Python Versions](https://img.shields.io/pypi/pyversions/scrapxd.svg)](https://pypi.org/project/scrapxd/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/cauafsantosdev/scrapxd)

`scrapxd` is a Python library designed for web scraping, analyzing, and exporting data from [Letterboxd](https://letterboxd.com/), the social network for cinephiles. With an intuitive, strictly-typed API using Pydantic, `scrapxd` makes it easy to access user profiles, film lists, diaries, and much more.

---

## Key Features

* **Scrape Whatever You Need:** Extract detailed data from user profiles, including watched films, ratings, diary entries, lists, followers, and more.
* **Film Search:** Search for films on Letterboxd based on various filters.
* **Pydantic Data Models:** All returned data is validated and structured into Pydantic models, ensuring consistency and ease of use in your code.
* **Analytics Module:** Perform statistical analysis on the collected data, such as correlations and trends (requires the `[analytics]` extra).
* **Exporting Module:** Export collected data to popular formats like CSV, JSON, and Excel (`.xlsx`) (requires the `[export]` extra).
* **Retries Logic:** Utilizes `tenacity` for automatic retries on network failures, making the scraping process more reliable.
* **Simple and Intuitive:** Designed with a clean and easy-to-use API, as demonstrated in the examples.

---

## Installation

You can install the library directly from PyPI.

**Standard Installation:**

**Bash**

```bash
pip install scrapxd
```

The library has optional dependencies for extra features. You can install them as needed:

**For Data Analytics:**

**Bash**

```
pip install "scrapxd[analytics]"
```

**For File Exporting:**

**Bash**

```
pip install "scrapxd[export]"
```

**To Install Everything (including testing dependencies):**

**Bash**

```
pip install "scrapxd[all]"
```

---

## Quickstart

Using `scrapxd` is very simple. Here is a basic example to get a user's watched films:

**Python**

```
from scrapxd import Scrapxd

# 1. Create a client instance
client = Scrapxd()

# 2. Get data for a Letterboxd user
# The client handles searching and pagination automatically
user = client.get_user("your_username_here")
user_films = user.logs

# 3. Access the data
print(f"Total films watched by '{user_films.username}': {user_films.number_of_entries}")

# Each entry is a Pydantic object with structured data
for entry in user_films.entries[:5]: # Displaying the first 5
    print(f"- {entry.film.title} ({entry.film.year}) - Rating: {entry.rating}")

# 4. (Optional) Export the data to an Excel file
try:
    user_films.to_xlsx(f"{user_films.username}_films")
    print(f"\nData exported to {user_films.username}_films.xlsx")
except ImportError:
    print("\nTo export data, please install with: pip install \"scrapxd[export]\"")
```



---

## Detailed Examples

For a more in-depth guide covering all features like profile analysis, comparisons, and advanced use cases, please explore the Jupyter notebooks in the `/examples` folder:

* **[1. Quickstart Guide](https://www.google.com/search?q=./examples/1_quickstart_guide.ipynb&authuser=2)**
* **[2. Deep Dive Analysis](https://www.google.com/search?q=./examples/2_deep_dive_analysis.ipynb&authuser=2)**
* **[3. Comparing Profiles](https://www.google.com/search?q=./examples/3_comparing_profiles.ipynb&authuser=2)**
* **[4. Advanced Guide](https://www.google.com/search?q=./examples/4_advanced_guide.ipynb&authuser=2)**

---

## Contributing

Contributions are very welcome! If you have an idea for a new feature, find a bug, or want to improve the documentation, please open an [Issue](https://github.com/cauafsantosdev/scrapxd/issues) or submit a [Pull Request](https://github.com/cauafsantosdev/scrapxd/pulls).

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=./LICENSE&authuser=2) file for more details.

---

## Contact

Cauã Santos - [My LinkedIn Profile](https://www.linkedin.com/in/cauafsantosdev/) - cauafsantosdev@gmail.com

GitHub URL: [https://github.com/cauafsantosdev/scrapxd](https://github.com/cauafsantosdev/scrapxd)
