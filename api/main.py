
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import random
import os
import hashlib
from datetime import date
from collections import Counter

# Resolve base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "web", "dist")

app = FastAPI(
    title="The Reddington Archives API",
    description="Programmatic access to the wisdom of Raymond Reddington.",
    version="1.0.0"
)

# CORS (Allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Quote(BaseModel):
    quote: str
    season: int | None = None
    episode: int | None = None
    episode_title: str | None = None
    source_name: str | None = None
    context: str | None = None
    # Enriched fields (Claude miner)
    character_addressed: str | None = None
    themes: list[str] | None = None
    quote_type: str | None = None
    iconic_rating: int | None = None

# Data Loading
QUOTES = []

def load_data():
    global QUOTES
    try:
        json_path = os.path.join(BASE_DIR, "output", "reddington_quotes.json")
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                QUOTES = data.get("quotes", [])
            print(f"[OK] Loaded {len(QUOTES)} quotes from {json_path}")
        else:
            print(f"[WARN] Quote file not found at {json_path}")
    except Exception as e:
        print(f"[ERROR] loading data: {e}")

@app.on_event("startup")
async def startup_event():
    load_data()

# ── API ENDPOINTS ──────────────────────────────────────────────

@app.get("/api", tags=["General"])
async def api_root():
    return {
        "message": "Welcome to The Reddington Archives.",
        "endpoints": {
            "all_quotes": "/api/quotes?season=1&theme=loyalty&quote_type=parable&min_rating=4",
            "random": "/api/quotes/random",
            "search": "/api/quotes/search?query=...",
            "stats": "/api/quotes/stats",
            "featured": "/api/quotes/featured",
            "themes": "/api/themes",
        },
        "stats": {
            "total_quotes": len(QUOTES)
        }
    }

@app.get("/api/quotes", response_model=list[Quote], tags=["Quotes"])
async def get_quotes(
    season: int | None = Query(None, description="Filter by season number"),
    episode: int | None = Query(None, description="Filter by episode number"),
    theme: str | None = Query(None, description="Filter by theme (e.g. loyalty, power, revenge)"),
    character: str | None = Query(None, description="Filter by who Red is addressing (e.g. Lizzie, Dembe)"),
    quote_type: str | None = Query(None, description="Filter by quote type (e.g. one-liner, parable, threat)"),
    min_rating: int | None = Query(None, description="Minimum iconic rating (1-5)"),
):
    """Get all quotes, optionally filtered by season, episode, theme, character, or type."""
    filtered = QUOTES
    if season:
        filtered = [q for q in filtered if q.get("season") == season]
    if episode:
        filtered = [q for q in filtered if q.get("episode") == episode]
    if theme:
        filtered = [q for q in filtered if theme.lower() in (t.lower() for t in (q.get("themes") or []))]
    if character:
        filtered = [q for q in filtered if character.lower() in (q.get("character_addressed") or "").lower()]
    if quote_type:
        filtered = [q for q in filtered if q.get("quote_type") == quote_type]
    if min_rating is not None:
        filtered = [q for q in filtered if (q.get("iconic_rating") or 0) >= min_rating]
    return filtered

@app.get("/api/quotes/random", response_model=Quote, tags=["Quotes"])
async def get_random_quote():
    """Get a single random quote."""
    if not QUOTES:
        raise HTTPException(status_code=404, detail="No quotes available")
    return random.choice(QUOTES)

@app.get("/api/quotes/featured", response_model=Quote, tags=["Quotes"])
async def get_featured_quote():
    """Get the quote of the day — deterministic per day so all visitors see the same one."""
    if not QUOTES:
        raise HTTPException(status_code=404, detail="No quotes available")
    today = date.today().isoformat()
    hash_val = int(hashlib.md5(today.encode()).hexdigest(), 16)
    index = hash_val % len(QUOTES)
    return QUOTES[index]

@app.get("/api/quotes/stats", tags=["Quotes"])
async def get_stats():
    """Get per-season quote counts, themes, characters, and total stats."""
    season_counts = Counter(q.get("season") for q in QUOTES if q.get("season") is not None)
    seasons = sorted(season_counts.keys())

    theme_counts = Counter()
    char_counts = Counter()
    type_counts = Counter()
    for q in QUOTES:
        for t in (q.get("themes") or []):
            theme_counts[t] += 1
        c = q.get("character_addressed")
        if c and c != "unknown":
            char_counts[c] += 1
        qt = q.get("quote_type")
        if qt:
            type_counts[qt] += 1

    return {
        "total_quotes": len(QUOTES),
        "seasons": {str(s): season_counts[s] for s in seasons},
        "total_seasons": len(seasons),
        "themes": dict(theme_counts.most_common(20)),
        "characters": dict(char_counts.most_common(15)),
        "quote_types": dict(type_counts),
    }


