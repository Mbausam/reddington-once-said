"""
TranscriptMiner — feeds cached episode transcripts through an LLM API
(Anthropic-compatible) to extract Raymond Reddington's most quotable lines
with rich metadata.

Each transcript is subtitle-format (no speaker labels). The LLM identifies
Reddington's lines by his distinctive voice — philosophical, sardonic,
storytelling, elegant threats, parables about "a man I once knew..."

Uses checkpoint-based resumability so interrupted runs pick up where they left off.

Configuration via environment variables:
    ANTHROPIC_AUTH_TOKEN   — API key (required; also reads ANTHROPIC_API_KEY)
    ANTHROPIC_BASE_URL     — API endpoint (default: https://api.deepseek.com/anthropic)

Usage:
    python scrapers/claude_miner.py                    # Mine all cached transcripts
    python scrapers/claude_miner.py --seasons 1 2 3    # Specific seasons only
    python scrapers/claude_miner.py --model deepseek-chat  # Model override
    python scrapers/claude_miner.py --dry-run           # Estimate token usage only
"""

import os
import json
import time
import sys
import argparse

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "transcripts")
META_FILE = os.path.join(CACHE_DIR, "_episodes.json")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "claude_checkpoint.json")
CLAUDE_QUOTES_FILE = os.path.join(OUTPUT_DIR, "claude_quotes.json")

# ── System prompt ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert on The Blacklist and Raymond "Red" Reddington (James Spader).
Analyze episode transcripts and extract Reddington's most memorable, quotable lines.

The transcripts are subtitle-based — ALL dialogue without speaker labels. You must identify Reddington's lines by his DISTINCTIVE VOICE:
- Philosophical, world-weary observations on life and human nature
- Storytelling parables ("I once knew a man in Marrakech who...")
- Witty, sardonic, darkly humorous remarks
- Elegant threats — menacing but never crude
- Speaks in riddles, metaphors, and analogies
- References to art, history, fine dining, world travel, the criminal underworld
- Manipulative yet disarmingly honest about his nature
- Fondness for Lizzie (Elizabeth Keen), often teaching/protecting her
- Loyalty speeches about Dembe, Mr. Kaplan, his associates

SKIP these (not quotable):
- Simple plot exposition ("The target is at the airport.", "We leave at dawn.")
- Short functional lines ("Yes.", "No.", "Go ahead.", "Let's go.", "This way.")
- Generic action dialogue ("Get down!", "Watch out!", "He's getting away!")
- Fillers and reactions ("What?", "Why?", "I see.", "Of course.")

INCLUDE these (quotable Reddington):
- Philosophical reflections on loyalty, betrayal, power, truth, identity, death
- Memorable threats or warnings delivered with Red's signature style
- Witty one-liners that showcase his dark humor
- Extended monologues or parables (his famous "I once knew..." stories)
- Emotional moments, especially with Lizzie or Dembe
- Observations about criminals, the FBI, the underworld
- Quotes that reveal his moral code or worldview

For each quote, return:
- "quote": exact text (preserve original wording, fix subtitle typos silently)
- "character_addressed": who Red is speaking to (Lizzie, Dembe, Ressler, Mr. Kaplan, Cooper, Tom, Aram, Samar, etc.) — use "unknown" if unclear
- "context": one-line scene context — why he's saying this, what's happening
- "themes": array of 1-3 lowercase themes from [loyalty, betrayal, power, family, truth, identity, death, love, crime, wisdom, humor, revenge, justice, freedom, sacrifice, survival, regret, legacy, morality, trust]
- "quote_type": one of [one-liner, monologue, parable, threat, wisdom, humor, emotional]
- "iconic_rating": integer 1-5 (5 = all-time classic Reddington line, 1 = decent but not era-defining)

Output valid JSON array. If no quotable Reddington lines found, return [].
Do NOT include markdown code fences. Output ONLY the JSON array."""


def _load_checkpoint() -> dict:
    """Load the checkpoint file tracking which episodes have been processed."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed": [], "total_quotes": 0, "last_updated": None}


def _save_checkpoint(processed: list[str], total_quotes: int):
    """Save progress after each episode so crashes don't lose work."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "processed": processed,
            "total_quotes": total_quotes,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, f, indent=2)


def _load_claude_quotes() -> list[dict]:
    """Load previously extracted Claude quotes from the output file."""
    if os.path.exists(CLAUDE_QUOTES_FILE):
        with open(CLAUDE_QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("quotes", [])
    return []


def _save_claude_quotes(quotes: list[dict]):
    """Save accumulated quotes to the output file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CLAUDE_QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "project": "ReddingtonOnceSaid",
                "description": "Quotes extracted by Claude from episode transcripts",
                "total_quotes": len(quotes),
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
            "quotes": quotes,
        }, f, indent=2, ensure_ascii=False)


