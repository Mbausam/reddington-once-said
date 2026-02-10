"""
IMDbScraper — collects Reddington quotes from IMDb.

Scrapes the quotes page for "The Blacklist" (tt2741602).
"""

import re
from scrapers.base_scraper import BaseScraper

class IMDbScraper(BaseScraper):
    """
    Scrapes quotes from IMDb.
    URL: https://www.imdb.com/title/tt2741602/quotes/
    """
    
    BASE_URL = "https://www.imdb.com/title/tt2741602/quotes/"
    
    def __init__(self):
        super().__init__(source_name="IMDb")

    def scrape(self) -> list[dict]:
        """Scrape IMDb quotes page."""
        # Note: IMDb often paginates or lazy loads. 
        # We'll start with the main one. It might show "See more" which is a separate page or JS.
        # For simplicity in this v1, we check the main URL. 
        # If IMDb structure is complex class-based, we search for specific divs.
        
        print(f"\n  🔍 Scraping: {self.source_name} ({self.BASE_URL})")
        soup = self._fetch_page(self.BASE_URL)
        if soup is None:
            return []

        quotes = []
        
        # IMDb quotes structure:
        # <div class="list-item">
        #   <div class="sodatext">
        #      <p>
        #        <span class="character">Raymond 'Red' Reddington</span>:
        #        Quote text here...
        #      </p>
        #   </div>
        # </div>
        
        # Fallback to old or new IMDb layout logic
        list_items = soup.find_all("div", class_="sodatext")
        
        if not list_items:
            # Try newer layout selectors if generic class fails
            # Often contained in 'ipc-list-card' or similar in new designs
            # But 'sodatext' is the classic desktop view usually served to bots
            pass

        print(f"    Found {len(list_items)} quote blocks to process...")

        for item in list_items:
            # Each item might have multiple lines/speakers
            # We want lines spoken by Red
            
            # The structure often has <span class="character">Name</span>
            paragraphs = item.find_all("p")
            for p in paragraphs:
                text = p.get_text(" ", strip=True)
                
                # Check speaker
                if "Raymond 'Red' Reddington" in text or "Reddington" in text:
                    # Clean up the speaker name to get just the quote
                    # Usually "Raymond 'Red' Reddington: The quote."
                    
                    # Split on colon
                    parts = text.split(":", 1)
                    if len(parts) == 2:
                        speaker = parts[0].strip()
                        content = parts[1].strip()
                        
                        if "Red" in speaker and len(content) > 10:
                            q = self._make_quote(
                                text=content,
                                source_url=self.BASE_URL,
                                context="IMDb"
                            )
                            if q: quotes.append(q)

        print(f"  ✅ Found {len(quotes)} quotes from IMDb")
        return quotes
