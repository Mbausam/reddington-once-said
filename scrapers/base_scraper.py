"""
Base scraper class — defines the interface and shared utilities for all quote collectors.

Every new source gets its own scraper class inheriting from BaseScraper.
This keeps things modular so we can plug in new sources easily,
and eventually expose collected data via an API.
"""

import re
import time
import random
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class BaseScraper:
    """
    Abstract base for all Reddington quote scrapers.

    Subclasses must implement `scrape()` which returns a list of quote dicts.

    Quote schema:
    {
        "quote": str,           # The actual quote text
        "season": int | None,   # Season number if known
        "episode": int | None,  # Episode number if known
        "episode_title": str,   # Episode title if known
        "context": str,         # Scene context / who he was talking to
        "source_url": str,      # URL the quote was scraped from
        "source_name": str,     # Human-readable source name
    }
    """

    # Rotate user agents to be polite and avoid blocks
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

    def _get_headers(self) -> dict:
        """Realistic browser headers to avoid being flagged as a bot."""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _polite_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Random delay between requests — be respectful to servers."""
        time.sleep(random.uniform(min_sec, max_sec))

    def _fetch_page(self, url: str) -> BeautifulSoup | None:
        """Fetch a page and return a BeautifulSoup object. Returns None on failure."""
        try:
            self._polite_delay()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"  [!] Failed to fetch {url}: {e}")
            return None

    @staticmethod
    def clean_quote(text: str) -> str:
        """Normalize a raw quote string."""
        if not text:
            return ""
        # Strip whitespace and common quote marks
        text = text.strip().strip('"').strip("'").strip("\u201c\u201d\u2018\u2019")
        # Collapse multiple spaces / newlines
        text = re.sub(r"\s+", " ", text)
        # Fix common encoding artifacts
        text = text.replace("\u2026", "...").replace("\u2014", " — ").replace("\u2013", " – ")
        return text.strip()

    def _make_quote(
        self,
        text: str,
        source_url: str,
        season: int | None = None,
        episode: int | None = None,
        episode_title: str = "",
        context: str = "",
    ) -> dict:
        """Build a standardized quote dict."""
        cleaned = self.clean_quote(text)
        if not cleaned or len(cleaned) < 10:
            return None  # Skip garbage / too-short strings

        return {
            "quote": cleaned,
            "season": season,
            "episode": episode,
            "episode_title": episode_title,
            "context": context,
            "source_url": source_url,
            "source_name": self.source_name,
        }

    @abstractmethod
    def scrape(self) -> list[dict]:
        """
        Run the scraper and return a list of quote dicts.
        Each subclass implements its own collection logic.
        """
        ...