def _get_episodes(seasons: list[int] | None = None) -> list[dict]:
    """Get the list of episodes to process, reading from the manifest if available."""
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            all_episodes = json.load(f)
    else:
        # Build manually
        SEASON_EPISODES = {1:22,2:22,3:23,4:22,5:22,6:22,7:19,8:22,9:22,10:22}
        all_episodes = []
        for s in range(1, 11):
            for e in range(1, SEASON_EPISODES.get(s, 22) + 1):
                all_episodes.append({
                    "season": s, "episode": e, "title": "",
                    "filename": f"s{s:02d}e{e:02d}.txt",
                })

    if seasons:
        all_episodes = [ep for ep in all_episodes if ep["season"] in seasons]

    return all_episodes


def _parse_json_response(raw: str) -> list[dict] | None:
    """Robustly extract a JSON array from an LLM response, handling various wrapper formats."""
    import re
    text = raw.strip()

    # Strategy 1: direct parse
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        # Maybe it's {"quotes": [...]} or {"data": [...]} etc
        if isinstance(result, dict):
            for key in ("quotes", "data", "results", "items"):
                if isinstance(result.get(key), list):
                    return result[key]
            # Maybe the array is nested under some other key
            for v in result.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    return v
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown fences
    cleaned = text
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-z]*\s*", "", cleaned, count=1)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for key in ("quotes", "data", "results", "items"):
                if isinstance(result.get(key), list):
                    return result[key]
    except json.JSONDecodeError:
        pass

    # Strategy 3: find the first [...] array in the text
    start = cleaned.find("[")
    if start != -1:
        # Try to find matching closing bracket by tracking nesting
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "[":
                depth += 1
            elif cleaned[i] == "]":
                depth -= 1
                if depth == 0:
                    try:
                        result = json.loads(cleaned[start:i + 1])
                        if isinstance(result, list):
                            return result
                    except json.JSONDecodeError:
                        pass
                    break

    return None


def _estimate_tokens(text: str | int) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    if isinstance(text, int):
        return text // 4
    return len(text) // 4


