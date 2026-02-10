"""
WikiquoteScraper — collects Reddington quotes from Wikiquote.

Parses the hierarchical structure of Wikiquote pages to extract quotes
often organized by Season/Episode.
"""

import re
from scrapers.base_scraper import BaseScraper


class WikiquoteScraper(BaseScraper):
    """
    Scrapes The Blacklist quotes from Wikiquote.
    """

    URL = "https://en.wikiquote.org/wiki/The_Blacklist"

    def __init__(self):
        super().__init__(source_name="Wikiquote")

    def scrape(self) -> list[dict]:
        """Scrape Wikiquote page."""
        print(f"\n  🔍 Scraping: {self.source_name} ({self.URL})")
        soup = self._fetch_page(self.URL)
        if soup is None:
            return []

        quotes = []
        
        # Wikiquote usually structures TV shows by Season headers (h2 or h3)
        # and lists quotes in <ul> or <dl> tags.
        
        # Strategy: Iterate through all elements, keeping track of the current Season/Episode context
        
        # Find all headlines to identify sections
        # Then look for lists following them
        
        # Simplified approach: Look for definition lists (<dl>) which often contain the dialogue
        # or unordered lists (<ul>) for standalone quotes.
        
        # Identify dialogue lines starting with "Red:" or "Reddington:"
        
        main_content = soup.find("div", {"id": "mw-content-text"})
        if not main_content:
            return []

        # Regex to catch Red speaking
        # Matches: "Red: ...", "Reddington: ...", "**Raymond:** ..."
        speaker_pattern = re.compile(r"^(?:Raymond\s+)?(?:Red|Reddington)\s*:", re.IGNORECASE)

        # Iterate over all text-containing elements to find dialogue
        # This catch-all approach is better for the messy Wikiquote format
        
        # Try to parse by season sections if possible
        current_season = None
        current_episode = None
        
        # Get all relevant tags in order
        tags = main_content.find_all(['h2', 'h3', 'h4', 'dl', 'ul', 'p'])
        
        for tag in tags:
            tag_name = tag.name
            text = tag.get_text().strip()

            # ── Context Tracking ──
            if tag_name in ['h2', 'h3']:
                # Check for Season header
                season_match = re.search(r"Season\s+(\d+)", text, re.IGNORECASE)
                if season_match:
                    current_season = int(season_match.group(1))
                    current_episode = None # Reset episode on new season
                
            if tag_name in ['h3', 'h4']:
                # Check for Episode header (often quoted or italicized)
                # Wikiquote format varies, but usually "Season X" > "Episode Name"
                pass 
                # (Skipping deeper episode parsing for now unless it's easy, 
                # as enrichment handles this well)

            # ── Quote Extraction ──
            if tag_name == 'dl':
                # Dialogue lists
                # <dl><dd><b>Red:</b> Quote...</dd></dl>
                for dd in tag.find_all("dd"):
                    line = dd.get_text(" ", strip=True)
                    match = speaker_pattern.match(line)
                    if match:
                        # Extract the quote part
                        raw_quote = line[match.end():].strip()
                        # Clean cleanup (remove [laughs], actions in parens if needed)
                        # clean_quote = re.sub(r"\[.*?\]", "", raw_quote) # Optional
                        
                        if len(raw_quote) > 10:
                            q = self._make_quote(
                                text=raw_quote,
                                source_url=self.URL,
                                season=current_season,
                                context="Wikiquote dialogue"
                            )
                            if q: quotes.append(q)
                            
            elif tag_name == 'ul':
                # Standalone quotes
                for li in tag.find_all("li"):
                    line = li.get_text(" ", strip=True)
                    # Check if it starts with Red attribution or is just a quote
                    # Wikiquote often puts the quote first, then attribution in sub-list
                    # But often for main characters it's "Quote. - Red"
                    
                    if "Reddington" in line or "Red" in line:
                         # Heuristic: split by dash
                         parts = re.split(r"[-–—]", line)
                         if len(parts) > 1:
                             possible_quote = parts[0].strip()
                             attribution = "".join(parts[1:]).strip()
                             
                             if "Red" in attribution and len(possible_quote) > 15:
                                 # Remove quotes around it if present
                                 possible_quote = possible_quote.strip('"“’’”')
                                 q = self._make_quote(
                                    text=possible_quote,
                                    source_url=self.URL,
                                    season=current_season,
                                    context="Wikiquote standalone"
                                )
                                 if q: quotes.append(q)

        print(f"  ✅ Found {len(quotes)} potential quotes from Wikiquote")
        return quotes
