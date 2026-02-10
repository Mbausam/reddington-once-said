
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import os
import hashlib
from datetime import date
from collections import Counter

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

# Data Loading
QUOTES = []

def load_data():
    global QUOTES
    try:
        # Resolve path relative to this file's location for deployment compatibility
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "output", "reddington_quotes.json")
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                QUOTES = data.get("quotes", [])
            print(f"Loaded {len(QUOTES)} quotes from {json_path}")
        else:
            print(f"WARNING: Quote file not found at {json_path}")
    except Exception as e:
        print(f"Error loading data: {e}")

@app.on_event("startup")
async def startup_event():
    load_data()

# Endpoints

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Welcome to The Reddington Archives.",
        "endpoints": {
            "all_quotes": "/quotes",
            "random": "/quotes/random",
            "search": "/quotes/search?query=...",
            "stats": "/quotes/stats",
            "featured": "/quotes/featured"
        },
        "stats": {
            "total_quotes": len(QUOTES)
        }
    }

@app.get("/quotes", response_model=list[Quote], tags=["Quotes"])
async def get_quotes(
    season: int | None = Query(None, description="Filter by season number"),
    episode: int | None = Query(None, description="Filter by episode number"),
):
    """Get all quotes, optionally filtered by season/episode."""
    filtered = QUOTES
    if season:
        filtered = [q for q in filtered if q.get("season") == season]
    if episode:
        filtered = [q for q in filtered if q.get("episode") == episode]
    return filtered

@app.get("/quotes/random", response_model=Quote, tags=["Quotes"])
async def get_random_quote():
    """Get a single random quote."""
    if not QUOTES:
        raise HTTPException(status_code=404, detail="No quotes available")
    return random.choice(QUOTES)

@app.get("/quotes/featured", response_model=Quote, tags=["Quotes"])
async def get_featured_quote():
    """Get the quote of the day — deterministic per day so all visitors see the same one."""
    if not QUOTES:
        raise HTTPException(status_code=404, detail="No quotes available")
    # Use today's date as seed for deterministic daily selection
    today = date.today().isoformat()
    hash_val = int(hashlib.md5(today.encode()).hexdigest(), 16)
    index = hash_val % len(QUOTES)
    return QUOTES[index]

@app.get("/quotes/stats", tags=["Quotes"])
async def get_stats():
    """Get per-season quote counts and total stats."""
    season_counts = Counter(q.get("season") for q in QUOTES if q.get("season") is not None)
    seasons = sorted(season_counts.keys())
    return {
        "total_quotes": len(QUOTES),
        "seasons": {str(s): season_counts[s] for s in seasons},
        "total_seasons": len(seasons)
    }

@app.get("/quotes/search", response_model=list[Quote], tags=["Quotes"])
async def search_quotes(
    query: str = Query(..., min_length=3, description="Search term"),
):
    """Fuzzy search quotes by text."""
    query = query.lower()
    results = [
        q for q in QUOTES 
        if query in q.get("quote", "").lower() or query in q.get("context", "").lower()
    ]
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
