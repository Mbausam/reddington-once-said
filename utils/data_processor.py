"""
Data processing utilities — deduplication, cleaning, and sorting.

Since the Blacklist is a finished show, we collect once and keep forever.
Dedup is critical because the same quote appears on dozens of sites.
"""

import re
from difflib import SequenceMatcher


def _normalize_for_comparison(text: str) -> str:
    """Lowercase, strip punctuation, collapse spaces — for fuzzy matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Drop punctuation
    text = re.sub(r"\s+", " ", text)     # Collapse whitespace
    return text


def _similarity(a: str, b: str) -> float:
    """Quick similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(quotes: list[dict], threshold: float = 0.85) -> list[dict]:
    """
    Remove duplicate quotes using fuzzy matching.

    Quotes that are >85% similar (after normalization) are considered duplicates.
    When a duplicate is found, we keep the one with more metadata (season/episode info).

    Args:
        quotes: List of quote dicts.
        threshold: Similarity threshold (0.0–1.0). Higher = stricter matching.

    Returns:
        Deduplicated list of quote dicts.
    """
    if not quotes:
        return []

    # Sort by metadata richness so quotes with more info come first
    def _metadata_score(q):
        score = 0
        if q.get("season"):
            score += 2
        if q.get("episode"):
            score += 2
        if q.get("episode_title"):
            score += 1
        if q.get("context"):
            score += 1
        return score

    sorted_quotes = sorted(quotes, key=_metadata_score, reverse=True)

    unique = []
    normalized_cache = []  # Parallel list of normalized text for fast comparison

    for quote in sorted_quotes:
        norm = _normalize_for_comparison(quote["quote"])

        # Skip very short "quotes" that are likely artifacts
        if len(norm) < 10:
            continue

        is_dup = False
        for existing_norm in normalized_cache:
            # Quick length check before expensive similarity calc
            len_ratio = len(norm) / max(len(existing_norm), 1)
            if 0.5 < len_ratio < 2.0:
                if _similarity(norm, existing_norm) >= threshold:
                    is_dup = True
                    break

        if not is_dup:
            unique.append(quote)
            normalized_cache.append(norm)

    return unique


def clean_all(quotes: list[dict]) -> list[dict]:
    """
    Batch clean all quotes — remove empties, fix encoding, normalize.

    Returns:
        Cleaned list (may be shorter if some were invalid).
    """
    from scrapers.base_scraper import BaseScraper

    cleaned = []
    for q in quotes:
        q["quote"] = BaseScraper.clean_quote(q["quote"])
        if q["quote"] and len(q["quote"]) >= 10:
            cleaned.append(q)
    return cleaned


def sort_quotes(quotes: list[dict]) -> list[dict]:
    """
    Sort quotes by season > episode > alphabetical.
    Quotes without season/episode info go to the end.
    """
    def _sort_key(q):
        season = q.get("season") or 999
        episode = q.get("episode") or 999
        return (season, episode, q.get("quote", ""))

    return sorted(quotes, key=_sort_key)