@app.get("/api/themes", tags=["Quotes"])
async def get_themes():
    """Get all available themes with counts."""
    theme_counts = Counter()
    for q in QUOTES:
        for t in (q.get("themes") or []):
            theme_counts[t] += 1
    return {"themes": dict(theme_counts.most_common())}

@app.get("/api/characters", tags=["Quotes"])
async def get_characters():
    """Get all characters Red addresses, with quote counts and metadata."""
    char_counts = Counter()
    char_themes = {}
    for q in QUOTES:
        c = q.get("character_addressed")
        if c and c.lower() != "unknown":
            char_counts[c] += 1
            if c not in char_themes:
                char_themes[c] = Counter()
            for t in (q.get("themes") or []):
                char_themes[c][t] += 1

    characters = []
    for name, count in char_counts.most_common():
        characters.append({
            "name": name,
            "quote_count": count,
            "top_themes": [t for t, _ in char_themes.get(name, Counter()).most_common(3)],
            "image": f"/images/characters/{name.lower().replace(' ', '-')}.svg",
        })
    return {"characters": characters}

@app.get("/api/quotes/top", response_model=list[Quote], tags=["Quotes"])
async def get_top_quotes(
    limit: int = Query(50, ge=1, le=200, description="Number of top quotes to return"),
):
    """Get highest-rated iconic quotes (rating 4+)."""
    rated = [q for q in QUOTES if (q.get("iconic_rating") or 0) >= 4]
    rated.sort(key=lambda q: (q.get("iconic_rating") or 0), reverse=True)
    return rated[:limit]

@app.get("/api/quotes/search", response_model=list[Quote], tags=["Quotes"])
async def search_quotes(
    query: str = Query(..., min_length=3, description="Search term"),
):
    """Fuzzy search quotes by text."""
    query_lower = query.lower()
    results = []
    for q in QUOTES:
        if query_lower in q.get("quote", "").lower():
            results.append(q)
            continue
        if query_lower in q.get("context", "").lower():
            results.append(q)
            continue
        if query_lower in (q.get("character_addressed") or "").lower():
            results.append(q)
            continue
        themes = q.get("themes") or []
        if any(query_lower in t.lower() for t in themes):
            results.append(q)
            continue
    return results

# ── BACKWARD COMPATIBILITY (old /quotes/* paths) ──────────────
# Keep old paths working for direct API users

@app.get("/quotes", response_model=list[Quote], tags=["Compat"], include_in_schema=False)
async def compat_get_quotes(
    season: int | None = Query(None),
    episode: int | None = Query(None),
    theme: str | None = Query(None),
    character: str | None = Query(None),
    quote_type: str | None = Query(None),
    min_rating: int | None = Query(None),
):
    return await get_quotes(season=season, episode=episode, theme=theme,
                            character=character, quote_type=quote_type, min_rating=min_rating)

@app.get("/quotes/random", response_model=Quote, tags=["Compat"], include_in_schema=False)
async def compat_random():
    return await get_random_quote()

@app.get("/quotes/featured", response_model=Quote, tags=["Compat"], include_in_schema=False)
async def compat_featured():
    return await get_featured_quote()

@app.get("/quotes/stats", tags=["Compat"], include_in_schema=False)
async def compat_stats():
    return await get_stats()

@app.get("/quotes/search", response_model=list[Quote], tags=["Compat"], include_in_schema=False)
async def compat_search(query: str = Query(..., min_length=3)):
    return await search_quotes(query)

# ── SERVE FRONTEND (React build) ──────────────────────────────

if os.path.isdir(STATIC_DIR):
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")
    app.mount("/images", StaticFiles(directory=os.path.join(STATIC_DIR, "images")), name="images")

    # Catch-all: serve index.html for any non-API route (SPA)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Serve static files if they exist
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html (SPA routing)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/", tags=["General"])
    async def root_redirect():
        return await api_root()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
