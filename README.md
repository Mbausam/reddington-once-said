<div align="center">

# 🎩 Reddington Once Said

### *The Definitive Raymond Reddington Quote Compendium*

**221+ verified quotes · 10 seasons · The Blacklist**

<br>

*"Every cause has more than one effect."* — Raymond Reddington

---

[Explore Quotes](#-the-webapp) · [API Docs](#-rest-api) · [Run Locally](#-getting-started) · [Contributing](#-contributing)

</div>

<br>

## 🔥 What Is This?

A **cinematic, dark-themed webapp** and **REST API** for the most iconic quotes from Raymond "Red" Reddington — the sharp-tongued criminal mastermind from NBC's *The Blacklist*.

This isn't your average quotes site. It's an **immersive experience** — noir aesthetics, glassmorphism, dramatic animations, and Reddington's finest wisdom delivered with style.

### ✨ Features

| Feature | Description |
|---|---|
| 🎬 **Cinematic Hero** | Full-viewport hero with rotating Reddington images, atmospheric overlays, and a per-character reveal title animation |
| 🎲 **Deal Me a Quote** | Random quote generator with card-flip animation — like Red dealing you wisdom |
| 🔍 **Real-time Search** | Debounced fuzzy search as you type, with staggered result animations |
| 📺 **Season Explorer** | Accordion-style browser for all 10 seasons with lazy-loaded quote lists |
| 🔊 **Read Aloud** | Text-to-speech on every quote — reads in a slower, deliberate cadence |
| 📋 **Copy & Share** | One-click copy-to-clipboard and Twitter/X share buttons |
| 📱 **Fully Responsive** | Mobile-first design that looks premium on every screen size |
| ⚡ **REST API** | FastAPI-powered endpoints for random quotes, search, filtering, and stats |

<br>

## 🎯 The Webapp

The frontend is a **React + Vite** single-page application with a custom-built design system:

- **Noir color palette** — deep blacks, smoke grays, and gold accents
- **Glassmorphism** quote cards with backdrop blur and subtle glow effects
- **Micro-animations** — typewriter reveals, card flips, staggered fades, Ken Burns zooms
- **Google Fonts** — Playfair Display for quotes, Inter for UI elements
- **Zero dependencies** beyond React — pure CSS magic, no Tailwind

<br>

## ⚡ REST API

The API is powered by **FastAPI** and serves the verified quote dataset.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API info and available endpoints |
| `GET` | `/quotes` | All quotes (filterable by `?season=` and `?episode=`) |
| `GET` | `/quotes/random` | A single random quote |
| `GET` | `/quotes/featured` | Quote of the day (deterministic per day) |
| `GET` | `/quotes/search?query=...` | Fuzzy text search (min 3 characters) |
| `GET` | `/quotes/stats` | Per-season quote counts and totals |

### Example Response

```json
{
  "quote": "Every cause has more than one effect.",
  "season": 1,
  "episode": 7,
  "episode_title": "Frederick Barnes",
  "source_name": "EverydayPower",
  "context": ""
}
```

📖 **Interactive API docs** available at `/docs` (Swagger UI) when running locally.

<br>

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm

### 1. Clone the repo

```bash
git clone https://github.com/Mbausam/reddington-once-said.git
cd reddington-once-said
```

### 2. Start the API

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api/main.py
```

The API will be available at `http://localhost:8000`.

### 3. Start the Webapp

```bash
cd web

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The webapp will be available at `http://localhost:5173`.

<br>

## 📂 Project Structure

```
reddington-once-said/
├── api/
│   └── main.py              # FastAPI server with all endpoints
├── data/
│   ├── additional_quotes.txt # Supplementary quote sources
│   └── user_provided_quotes.txt
├── output/
│   ├── reddington_quotes.json  # The verified quote dataset (221 quotes)
│   └── reddington_quotes.csv   # CSV export
├── scrapers/                # Quote collection scrapers
│   ├── quotes_scraper.py    # Multi-source quote scraper
│   ├── transcript_scraper.py # Episode transcript scraper
│   ├── transcript_miner.py  # Quote extraction from transcripts
│   ├── wikiquote_scraper.py # Wikiquote scraper
│   └── ...
├── utils/                   # Data processing utilities
│   ├── data_processor.py    # Deduplication & cleaning
│   ├── enricher.py          # Season/episode tagging
│   └── exporter.py          # JSON/CSV export
├── web/                     # React + Vite frontend
│   ├── public/images/       # Reddington hero images
│   └── src/
│       ├── api.js           # API client module
│       ├── App.jsx          # Main app composition
│       ├── App.css          # Component styles
│       ├── index.css        # Design system & tokens
│       └── components/
│           ├── HeroSection.jsx    # Cinematic hero with rotating images
│           ├── QuoteCard.jsx      # Glassmorphism card with copy/share/speak
│           ├── RandomQuote.jsx    # Random quote dealer
│           ├── SearchBar.jsx      # Real-time search
│           ├── SeasonExplorer.jsx # Season accordion browser
│           └── Footer.jsx
├── main.py                  # Main scraper pipeline
├── requirements.txt
├── LICENSE
└── README.md
```

<br>

## 📊 Quote Coverage

| Season | Quotes | Season | Quotes |
|--------|--------|--------|--------|
| Season 1 | 30 | Season 6 | 13 |
| Season 2 | 26 | Season 7 | 15 |
| Season 3 | 28 | Season 8 | 13 |
| Season 4 | 26 | Season 9 | 16 |
| Season 5 | 37 | Season 10 | 7 |

**Total: 221 verified quotes** from verified sources including episode transcripts, Wikiquote, EverydayPower, HabitStacker, and manual curation.

<br>

## 🛣️ Roadmap

- [ ] 🎯 **More quotes** — expand to 500+ with better season coverage
- [ ] 💬 **Context & themes** — who Red was talking to, quote themes (loyalty, revenge, wisdom, humor)
- [ ] 🎨 **Shareable quote images** — generate styled images for social media
- [ ] 🌐 **Deploy online** — Vercel (frontend) + Render (API)
- [ ] 🗄️ **Database backend** — migrate from JSON to PostgreSQL for scale
- [ ] 🏷️ **Tags & categories** — filter by mood, theme, or character addressed
- [ ] ❤️ **Favorites** — save your favorite quotes with local storage

<br>

## 🤝 Contributing

Contributions are welcome! Whether it's new quotes, bug fixes, or feature ideas:

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding Quotes

Quotes should be verified against episode transcripts or reliable sources. Each quote entry needs:
- The exact quote text
- Season and episode number
- Source attribution

<br>

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<br>

## 🙏 Acknowledgments

- **The Blacklist** (NBC) for creating the legendary Raymond Reddington
- **James Spader** for bringing Red to life with unmatched charisma
- Quote sources: episode transcripts, Wikiquote, EverydayPower, HabitStacker

<br>

---

<div align="center">

*"I'm not a gumball machine, Lizzy. You don't get to just twist the handle whenever you want a treat."*

**Raymond Reddington** · The Blacklist

<br>

⭐ Star this repo if Red would approve

</div>
