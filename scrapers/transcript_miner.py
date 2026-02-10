
import os
import re
import glob
from scrapers.base_scraper import BaseScraper

class TranscriptMiner(BaseScraper):
    """
    Mines quotes directly from cached episode transcripts.
    This finds "deep cuts" that might not be on curated quote sites.
    """
    
    TRANSCRIPT_DIR = "cache/transcripts"
    
    # Patterns to identify Red speaking
    # Springfield transcripts usually don't have perfect formatting, but often use "Red:" or "Reddington:"
    SPEAKER_PATTERNS = [
        r"(?:^|\n)\s*(?:Red|Reddington|Raymond|Mr\.?\s*Reddington)\s*[:]\s*(.*?)(?:\n|$)"
    ]
    
    # Text quality filters
    MIN_LENGTH = 40  # Avoid short "Yes" or "No" lines
    MAX_LENGTH = 600 # Avoid massive monologues that might be parsing errors (or keep them?)
    
    # Keywords that suggest a "Reddington-esque" quote (philosophical, criminal, storytelling)
    KEYWORDS = [
        "life", "death", "truth", "lie", "criminal", "business", "loyalty", 
        "friend", "enemy", "world", "story", "remember", "know", "believe",
        "love", "fear", "money", "power", "time", "past", "future"
    ]

    def __init__(self):
        super().__init__(source_name="TranscriptMining")

    def scrape(self) -> list[dict]:
        """
        Iterate through cached transcripts and extract quotes.
        """
        print(f"\n  ⛏️  Mining transcripts from {self.TRANSCRIPT_DIR}...")
        
        if not os.path.exists(self.TRANSCRIPT_DIR):
            print(f"    [!] Transcript cache not found at {self.TRANSCRIPT_DIR}")
            print(f"    [!] Please run with --enrich first to download transcripts.")
            return []

        files = glob.glob(os.path.join(self.TRANSCRIPT_DIR, "*.txt"))
        if not files:
            print("    [!] No transcript files found.")
            return []
            
        print(f"    Found {len(files)} transcripts to process.")
        
        all_quotes = []
        
        for file_path in files:
            # Filename format: s01e01.txt (assumed from Enricher logic)
            filename = os.path.basename(file_path)
            # Try to parse season/episode from filename
            # Expected format sXXeXX.txt
            match = re.search(r"s(\d+)e(\d+)", filename, re.IGNORECASE)
            if not match:
                continue
                
            season = int(match.group(1))
            episode = int(match.group(2))
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            quotes = self._extract_from_text(content, season, episode)
            all_quotes.extend(quotes)
            
        print(f"  ✅ Mined {len(all_quotes)} potential quotes locally.")
        return all_quotes

    def _extract_from_text(self, text: str, season: int, episode: int) -> list[dict]:
        found = []
        
        for pattern in self.SPEAKER_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for raw_text in matches:
                # Clean up whitespace
                clean_text = " ".join(raw_text.split())
                
                # Filter by length
                if len(clean_text) < self.MIN_LENGTH:
                    continue
                if len(clean_text) > self.MAX_LENGTH:
                     continue
                     
                # Filter by keywords (optional, keeps quality high)
                # We want deep/philosophical quotes, not "The gun is in the car."
                # But maybe we want everything? Let's use a loose keyword filter or just score it?
                # For now, let's essentially keep everything substantial.
                
                # Check for "junk" starts like "Scene:" or descriptions
                if clean_text.startswith("(") or clean_text.startswith("["):
                    continue

                # Create quote object
                # We don't have the episode title easily here unless we look it up, 
                # but BaseScraper handles missing titles gracefully usually.
                q = self._make_quote(
                    text=clean_text,
                    source_url=f"Transcript S{season:02d}E{episode:02d}",
                    season=season,
                    episode=episode,
                    context="Mined from transcript"
                )
                if q:
                    found.append(q)
                    
        return found
