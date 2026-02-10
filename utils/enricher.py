"""
Quote Enricher — Cross-references quotes against episode transcripts
to discover which season/episode each quote came from.

This is the key to making our dataset useful for a future webapp
where users can filter by season, browse quotes per episode, etc.

Strategy:
1. Download all episode transcripts from Springfield
2. For each untagged quote, fuzzy-search through all transcripts
3. When a match is found, tag the quote with season/episode/title
"""

import os
import re
import json
import time
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup


class QuoteEnricher:
    """
    Cross-references collected quotes against episode transcripts
    to find season/episode information.
    """

    BASE_URL = "https://www.springfieldspringfield.co.uk"
    SHOW_SLUG = "the-blacklist"
    EPISODES_URL = f"{BASE_URL}/episode_scripts.php?tv-show={SHOW_SLUG}"

    # Episode count per season
    SEASON_EPISODES = {
        1: 22, 2: 22, 3: 23, 4: 22, 5: 22,
        6: 22, 7: 19, 8: 22, 9: 22, 10: 22,
    }

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    def __init__(self, cache_dir: str = "cache/transcripts"):
        """
        Args:
            cache_dir: Directory to cache downloaded transcripts so we
                       don't re-download them on every run.
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _cache_path(self, season: int, episode: int) -> str:
        """Get the cache file path for a transcript."""
        return os.path.join(self.cache_dir, f"s{season:02d}e{episode:02d}.txt")

    def _episode_url(self, season: int, episode: int) -> str:
        """Build the Springfield transcript URL."""
        return (
            f"{self.BASE_URL}/view_episode_scripts.php"
            f"?tv-show={self.SHOW_SLUG}"
            f"&episode=s{season:02d}e{episode:02d}"
        )

    def _fetch_and_cache_transcript(self, season: int, episode: int) -> str:
        """
        Download a transcript from Springfield and cache it locally.
        Returns the transcript text, or empty string on failure.
        """
        cache_file = self._cache_path(season, episode)

        # Check cache first
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()

        # Download
        url = self._episode_url(season, episode)
        try:
            time.sleep(1.5)  # Be polite
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"    [!] Failed to fetch S{season:02d}E{episode:02d}: {e}")
            return ""

        soup = BeautifulSoup(response.text, "lxml")

        # Extract transcript text
        script_div = soup.find("div", class_="scrolling-script-container")
        if not script_div:
            script_div = soup.find("div", class_="movie_script")
        if not script_div:
            return ""

        transcript = script_div.get_text("\n", strip=False)

        # Extract episode title from the page
        title = ""
        title_tag = soup.find("h1")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Format: "The Blacklist s01e01 Episode Script" or similar
            title = title_text

        # Cache it
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        return transcript

    def _get_episode_titles(self) -> dict:
        """Fetch episode titles from the episode list page."""
        titles = {}
        try:
            response = self.session.get(self.EPISODES_URL, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                match = re.search(r"episode=s(\d+)e(\d+)", href)
                if match:
                    s, e = int(match.group(1)), int(match.group(2))
                    title = link.get_text(strip=True)
                    title = re.sub(r"^\d+\.\s*", "", title)  # Remove "1. "
                    titles[(s, e)] = title
        except Exception as e:
            print(f"  [!] Could not fetch episode titles: {e}")

        return titles

    def _normalize(self, text: str) -> str:
        """Normalize text for fuzzy matching."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _find_in_transcript(self, quote: str, norm_transcript: str) -> bool:
        """
        Check if a quote appears in a transcript.

        FAST approach (no sliding window):
        1. Exact normalized substring match
        2. Key-phrase check — extract distinctive multi-word phrases
           from the quote and check if they appear in the transcript
        3. For short quotes, require full exact match only
        """
        norm_quote = self._normalize(quote)

        # Tier 1: Exact substring (instant)
        if norm_quote in norm_transcript:
            return True

        quote_words = norm_quote.split()

        # Short quotes (≤5 words): require exact match only — too risky otherwise
        if len(quote_words) <= 5:
            return False

        # Tier 2: Key-phrase extraction
        # Take distinctive 4-6 word chunks from the quote and check
        # if they appear in the transcript. If 2+ chunks match, it's a hit.
        chunk_size = min(5, len(quote_words) - 1)
        chunks = []
        for i in range(0, len(quote_words) - chunk_size + 1, 3):
            chunk = " ".join(quote_words[i:i + chunk_size])
            chunks.append(chunk)

        if not chunks:
            return False

        matches = sum(1 for chunk in chunks if chunk in norm_transcript)
        # Need at least 2 matching chunks, or 1 if it's a big chunk
        min_matches = 2 if len(chunks) >= 3 else 1
        return matches >= min_matches

    def _load_all_transcripts(self, seasons: list[int]) -> dict:
        """Pre-load and pre-normalize all transcripts into memory."""
        print("  📖 Loading transcripts into memory...")
        transcripts = {}
        for season in seasons:
            ep_count = self.SEASON_EPISODES.get(season, 22)
            for episode in range(1, ep_count + 1):
                cache_file = self._cache_path(season, episode)
                if not os.path.exists(cache_file):
                    continue
                with open(cache_file, "r", encoding="utf-8") as f:
                    raw = f.read()
                transcripts[(season, episode)] = self._normalize(raw)
        print(f"  ✅ Loaded {len(transcripts)} transcripts")
        return transcripts

    def download_transcripts(self, seasons: list[int] | None = None):
        """
        Download and cache all transcripts for the specified seasons.

        Args:
            seasons: List of season numbers. Defaults to all 10.
        """
        seasons = seasons or list(range(1, 11))

        print("\n  📥 Downloading transcripts...")
        total = sum(self.SEASON_EPISODES.get(s, 22) for s in seasons)
        downloaded = 0
        cached = 0

        for season in seasons:
            ep_count = self.SEASON_EPISODES.get(season, 22)
            for episode in range(1, ep_count + 1):
                cache_file = self._cache_path(season, episode)

                if os.path.exists(cache_file):
                    cached += 1
                    continue

                print(f"    📺 Downloading S{season:02d}E{episode:02d}...", end=" ", flush=True)
                transcript = self._fetch_and_cache_transcript(season, episode)
                if transcript:
                    print(f"✅ ({len(transcript)} chars)")
                    downloaded += 1
                else:
                    print("❌")

        print(f"\n  📊 Transcripts: {downloaded} downloaded, {cached} from cache, {total} total")

    def enrich_quotes(
        self,
        quotes: list[dict],
        seasons: list[int] | None = None,
    ) -> list[dict]:
        """
        Cross-reference quotes against transcripts to find season/episode.

        Pre-loads all transcripts and pre-normalizes them for speed.
        """
        seasons = seasons or list(range(1, 11))

        # Get episode titles
        print("\n  📋 Fetching episode titles...")
        titles = self._get_episode_titles()

        # Pre-load all transcripts (fast — from cache)
        transcripts = self._load_all_transcripts(seasons)

        # Filter to untagged quotes only
        untagged = [q for q in quotes if q.get("season") is None]
        if not untagged:
            print("  ✅ All quotes already have season info!")
            return quotes

        print(f"  🔍 Cross-referencing {len(untagged)} untagged quotes against {len(transcripts)} transcripts...")

        enriched_count = 0

        for qi, quote_data in enumerate(untagged, 1):
            quote_text = quote_data["quote"]
            short_display = quote_text[:60] + "..." if len(quote_text) > 60 else quote_text
            print(f"    [{qi}/{len(untagged)}] \"{short_display}\"", end=" ", flush=True)

            found = False
            for (season, episode), norm_transcript in transcripts.items():
                if self._find_in_transcript(quote_text, norm_transcript):
                    title = titles.get((season, episode), "")
                    quote_data["season"] = season
                    quote_data["episode"] = episode
                    quote_data["episode_title"] = title
                    print(f"✅ S{season:02d}E{episode:02d} — {title}")
                    enriched_count += 1
                    found = True
                    break

            if not found:
                print("❌")

        print(f"\n  📊 Enriched {enriched_count}/{len(untagged)} quotes with season/episode info")
        return quotes


def enrich_from_file(
    json_path: str,
    seasons: list[int] | None = None,
    download_first: bool = True,
) -> list[dict]:
    """
    Convenience function: load quotes from JSON, enrich them, and save back.

    Args:
        json_path: Path to the reddington_quotes.json file.
        seasons: Seasons to process.
        download_first: Whether to download transcripts before enriching.

    Returns:
        The enriched quotes list.
    """
    from utils.exporter import export_json, export_csv, generate_stats, print_stats

    # Load existing quotes
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    quotes = data.get("quotes", [])

    print(f"\n  📂 Loaded {len(quotes)} quotes from {json_path}")

    # Create enricher
    enricher = QuoteEnricher()

    # Download transcripts if needed
    if download_first:
        enricher.download_transcripts(seasons)

    # Enrich
    quotes = enricher.enrich_quotes(quotes, seasons)

    # Save back
    csv_path = json_path.replace(".json", ".csv")
    export_json(quotes, json_path)
    export_csv(quotes, csv_path)

    # Print updated stats
    stats = generate_stats(quotes)
    print_stats(stats)

    return quotes
