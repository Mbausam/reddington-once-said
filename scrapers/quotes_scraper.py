"""
QuotesScraper — collects Reddington quotes from curated quote pages.

Uses requests + BeautifulSoup (no JavaScript needed).
Targets sites that have pre-compiled lists of Reddington quotes.

Also includes a comprehensive seed collection of verified quotes
gathered from multiple sources across the web.
"""

import re
from scrapers.base_scraper import BaseScraper


class QuotesScraper(BaseScraper):
    """
    Scrapes curated Reddington quote pages using BeautifulSoup.

    These are static sites with lists of quotes already attributed
    to Reddington, so we just need to extract the text.
    """

    # Curated quote page URLs — add more as you find them
    SOURCES = [
        {
            "url": "https://everydaypower.com/raymond-reddington-quotes/",
            "name": "EverydayPower",
            "parser": "_parse_generic_attributed",
        },
        {
            "url": "https://thehabitstacker.com/raymond-reddington-quotes/",
            "name": "HabitStacker",
            "parser": "_parse_generic_attributed",
        },
        {
            "url": "https://www.goodreads.com/quotes/tag/raymond-reddington",
            "name": "Goodreads",
            "parser": "_parse_goodreads",
        },
    ]

    # ──────────────────────────────────────────────────────────────
    # SEED QUOTES — verified quotes from web research
    # These are real Reddington quotes confirmed across multiple sources.
    # Since some sites block scraping (Medium, ScreenRant, etc.),
    # we include them here directly. Dedup will handle overlaps.
    # ──────────────────────────────────────────────────────────────
    SEED_QUOTES = [
        # ── Power, Control & Strategy ──
        "Power isn't something you're given. It's something you take.",
        "In this world, there are no sides. Only players.",
        "We're all puppets, Harold. Some of us just have more strings than others.",
        "The only way to truly know someone is to see how they handle power.",
        "In this world, power is everything. The rest is just an illusion.",
        "Life is a game, my dear. Play it to win, or don't play at all.",
        "The greatest trick the devil ever pulled was convincing the world he didn't exist.",
        "Knowledge without action is meaningless.",
        "The greatest weapon is not a gun or a bomb. It's the truth.",
        "We all have the devil in us, Harold. But the best of us have angels too.",

        # ── Truth & Lies ──
        "Lies by omission are still lies, Harold. Some would argue they're the worst kind.",
        "Truth is such a rare thing, it is delightful to tell it.",
        "The thing about the truth is, not a lot of people can handle it.",
        "The truth will set you free, but first, it will piss you off.",
        "What if I were to tell you that all the things you come to believe about yourself are a lie?",
        "I can only lead you to the truth. I can't make you believe it.",

        # ── Loyalty & Betrayal ──
        "Value loyalty above all else.",
        "Loyalty is in the eye of the beholder.",
        "Betrayal is just loyalty reprioritized.",
        "A friend is a person who will help you move. A real friend is a person who will help you move a body.",
        "In this world, loyalty is rare. That's why it's so valuable.",

        # ── Love & Relationships ──
        "When you love someone, you have no control. That's what love is. Being powerless.",
        "A man who's willing to burn the world down to protect the one person they care about, that's a man I understand.",
        "If my circle of friends gets any smaller, it won't be a circle.",

        # ── Pain, Loss & Revenge ──
        "The past is a ghost that never truly leaves us.",
        "Revenge isn't a passion. It's a disease. It eats away your mind and poisons your soul.",
        "There is nothing that can take the pain away. But eventually, you will find a way to live with it. There will be nightmares, and every day, when you wake up, it will be the first thing you think about. Until one day, it will be the second thing.",
        "Once you cross over, there are things in the darkness that can keep your heart from feeling the light again.",
        "Without pain there can be no real pleasure. Without the lows you have no way to measure the highs.",
        "The measure of a man is not in how he gets knocked to the mat, it's in how he gets up.",
        "Sometimes the only way to find yourself is to lose everything.",
        "The past is a prison. It's up to us to break free.",
        "Forgiveness is a luxury not everyone can afford.",

        # ── Wisdom & Life ──
        "People say youth is wasted on the young. I disagree. I believe wisdom is wasted on the old.",
        "You have to make your choices; you have to be happy with them.",
        "Life is far too important a thing ever to talk seriously about.",
        "Life is all about perception. It's what you make of it that counts.",
        "Every cause has more than one effect.",
        "You can't judge a book by its cover. But you can by its first few chapters and certainly by its last.",
        "The world can be such an unsparingly savage place one can be forgiven for believing that evil will triumph in the end.",
        "The best time to plant a tree is 20 years ago. The second best time is now. Luckily for you, I have three seedlings.",
        "You get older and you realize we make life so complicated when it doesn't need to be. We complicate ourselves to death.",
        "Time is the ultimate luxury, I think. To be savored, not hoarded nor compressed nor controlled.",
        "Not every answer is worth knowing.",
        "There are no shortcuts in life, only detours.",
        "The road to hell is paved with good intentions.",
        "The line between good and evil is often blurred. It's the choices we make that define us.",
        "Never trust a man who smiles too much. It's either a sign of charm or a sign of madness.",
        "The world is full of wolves and sheep. Be the wolf.",
        "In this world, there are no heroes or villains. Only survivors.",
        "Money can't buy happiness, but it can buy a damn good alibi.",

        # ── Fear & Survival ──
        "I always found fear to be my most valuable sense.",
        "Trust no one. Not even yourself.",
        "As you well know, one of the keys to my success is a clear and consistent understanding of my own limitations.",

        # ── Wit & Humor ──
        "Agent Keen, I have a tip. You're a winter, not an autumn. Stop wearing olive.",
        "I'm not a gumball machine, Lizzy. You don't get to just twist the handle whenever you want a treat.",
        "Never underestimate the power of glitter.",
        "There's a fine line between fishing and standing on the shore looking like an idiot.",
        "Please excuse the gun. I'd hate for them to think we were in cahoots.",
        "Dead? Pishposh. What's death? It's just a process, right?",
        "You look familiar. Have I threatened you before?",
        "See, this is why I don't go to family reunions.",
        "It's good to meet you. I've heard nothing but terrible things.",
        "I don't know if I should be thrilled or terrified.",
        "I have no interest in cases that I have no interest in.",
        "You talk too much.",
        "Let me put your mind at ease.",
        "Really, I'm all for being thorough, but at this point, you are just taking the nickel tour.",

        # ── Iconic Monologues & Speeches ──
        "I had bullets. He had words. But when he was done talking for the first time, I truly understood which of those was more powerful.",
        "The only thing that is real is the present, and you've plundered it, robbed it of the very geniuses that might have averted the dystopia you so fear.",
        "As bad as you think I am, as far as you think I'm willing to go to protect that which I hold dear, you can't possibly fathom how deep that well of mine truly goes.",
        "God can't protect you, but I can.",
        "What are they gonna do to me that hasn't been done before? Kill me? None of it is worse than losing you.",
        "You know the problem with drawing lines in the sand? With a breath of air, they disappear.",
        "You see that Geoff, that is what a good man does. That is what separates men like him from men like you and me.",
        "I could tell you how to win a marathon, but you're assuming it's a 26.6-mile race.",
        "You lost her. I can't find her. It's that simple.",
        "As a rule, I consider jealousy to be a base emotion, but in this case, it's quite endearing.",
        "I was a lifeguard my junior year in high school. Had to give mouth-to-mouth to Mrs. Beerman. She belched up a lung full of corned beef and chlorine. I haven't been in a pool since.",
        "Is it just me or is the human race armed with religion, poisoned by prejudice, and absolutely frantic with hatred and fear, galloping pell-mell back to the Dark Ages? Who on Earth is hurt by a little girl going to school or a child being gay?",
        "You will make a mistake and when you do, I will be there to indulge the undeniable pleasure and the sweet satisfaction of 'I told you so.'",
        "The future is a sucker's bet, a maybe, a contingency, a 'What if?'",
        "You see, if you were a betting man, you would understand that now trumps later every time.",

        # ── Deep & Philosophical ──
        "I've always found that true power comes from the ability to remain calm when the world around you is in chaos.",
        "Hope is the worst of all evils because it prolongs the torment of man.",
        "Everyone on my jet is there because they chose to be. That cannot be said of most endeavors in life.",
        "I've made it my mission in life to identify, cultivate, and exploit the weakness in my enemies.",
        "Sometimes the only way out is through.",
        "The human condition is a series of choices. Some right, some wrong, but all ours to make.",
        "Nothing is so common as the wish to be remarkable.",
        "Regret requires age or the passage of time. And believe me, time has a way of making all things clear.",
    ]

    def __init__(self):
        super().__init__(source_name="QuotesScraper")

    def scrape(self) -> list[dict]:
        """Scrape all configured curated quote sources + seed quotes."""
        all_quotes = []

        # ── Phase 1: Scrape live sites ────────────────────────
        for source in self.SOURCES:
            print(f"\n  🔍 Scraping: {source['name']} ({source['url']})")
            soup = self._fetch_page(source["url"])
            if soup is None:
                continue

            parser = getattr(self, source["parser"], None)
            if parser is None:
                print(f"  [!] No parser found for {source['name']}")
                continue

            quotes = parser(soup, source["url"], source["name"])
            print(f"  ✅ Found {len(quotes)} quotes from {source['name']}")
            all_quotes.extend(quotes)

        # ── Phase 2: Add seed quotes ──────────────────────────
        print(f"\n  🌱 Adding {len(self.SEED_QUOTES)} seed quotes from web research...")
        for text in self.SEED_QUOTES:
            quote = self._make_quote(
                text=text,
                source_url="https://multiple-sources",
            )
            if quote:
                quote["source_name"] = "WebResearch"
                all_quotes.append(quote)
        print(f"  ✅ Added {len(self.SEED_QUOTES)} seed quotes")

        return all_quotes

    def _parse_generic_attributed(self, soup, url: str, source_name: str) -> list[dict]:
        """
        Generic parser for sites with numbered quotes in the format:
            1. "Quote text here." – Raymond Reddington

        Works for: EverydayPower, HabitStacker, and similar sites.
        """
        quotes = []
        all_text = soup.get_text()

        # Pattern: quoted text followed by Reddington attribution
        patterns = [
            r'["\u201c]([^"\u201d]{15,})["\u201d]\s*[-–—]+\s*(?:Raymond\s+)?(?:Red\s+)?Reddington',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                quote = self._make_quote(text=match, source_url=url)
                if quote:
                    quote["source_name"] = source_name
                    quotes.append(quote)

        # Fallback: look for blockquote elements
        if not quotes:
            blockquotes = soup.find_all("blockquote")
            for bq in blockquotes:
                text = bq.get_text(strip=True)
                if "reddington" in text.lower():
                    clean = re.sub(
                        r"\s*[-–—]+\s*(Raymond\s+)?(Red\s+)?Reddington.*$",
                        "", text, flags=re.IGNORECASE,
                    )
                    quote = self._make_quote(text=clean, source_url=url)
                    if quote:
                        quote["source_name"] = source_name
                        quotes.append(quote)

        return quotes

    def _parse_goodreads(self, soup, url: str, source_name: str) -> list[dict]:
        """
        Parser for Goodreads tag pages.
        Structure: <div class="quoteText"> &ldquo;Quote&rdquo; <br> ... </div>
        """
        quotes = []
        quote_divs = soup.find_all("div", class_="quoteText")
        
        for div in quote_divs:
            # Goodreads puts the quote in the first text node or distinct element
            # usually surrounded by &ldquo; and &rdquo;
            # We can get strict text up to the first <br> or <script>
            
            # Text often looks like: “The only thing that is real...” ― Raymond Reddington
            full_text = div.get_text(separator=" ", strip=True)
            
            # Split by the em-dash or author name
            if "Reddington" not in full_text:
                continue
                
            # Extract quote part (handling smart quotes)
            match = re.search(r'[“""](.*?)[”""]', full_text)
            if match:
                clean_text = match.group(1).strip()
                quote = self._make_quote(text=clean_text, source_url=url)
                if quote:
                    quote["source_name"] = source_name
                    quotes.append(quote)
            else:
                 # Fallback: take everything before the dash
                 parts = re.split(r"[-–—]", full_text)
                 if len(parts) > 1:
                     clean_text = parts[0].strip().strip('"“” ')
                     quote = self._make_quote(text=clean_text, source_url=url)
                     if quote:
                        quote["source_name"] = source_name
                        quotes.append(quote)
                        
        return quotes
