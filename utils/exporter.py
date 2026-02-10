"""
Export utilities — write collected quotes to JSON and CSV files.
Also generates basic stats about the collection.
"""

import json
import csv
import os
from datetime import datetime


def export_json(quotes: list[dict], filepath: str) -> str:
    """
    Export quotes to a pretty-printed JSON file.

    Returns the absolute filepath written.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    output = {
        "metadata": {
            "project": "ReddingtonOnceSaid",
            "description": "Raymond 'Red' Reddington Quote Compendium — The Blacklist",
            "total_quotes": len(quotes),
            "last_updated": datetime.now().isoformat(),
        },
        "quotes": quotes,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return os.path.abspath(filepath)


def export_csv(quotes: list[dict], filepath: str) -> str:
    """
    Export quotes to a CSV file with headers.

    Returns the absolute filepath written.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    fieldnames = ["quote", "season", "episode", "episode_title", "context", "source_url", "source_name"]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for q in quotes:
            writer.writerow(q)

    return os.path.abspath(filepath)


def generate_stats(quotes: list[dict]) -> dict:
    """
    Generate summary statistics about the quote collection.

    Returns a dict with various stats.
    """
    stats = {
        "total_quotes": len(quotes),
        "quotes_with_season": sum(1 for q in quotes if q.get("season")),
        "quotes_with_episode": sum(1 for q in quotes if q.get("episode")),
        "quotes_with_context": sum(1 for q in quotes if q.get("context")),
        "sources": {},
        "seasons": {},
    }

    # Count per source
    for q in quotes:
        src = q.get("source_name", "Unknown")
        stats["sources"][src] = stats["sources"].get(src, 0) + 1

    # Count per season
    for q in quotes:
        s = q.get("season")
        if s:
            key = f"Season {s}"
            stats["seasons"][key] = stats["seasons"].get(key, 0) + 1

    # Average quote length
    if quotes:
        lengths = [len(q["quote"]) for q in quotes]
        stats["avg_quote_length"] = round(sum(lengths) / len(lengths))
        stats["shortest_quote"] = min(lengths)
        stats["longest_quote"] = max(lengths)

    return stats


def print_stats(stats: dict):
    """Pretty-print collection stats to console."""
    print("\n" + "=" * 60)
    print("  📊 REDDINGTON QUOTE COMPENDIUM — STATS")
    print("=" * 60)
    print(f"  Total quotes collected:  {stats['total_quotes']}")
    print(f"  With season info:        {stats['quotes_with_season']}")
    print(f"  With episode info:       {stats['quotes_with_episode']}")
    print(f"  With context:            {stats['quotes_with_context']}")

    if stats.get("avg_quote_length"):
        print(f"  Avg quote length:        {stats['avg_quote_length']} chars")
        print(f"  Shortest:                {stats['shortest_quote']} chars")
        print(f"  Longest:                 {stats['longest_quote']} chars")

    if stats.get("sources"):
        print("\n  📡 Quotes per source:")
        for src, count in sorted(stats["sources"].items(), key=lambda x: -x[1]):
            print(f"     {src:30s}  {count}")

    if stats.get("seasons"):
        print("\n  📺 Quotes per season:")
        for season, count in sorted(stats["seasons"].items()):
            print(f"     {season:30s}  {count}")

    print("=" * 60 + "\n")
