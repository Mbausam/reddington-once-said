"""
TranscriptScraper — scrapes episode transcripts and extracts Reddington's lines.

Uses Selenium for JS-heavy sites (like SubsLikeScript) and BeautifulSoup
for static transcript sites (like Springfield Springfield).

Since transcript sites are subtitle-based (no character names), we use
keyword patterns to attempt identification where possible, and fall back
to collecting full transcripts for manual curation later.
"""

import re
import time

from scrapers.base_scraper import BaseScraper

# Selenium imports — fail gracefully if not installed
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class TranscriptScraper(BaseScraper):
    """
    Scrapes episode transcripts from Springfield Springfield.

    This site has all 10 seasons of The Blacklist transcripts
    in a simple static HTML format — no JS needed, just requests + BS4.

    URL pattern:
        https://www.springfieldspringfield.co.uk/view_episode_scripts.php?tv-show=the-blacklist&episode=s{SS}e{EE}
    """

    BASE_URL = "https://www.springfieldspringfield.co.uk"
    SHOW_SLUG = "the-blacklist"
    EPISODES_URL = f"{BASE_URL}/episode_scripts.php?tv-show={SHOW_SLUG}"

    # Patterns that suggest Reddington is speaking
    # In transcripts, his lines sometimes start with these
    REDDINGTON_PATTERNS = [
        r"(?:^|\n)\s*(?:Red|Reddington|Raymond|Mr\.?\s*Reddington)\s*[:]\s*(.*?)(?:\n|$)",
    ]

    # Episode count per season (The Blacklist)
    SEASON_EPISODES = {
        1: 22, 2: 22, 3: 23, 4: 22, 5: 22,
        6: 22, 7: 19, 8: 22, 9: 22, 10: 22,
    }

    def __init__(self, seasons: list[int] | None = None):
        """
        Args:
            seasons: List of season numbers to scrape. Defaults to all 10.
        """
        super().__init__(source_name="SpringfieldTranscripts")
        self.seasons = seasons or list(range(1, 11))

    def _episode_url(self, season: int, episode: int) -> str:
        """Build the transcript URL for a specific episode."""
        return (
            f"{self.BASE_URL}/view_episode_scripts.php"
            f"?tv-show={self.SHOW_SLUG}"
            f"&episode=s{season:02d}e{episode:02d}"
        )

    def _get_episode_list(self) -> list[dict]:
        """
        Fetch the main episode list page and extract all episode links
        with their titles, seasons, and episode numbers.
        """
        print(f"\n  📋 Fetching episode list from Springfield...")
        soup = self._fetch_page(self.EPISODES_URL)
        if soup is None:
            return []

        episodes = []

        # Springfield has episode links in a specific pattern
        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            if "view_episode_scripts.php" not in href or self.SHOW_SLUG not in href:
                continue

            # Parse season and episode from the URL
            match = re.search(r"episode=s(\d+)e(\d+)", href)
            if match:
                season = int(match.group(1))
                episode = int(match.group(2))

                if season not in self.seasons:
                    continue

                title = link.get_text(strip=True)
                # Remove the leading number and period (e.g. "1. Pilot" -> "Pilot")
                title = re.sub(r"^\d+\.\s*", "", title)

                episodes.append({
                    "season": season,
                    "episode": episode,
                    "title": title,
                    "url": f"{self.BASE_URL}/{href}" if not href.startswith("http") else href,
                })

        print(f"  ✅ Found {len(episodes)} episodes across seasons {self.seasons}")
        return episodes

    def _extract_transcript(self, soup) -> str:
        """Extract the transcript text from a Springfield episode page."""
        # Springfield puts the script in a div with class "scrolling-script-container"
        # or inside the main content area
        script_div = soup.find("div", class_="scrolling-script-container")
        if script_div:
            return script_div.get_text("\n", strip=False)

        # Fallback: try the main script content div
        script_div = soup.find("div", class_="movie_script")
        if script_div:
            return script_div.get_text("\n", strip=False)

        return ""

    def _find_reddington_lines(
        self, transcript: str, season: int, episode: int, episode_title: str, url: str
    ) -> list[dict]:
        """
        Attempt to extract Reddington's lines from a transcript.

        Since subtitle transcripts don't always attribute dialogue to characters,
        we look for patterns where Reddington is addressed or speaking.
        """
        quotes = []

        for pattern in self.REDDINGTON_PATTERNS:
            matches = re.findall(pattern, transcript, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                text = match.strip()
                if len(text) < 15:
                    continue

                quote = self._make_quote(
                    text=text,
                    source_url=url,
                    season=season,
                    episode=episode,
                    episode_title=episode_title,
                    context="From episode transcript",
                )
                if quote:
                    quotes.append(quote)

        return quotes

    def scrape(self) -> list[dict]:
        """
        Scrape transcripts for all configured seasons.

        Returns quotes found with Reddington attribution in transcripts.
        """
        all_quotes = []
        episodes = self._get_episode_list()

        if not episodes:
            print("  [!] No episodes found. Falling back to manual URL construction.")
            # Build episode list manually
            for season in self.seasons:
                ep_count = self.SEASON_EPISODES.get(season, 22)
                for ep in range(1, ep_count + 1):
                    episodes.append({
                        "season": season,
                        "episode": ep,
                        "title": "",
                        "url": self._episode_url(season, ep),
                    })

        total = len(episodes)
        for i, ep in enumerate(episodes, 1):
            print(
                f"  📺 [{i}/{total}] S{ep['season']:02d}E{ep['episode']:02d} "
                f"- {ep['title'] or 'Unknown'}"
            )

            soup = self._fetch_page(ep["url"])
            if soup is None:
                continue

            transcript = self._extract_transcript(soup)
            if not transcript:
                print(f"     [!] No transcript found")
                continue

            quotes = self._find_reddington_lines(
                transcript=transcript,
                season=ep["season"],
                episode=ep["episode"],
                episode_title=ep["title"],
                url=ep["url"],
            )

            if quotes:
                print(f"     ✅ Found {len(quotes)} Reddington lines")
                all_quotes.extend(quotes)
            else:
                print(f"     ℹ️  No attributed Reddington lines found (subtitle format)")

        return all_quotes


class SeleniumTranscriptScraper(BaseScraper):
    """
    Alternative scraper using Selenium for JS-rendered transcript pages.

    Useful for sites like SubsLikeScript that require JavaScript.
    Falls back gracefully if Selenium isn't installed.
    """

    def __init__(self):
        super().__init__(source_name="SeleniumTranscripts")
        self.driver = None

    def _init_driver(self):
        """Initialize headless Chrome via webdriver-manager."""
        if not SELENIUM_AVAILABLE:
            print("  [!] Selenium not installed. Run: pip install selenium webdriver-manager")
            return False

        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={self.USER_AGENTS[0]}")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            return True
        except Exception as e:
            print(f"  [!] Failed to initialize Chrome driver: {e}")
            return False

    def _close_driver(self):
        """Clean up the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape(self) -> list[dict]:
        """
        Scrape SubsLikeScript using Selenium.

        This is a secondary source — the static TranscriptScraper should
        be used first as it's faster and more reliable.
        """
        if not self._init_driver():
            return []

        all_quotes = []

        try:
            base_url = "https://subslikescript.com/series/The_Blacklist-2741602"
            print(f"\n  🌐 Loading SubsLikeScript with Selenium...")

            self.driver.get(base_url)
            time.sleep(3)

            # Find all episode links
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='season-']")
            episode_urls = []

            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and "episode-" in href:
                    # Parse season and episode
                    match = re.search(r"season-(\d+)/episode-(\d+)", href)
                    if match:
                        episode_urls.append({
                            "url": href,
                            "season": int(match.group(1)),
                            "episode": int(match.group(2)),
                            "title": text,
                        })

            print(f"  ✅ Found {len(episode_urls)} episodes")

            # Limit to first season for now to avoid hammering the server
            episode_urls = [ep for ep in episode_urls if ep["season"] <= 1]
            print(f"  ℹ️  Processing Season 1 only ({len(episode_urls)} episodes)")

            for i, ep in enumerate(episode_urls, 1):
                print(f"  📺 [{i}/{len(episode_urls)}] S{ep['season']:02d}E{ep['episode']:02d}")

                try:
                    self.driver.get(ep["url"])
                    time.sleep(2)

                    # Look for the transcript content
                    try:
                        transcript_el = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".full-script")
                            )
                        )
                        transcript = transcript_el.text
                    except Exception:
                        print(f"     [!] Could not find transcript element")
                        continue

                    if transcript:
                        # Same Reddington line detection as TranscriptScraper
                        for pattern in TranscriptScraper.REDDINGTON_PATTERNS:
                            matches = re.findall(
                                pattern, transcript, re.IGNORECASE | re.MULTILINE
                            )
                            for match in matches:
                                quote = self._make_quote(
                                    text=match.strip(),
                                    source_url=ep["url"],
                                    season=ep["season"],
                                    episode=ep["episode"],
                                    episode_title=ep["title"],
                                    context="From SubsLikeScript transcript",
                                )
                                if quote:
                                    all_quotes.append(quote)

                except Exception as e:
                    print(f"     [!] Error: {e}")
                    continue

                self._polite_delay(2.0, 4.0)

        finally:
            self._close_driver()

        return all_quotes
