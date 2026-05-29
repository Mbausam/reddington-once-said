"""
Bulk transcript downloader — fetches ALL episode transcripts from Springfield
and caches them locally for the Claude miner to process.

Resumable: skips already-downloaded files so interrupted runs pick up where they left off.
"""

import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "transcripts")
META_FILE = os.path.join(CACHE_DIR, "_episodes.json")

BASE_URL = "https://www.springfieldspringfield.co.uk"
SHOW_SLUG = "the-blacklist"

SEASON_EPISODES = {
    1: 22, 2: 22, 3: 23, 4: 22, 5: 22,
    6: 22, 7: 19, 8: 22, 9: 22, 10: 22,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _episode_url(season: int, episode: int) -> str:
    return (
        f"{BASE_URL}/view_episode_scripts.php"
        f"?tv-show={SHOW_SLUG}&episode=s{season:02d}e{episode:02d}"
    )


def _fetch_transcript_text(url: str, session: requests.Session) -> str | None:
    """Fetch a transcript page and extract the raw text."""
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        script_div = soup.find("div", class_="scrolling-script-container")
        if script_div:
            return script_div.get_text("\n", strip=False)
        return None
    except requests.RequestException as e:
        print(f"    [!] HTTP error: {e}")
        return None


def _try_fetch_episode_list(session: requests.Session) -> dict[tuple[int, int], str]:
    """Try to get episode titles from the listing page. Returns {(season, ep): title}."""
    titles = {}
    list_url = f"{BASE_URL}/episode_scripts.php?tv-show={SHOW_SLUG}"
    try:
        resp = session.get(list_url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            m = re.search(r"episode=s(\d+)e(\d+)", href)
            if m:
                s, e = int(m.group(1)), int(m.group(2))
                title = re.sub(r"^\d+\.\s*", "", link.get_text(strip=True))
                titles[(s, e)] = title
    except Exception:
        pass
    return titles


def download_all(seasons: list[int] | None = None, delay: float = 1.5) -> int:
    """
    Download all episode transcripts to cache/transcripts/.

    Args:
        seasons: Which seasons to download. Defaults to all 10.
        delay: Seconds between requests (be polite).

    Returns:
        Number of transcripts downloaded (not counting already-cached).
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    seasons = seasons or list(range(1, 11))

    session = requests.Session()
    session.headers.update(HEADERS)

    # Try to get episode titles
    print("Fetching episode list for titles...")
    titles = _try_fetch_episode_list(session)
    print(f"   Found {len(titles)} episode titles")

    # Build the full episode manifest
    all_episodes = []
    for season in seasons:
        ep_count = SEASON_EPISODES.get(season, 22)
        for ep in range(1, ep_count + 1):
            all_episodes.append({
                "season": season,
                "episode": ep,
                "title": titles.get((season, ep), ""),
                "url": _episode_url(season, ep),
                "filename": f"s{season:02d}e{ep:02d}.txt",
            })

    # Save manifest
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(all_episodes, f, indent=2)

    total = len(all_episodes)
    downloaded = 0
    skipped = 0
    failed = 0

    print(f"\n>> Downloading {total} transcripts to {CACHE_DIR}/")
    print(f"   Seasons: {seasons}")
    print(f"   Delay: {delay}s between requests\n")

    for i, ep in enumerate(all_episodes, 1):
        filepath = os.path.join(CACHE_DIR, ep["filename"])
        label = f"S{ep['season']:02d}E{ep['episode']:02d}"
        title_str = f" — {ep['title']}" if ep["title"] else ""

        # Skip if already cached
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            skipped += 1
            if skipped % 20 == 0:
                print(f"   [{i}/{total}] [skip]  {label}{title_str} (cached, skipping)")
            continue

        print(f"   [{i}/{total}] [dl] {label}{title_str} ...", end=" ", flush=True)

        text = _fetch_transcript_text(ep["url"], session)
        if text and len(text) > 100:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            downloaded += 1
            print(f"OK {len(text):,} chars")
        else:
            failed += 1
            print(f"FAIL empty or too short")

        # Polite delay (slightly randomized)
        time.sleep(delay * (0.8 + 0.4 * (i % 3 == 0)))

    print(f"\n{'='*50}")
    print(f"[stats] Done! Downloaded: {downloaded} | Skipped (cached): {skipped} | Failed: {failed}")
    print(f"[dir] Transcripts: {CACHE_DIR}/")

    return downloaded


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download all Blacklist transcripts from Springfield")
    parser.add_argument("--seasons", nargs="+", type=int, default=None,
                        help="Seasons to download (default: all 1-10)")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Delay between requests in seconds")
    args = parser.parse_args()
    download_all(seasons=args.seasons, delay=args.delay)