def mine_transcripts(
    seasons: list[int] | None = None,
    model: str = "deepseek-chat",
    dry_run: bool = False,
    delay: float = 1.0,
) -> list[dict]:
    """
    Process all cached transcripts through Claude to extract Reddington quotes.

    Args:
        seasons: Which seasons to process (default: all 1-10).
        model: Claude model ID to use.
        dry_run: If True, estimate token usage without making API calls.
        delay: Seconds between API calls (for rate limiting).

    Returns:
        List of enriched quote dicts.
    """
    # ── Check prerequisites ─────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not dry_run:
        print("X No API key found.")
        print("   Set one of: ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY")
        print("   PowerShell: $env:ANTHROPIC_AUTH_TOKEN = 'sk-...'")
        print("   Bash:       export ANTHROPIC_AUTH_TOKEN='sk-...'")
        return []

    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
    is_deepseek = "deepseek" in base_url.lower()

    if not dry_run:
        try:
            from anthropic import Anthropic
        except ImportError:
            print("X anthropic SDK not installed. Run: pip install anthropic")
            return []
        client = Anthropic(api_key=api_key, base_url=base_url)

    # ── Load state ──────────────────────────────────────────────
    checkpoint = _load_checkpoint()
    processed = set(checkpoint.get("processed", []))
    all_quotes = _load_claude_quotes()

    episodes = _get_episodes(seasons)
    pending = [ep for ep in episodes if ep["filename"].replace(".txt", "") not in processed]

    print(f"\n{'='*60}")
    print(f"  [mine]  TRANSCRIPT MINER")
    print(f"  Model: {model}")
    print(f"  API endpoint: {base_url}")
    print(f"  Total episodes: {len(episodes)}")
    print(f"  Already processed: {len(processed)}")
    print(f"  Remaining: {len(pending)}")
    print(f"  Quotes collected so far: {len(all_quotes)}")
    print(f"{'='*60}\n")

    if dry_run:
        total_chars = 0
        for ep in pending:
            filepath = os.path.join(CACHE_DIR, ep["filename"])
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    total_chars += len(f.read())

        est_tokens = _estimate_tokens(total_chars)
        sys_tokens = _estimate_tokens(SYSTEM_PROMPT)
        print(f"  [stats] Dry Run Estimates:")
        print(f"     Episodes to process: {len(pending)}")
        print(f"     Total transcript chars: {total_chars:,}")
        print(f"     Est. transcript tokens: ~{est_tokens:,}")
        print(f"     System prompt tokens: ~{sys_tokens}")
        print(f"     Est. total input tokens: ~{est_tokens + sys_tokens * len(pending):,}")
        print(f"     Est. output tokens: ~{len(pending) * 500:,} (assuming ~500 per episode)")
        print(f"     Using endpoint: {base_url}")
        print(f"     Model: {model}")
        return []

    if not pending:
        print("  OK All episodes already processed!")
        return all_quotes

    # ── Process each pending transcript ─────────────────────────
    total = len(pending)
    for i, ep in enumerate(pending, 1):
        filepath = os.path.join(CACHE_DIR, ep["filename"])
        label = f"S{ep['season']:02d}E{ep['episode']:02d}"
        title_str = f" — {ep['title']}" if ep.get("title") else ""

        if not os.path.exists(filepath):
            print(f"  [{i}/{total}] [warn]  {label}{title_str} — transcript not cached, skipping")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        if len(transcript_text) < 200:
            print(f"  [{i}/{total}] [warn]  {label}{title_str} — transcript too short ({len(transcript_text)} chars), skipping")
            continue

        print(f"  [{i}/{total}] >> {label}{title_str} ({len(transcript_text):,} chars) ...", end=" ", flush=True)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Season {ep['season']}, Episode {ep['episode']}"
                        f"{': ' + ep['title'] if ep.get('title') else ''}\n\n"
                        f"TRANSCRIPT:\n\n{transcript_text}\n\n"
                        f"Extract Raymond Reddington's quotable lines from this transcript."
                    ),
                }],
            )

            # Parse LLM response
            raw_output = response.content[0].text
            episode_quotes = _parse_json_response(raw_output)
            if episode_quotes is None:
                print(f"[warn]  Invalid JSON response, skipping")
                continue

            if not isinstance(episode_quotes, list):
                print(f"[warn]  Unexpected response type: {type(episode_quotes).__name__}, skipping")
                continue

            # Enrich each quote with season/episode metadata from our side
            for q in episode_quotes:
                q["season"] = ep["season"]
                q["episode"] = ep["episode"]
                q["episode_title"] = ep.get("title", "")
                q["source_name"] = "ClaudeMiner"
                q["source_url"] = f"Transcript S{ep['season']:02d}E{ep['episode']:02d}"
                # Ensure all enriched fields exist
                q.setdefault("character_addressed", None)
                q.setdefault("themes", [])
                q.setdefault("quote_type", None)
                q.setdefault("iconic_rating", None)
                q.setdefault("context", "")

            all_quotes.extend(episode_quotes)
            processed.add(ep["filename"].replace(".txt", ""))

            # Save after every episode (resumability)
            _save_claude_quotes(all_quotes)
            _save_checkpoint(list(processed), len(all_quotes))

            print(f"OK {len(episode_quotes)} quotes (total: {len(all_quotes)})")

        except Exception as e:
            print(f"X {e}")
            # Save checkpoint even on error so we don't re-process this one
            # unless it's a transient error (rate limit, etc.)
            if "rate" in str(e).lower() or "429" in str(e):
                print(f"     Rate limited. Waiting 10s before continuing...")
                time.sleep(10)
            elif "overloaded" in str(e).lower() or "529" in str(e):
                print(f"     Server overloaded. Waiting 30s before continuing...")
                time.sleep(30)
            else:
                # Save progress but don't mark this episode as processed
                # so it gets retried on next run
                _save_claude_quotes(all_quotes)
                _save_checkpoint(list(processed), len(all_quotes))
                time.sleep(3)

        # Polite delay between calls
        if i < total:
            time.sleep(delay)

    # ── Final save ──────────────────────────────────────────────
    _save_claude_quotes(all_quotes)
    _save_checkpoint(list(processed), len(all_quotes))

    print(f"\n{'='*60}")
    print(f"  Done! Mining complete!")
    print(f"  Total quotes extracted: {len(all_quotes)}")
    print(f"  Episodes processed: {len(processed)}")
    print(f"  Output: {CLAUDE_QUOTES_FILE}")
    print(f"{'='*60}\n")

    return all_quotes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Claude Transcript Miner for Reddington quotes")
    parser.add_argument("--seasons", nargs="+", type=int, default=None,
                        help="Seasons to mine (default: all 1-10)")
    parser.add_argument("--model", default="deepseek-chat",
                        help="Model ID (default: deepseek-chat)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Estimate token usage without making API calls")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between API calls in seconds")
    args = parser.parse_args()
    mine_transcripts(seasons=args.seasons, model=args.model,
                     dry_run=args.dry_run, delay=args.delay)
