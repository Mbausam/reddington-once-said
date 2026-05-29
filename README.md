<div align="center">

# 🎩 Reddington Once Said

### *The Definitive Raymond Reddington Quote Compendium*

**1,868 quotes · 10 seasons · 20 themes · 15+ characters · Iconic ratings**

<br>

*"Every cause has more than one effect."* — Raymond Reddington

---

[Live Demo](#) · [API Docs](#-rest-api) · [Run Locally](#-getting-started) · [Contributing](#-contributing)

</div>

<br>

## 🔥 What Is This?

A **cinematic, dark-themed webapp** and **REST API** for every quotable line from Raymond "Red" Reddington — the sharp-tongued criminal mastermind from NBC's *The Blacklist*.

Each quote is enriched with AI-extracted metadata: **who Red was talking to, what themes it covers, what type of quote it is, and an iconic rating from 1-5**. It's not just a quote list — it's an **immersive exploration of Reddington's worldview**.

<img src="docs/screenshots/hero.png" alt="Hero screenshot" width="100%" />

### ✨ Features

| Feature | Description |
|---|---|
| 🎬 **Cinematic Hero** | Full-viewport hero with 10 rotating Reddington images, atmospheric overlays, per-character reveal title |
| 🎲 **Deal Me a Quote** | Random quote generator with card-flip animation — like Red dealing you wisdom |
| 🔍 **Smart Search** | Debounced search with filter panel — filter by theme, character, quote type, and minimum rating |
| 🏷️ **Theme Explorer** | Interactive tag cloud of 20 themes (loyalty, power, identity, revenge...) — click to filter |
| 👤 **Character Gallery** | Browse quotes by who Red was talking to — Lizzie, Dembe, Cooper, and more |
| ⭐ **Iconic Hall** | Red's greatest hits — the top-rated quotes across all 10 seasons |
| 📊 **Live Stats** | Animated counters showing total quotes, seasons, themes, and characters |
| 🔊 **Read Aloud** | Text-to-speech on every quote — reads in a slower, deliberate cadence |
| 📋 **Copy & Share** | One-click copy-to-clipboard and Twitter/X share |
| 📱 **Fully Responsive** | Mobile-first design that looks premium on every screen size |
| ⚡ **REST API** | FastAPI-powered endpoints with rich filtering and Swagger docs |

<br>

## 🎯 The Webapp

The frontend is a **React + Vite** single-page application with a custom-built design system:

- **Noir color palette** — deep blacks, smoke grays, and gold accents
- **Glassmorphism** quote cards with backdrop blur and subtle glow effects
- **Micro-animations** — character-by-character title reveal, card flips, staggered fades, Ken Burns zooms
- **Google Fonts** — Playfair Display for quotes, Inter for UI
- **Zero UI dependencies** — pure CSS magic, no Tailwind, no component library
- **Scroll-reveal animations** — sections animate in as you browse
- **Character avatars** — noir-styled SVG portraits for every character Red addresses

### Sections

| Section | What it does |
|---|---|
| **Stats Banner** | Animated counters — 1,868 quotes, 10 seasons, 20 themes, 15+ characters |
| **Theme Cloud** | 20 interactive theme chips, sized by frequency. Click to filter all quotes by theme |
| **Deal Me a Quote** | Random quote with card-flip animation and full metadata display |
| **Character Gallery** | Horizontal scroll of character cards. Click to see every quote Red spoke to that person |
| **Iconic Hall** | Grid of the highest-rated quotes (4-5 stars) with special gold border treatment |
| **Search Archives** | Debounced search with collapsible filter panel — theme, character, type, min rating |
| **Season Explorer** | Accordion-style browser for all 10 seasons with lazy-loaded quote lists |

<br>

## ⚡ REST API

The API is powered by **FastAPI** and serves all 1,868 enriched quotes.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api` | API info, available endpoints, and quote count |
| `GET` | `/api/quotes` | All quotes — filterable by `season`, `episode`, `theme`, `character`, `quote_type`, `min_rating` |
| `GET` | `/api/quotes/random` | A single random quote |
| `GET` | `/api/quotes/featured` | Quote of the day — deterministic per date |
| `GET` | `/api/quotes/top?limit=50` | Highest-rated iconic quotes (rating 4+) |
| `GET` | `/api/quotes/search?query=...` | Search across quote text, context, character, and themes |
| `GET` | `/api/quotes/stats` | Per-season counts, top themes, character breakdowns, quote type distribution |
| `GET` | `/api/themes` | All themes with quote counts |
| `GET` | `/api/characters` | All characters with quote counts and top themes |

### Quote Schema

```json
{
  "quote": "Every cause has more than one effect.",
  "season": 1,
  "episode": 7,
  "episode_title": "Frederick Barnes",
  "source_name": "TranscriptMiner",
  "context": "Red explains to Lizzy why seemingly small actions ripple outward",
  "character_addressed": "Elizabeth Keen",
  "themes": ["wisdom", "power", "truth"],
  "quote_type": "wisdom",
  "iconic_rating": 5
}
```

📖 **Interactive Swagger docs** at `/docs` when running locally.

<br>

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm

### 1. Clone & Install

```bash
git clone https://github.com/Mbausam/reddington-once-said.git
cd reddington-once-said

# Python dependencies
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend dependencies
cd web && npm install && cd ..
```

### 2. Run the API (serves both backend + frontend)

```bash
python api/main.py
# → http://localhost:8000 (API + webapp)
# → http://localhost:8000/docs (Swagger)
```

### 3. Dev mode (frontend with hot reload)

```bash
cd web && npm run dev
# → http://localhost:5173 (hits API on :8000)
```

<br>

## 📂 Project Structure

```
reddington-once-said/
├── api/
│   └── main.py                    # FastAPI server — all endpoints + SPA serving
├── output/
│   ├── reddington_quotes.json     # 1,868 enriched quotes (the canonical dataset)
│   └── reddington_quotes.csv      # CSV export
├── scrapers/
│   ├── claude_miner.py            # LLM transcript miner — extracts quotes from episodes
│   ├── transcript_downloader.py   # Bulk transcript downloader (Springfield)
│   ├── transcript_scraper.py      # Individual transcript scraper
│   └── ...
├── scripts/
│   └── fetch_images.py            # Generate noir-themed character & hero SVGs
├── utils/
│   ├── data_processor.py          # Deduplication, cleaning, sorting
│   ├── enricher.py                # Season/episode tagging from transcripts
│   └── exporter.py                # JSON/CSV export with enriched fields
├── web/                           # React + Vite frontend
│   ├── public/
│   │   └── images/
│   │       ├── reddington-1.png through reddington-5.png   # Hero photos
│   │       ├── characters/         # 9 character SVG avatars
│   │       └── hero/               # 5 noir gradient hero backgrounds
│   └── src/
│       ├── api.js                  # API client (fetch wrapper)
│       ├── App.jsx                 # App composition — all sections wired together
│       ├── App.css                 # 1,500+ lines of component styles
│       ├── index.css               # Design system, tokens, animations, reset
│       └── components/
│           ├── HeroSection.jsx       # Cinematic hero with rotating images
│           ├── StatsBanner.jsx       # Animated stat counters
│           ├── ThemeCloud.jsx        # Interactive theme filter grid
│           ├── RandomQuote.jsx       # Card-flip random quote dealer
│           ├── CharacterGallery.jsx  # Horizontal scrollable character cards
│           ├── IconicHall.jsx        # Top-rated quotes showcase
│           ├── SearchBar.jsx         # Search + filter panel
│           ├── SeasonExplorer.jsx    # Season accordion browser
│           ├── QuoteCard.jsx         # Glassmorphism card with metadata
│           └── Footer.jsx
├── main.py                        # Scraper CLI pipeline
├── requirements.txt
├── LICENSE
└── README.md
```

<br>

## 📊 The Dataset

### Quote Coverage by Season

| Season | Quotes | Avg Rating | Season | Quotes | Avg Rating |
|--------|--------|------------|--------|--------|------------|
| Season 1 | ~207 | 4.2 | Season 6 | ~190 | 4.1 |
| Season 2 | ~165 | 4.1 | Season 7 | ~100 | 4.0 |
| Season 3 | ~195 | 4.1 | Season 8 | ~170 | 4.0 |
| Season 4 | ~160 | 4.0 | Season 9 | ~120 | 3.9 |
| Season 5 | ~160 | 4.0 | Season 10 | ~130 | 4.0 |

### Enriched Metadata

Every quote in the dataset includes:

| Field | Description |
|---|---|
| `character_addressed` | Who Red was speaking to — Lizzie, Dembe, Cooper, Ressler, Mr. Kaplan, etc. |
| `themes` | 1-3 lowercase themes — loyalty, betrayal, power, truth, identity, death, love, crime, wisdom... |
| `quote_type` | one-liner, monologue, parable, threat, wisdom, humor, or emotional |
| `iconic_rating` | 1-5 rating — 5 = all-time classic Reddington line, 1 = decent but not his best |

### Top Themes

loyalty · power · identity · truth · betrayal · family · crime · wisdom · death · love · revenge · justice · morality · survival · trust · humor · freedom · sacrifice · legacy · regret

<br>

## 🛣️ Roadmap

- [x] ~~Expand to 500+ quotes~~ — 1,868 and counting
- [x] ~~Context & themes~~ — AI-enriched with characters, themes, types, and ratings
- [x] ~~Tags & category filters~~ — filter by theme, character, quote type, and rating
- [ ] 🌐 **Deploy online** — Render/Railway for the API, serve the built frontend
- [ ] 🗄️ **Database backend** — migrate from JSON to PostgreSQL
- [ ] 🎨 **Shareable quote cards** — generate styled images for social media
- [ ] ❤️ **Favorites** — save your favorite quotes with local storage
- [ ] 📸 **Real character photos** — replace SVG avatars with actual cast photos

<br>

## 🤝 Contributing

Contributions are welcome — new quotes, bug fixes, or features:

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding Quotes

Quotes should be verified against episode transcripts. Each entry needs:
- Exact quote text
- Season and episode number
- Source attribution

<br>

## 📜 License

MIT License — see [LICENSE](LICENSE).

<br>

## 🙏 Acknowledgments

- **The Blacklist** (NBC/Sony) for creating Raymond Reddington
- **James Spader** for bringing him to life
- Quote sources: episode transcripts (Springfield), Wikiquote, EverydayPower, HabitStacker
- AI transcript mining: DeepSeek API

<br>

---

<div align="center">

*"I'm not a gumball machine, Lizzy. You don't get to just twist the handle whenever you want a treat."*

**Raymond Reddington** · The Blacklist

<br>

⭐ **Star this repo if Red would approve**

</div>
