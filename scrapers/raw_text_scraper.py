"""
RawTextScraper — parses a text file containing quotes.
Useful for bulk ingestion of manually pasted quotes.
"""

import re
import os
from scrapers.base_scraper import BaseScraper

class RawTextScraper(BaseScraper):
    """
    Parses a local text file for quotes.
    Handles various copy-paste formats.
    """

    def __init__(self, filepath: str):
        super().__init__(source_name="ManualIngest")
        self.filepath = filepath

    def scrape(self) -> list[dict]:
        if not os.path.exists(self.filepath):
            print(f"  [!] File not found: {self.filepath}")
            return []

        print(f"\n  🔍 Ingesting file: {self.filepath}")
        quotes = []
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # ── Strategy 1: Double-quoted strings ──
        # Looks for "Quote text"
        # Since the user input has quotes like "Lies By Omission...", this is good.
        
        pattern = r'["“”](.*?)["“”]'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            clean = match.strip()
            # Filter brevity to avoid grabbing single words
            if len(clean) > 15:
                # Heuristic: Is it likely a quote?
                # The user's text also contains headers in quotes maybe? 
                # e.g. "Lies By Omission..." is a quote.
                
                q = self._make_quote(
                    text=clean,
                    source_url="Manual Input",
                    context="Bulk Ingest"
                )
                if q: quotes.append(q)

        # ── Strategy 2: Fallback for lines without quotes ──
        # If we didn't find many quotes, maybe try line-by-line
        if len(quotes) < 3:
             lines = content.split('\n')
             for line in lines:
                 line = line.strip()
                 if len(line) > 20 and not line.startswith("http"):
                     q = self._make_quote(text=line, source_url="Manual Input")
                     if q: quotes.append(q)
        
        print(f"  ✅ Extracted {len(quotes)} potential quotes from text file")
        return quotes
