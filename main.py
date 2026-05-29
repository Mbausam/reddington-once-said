"""
ReddingtonOnceSaid — Main entry point.

Runs all configured scrapers, merges and deduplicates results,
and exports the final quote collection to JSON and CSV.

Usage:
    python main.py                     # Run all scrapers
    python main.py --quotes-only       # Only curated quote pages (fast)
    python main.py --transcripts-only  # Only transcript scraping (slow)
    python main.py --enrich            # Cross-reference quotes with transcripts
    python main.py --merge-claude      # Merge Claude-mined quotes into final output
    python main.py --mine-claude       # Run Claude miner on cached transcripts
    python main.py --ingest file.txt   # Ingest raw text file
"""

import argparse
import os
import json
import sys

from scrapers.quotes_scraper import QuotesScraper
from scrapers.transcript_scraper import TranscriptScraper
from scrapers.wikiquote_scraper import WikiquoteScraper
from scrapers.imdb_scraper import IMDbScraper
from scrapers.raw_text_scraper import RawTextScraper

from scrapers.transcript_miner import TranscriptMiner
from utils.data_processor import deduplicate, clean_all, sort_quotes
from utils.exporter import export_json, export_csv, generate_stats, print_stats
from utils.enricher import enrich_from_file

# ── Output paths ──────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "reddington_quotes.json")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "reddington_quotes.csv")
CLAUDE_QUOTES_FILE = os.path.join(OUTPUT_DIR, "claude_quotes.json")


def load_existing_quotes(filepath: str) -> list[dict]:
    """Load previously collected quotes from the JSON file if it exists."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        existing = data.get("quotes", [])
        print(f"\n  📂 Loaded {len(existing)} existing quotes from {filepath}")
        return existing
    except (json.JSONDecodeError, KeyError) as e:
        print(f"\n  [!] Could not load existing quotes: {e}")
        return []


def run_collection(
    run_quotes: bool = True,
    run_transcripts: bool = True,
    run_wikiquote: bool = True,
    run_imdb: bool = True,
    run_mining: bool = False,
    ingest_file: str | None = None,
):
    """
    Main collection pipeline:
    1. Load any previously collected quotes
    2. Run enabled scrapers
    3. Merge with existing data
    4. Deduplicate and clean
    5. Export to JSON and CSV
    6. Print stats
    """
    print("\n" + "=" * 60)
    print("  🎩 REDDINGTON ONCE SAID...")
    print("  Raymond Reddington Quote Compendium — Collector")
    print("=" * 60)

    # ── Step 1: Load existing ──────────────────────────────────
    existing_quotes = load_existing_quotes(JSON_OUTPUT)

    # ── Step 2: Scrape new quotes ──────────────────────────────
    new_quotes = []

    if ingest_file:
        print("\n" + "-" * 40)
        print("  📥 PHASE 0: Raw Text Ingestion")
        print("-" * 40)
        scraper = RawTextScraper(ingest_file)
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 Ingested {len(quotes)} quotes from file")

    if run_quotes:
        print("\n" + "-" * 40)
        print("  📡 PHASE 1: Curated Quote Pages")
        print("-" * 40)
        scraper = QuotesScraper()
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 Curated sources yielded {len(quotes)} quotes")

    if run_wikiquote:
        print("\n" + "-" * 40)
        print("  📖 PHASE 2: Wikiquote")
        print("-" * 40)
        scraper = WikiquoteScraper()
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 Wikiquote yielded {len(quotes)} quotes")

    if run_imdb:
        print("\n" + "-" * 40)
        print("  🎬 PHASE 3: IMDb")
        print("-" * 40)
        scraper = IMDbScraper()
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 IMDb yielded {len(quotes)} quotes")

    if run_transcripts:
        print("\n" + "-" * 40)
        print("  📺 PHASE 4: Episode Transcripts (External)")
        print("-" * 40)
        # Start with Season 1 only for the first run — expand later
        scraper = TranscriptScraper(seasons=[1])
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 Transcripts yielded {len(quotes)} quotes")
        
    if run_mining:
        print("\n" + "-" * 40)
        print("  ⛏️  PHASE 5: Transcript Mining (Internal)")
        print("-" * 40)
        scraper = TranscriptMiner()
        quotes = scraper.scrape()
        new_quotes.extend(quotes)
        print(f"  📊 Mining yielded {len(quotes)} quotes")

    # ── Step 3: Merge ──────────────────────────────────────────
    all_quotes = existing_quotes + new_quotes
    print(f"\n  🔀 Total before dedup: {len(all_quotes)} quotes")

    # ── Step 4: Clean and deduplicate ──────────────────────────
    all_quotes = clean_all(all_quotes)
    all_quotes = deduplicate(all_quotes)
    all_quotes = sort_quotes(all_quotes)
    print(f"  ✅ After dedup:        {len(all_quotes)} unique quotes")

    # ── Step 5: Export ─────────────────────────────────────────
    json_path = export_json(all_quotes, JSON_OUTPUT)
    csv_path = export_csv(all_quotes, CSV_OUTPUT)
    print(f"\n  💾 JSON saved: {json_path}")
    print(f"  💾 CSV saved:  {csv_path}")

    # ── Step 6: Stats ──────────────────────────────────────────
    stats = generate_stats(all_quotes)
    print_stats(stats)

    return all_quotes


def run_enrichment(seasons: list[int] | None = None):
    """
    Enrich existing quotes with season/episode info by cross-referencing
    against episode transcripts from Springfield.
    """
    print("\n" + "=" * 60)
    print("  🎩 REDDINGTON ONCE SAID...")
    print("  Raymond Reddington Quote Compendium — Enricher")
    print("=" * 60)

    if not os.path.exists(JSON_OUTPUT):
        print("\n  [!] No quotes file found. Run collection first:")
        print("      python main.py --quotes-only")
        return

    enrich_from_file(JSON_OUTPUT, seasons=seasons, download_first=True)


def merge_claude_quotes():
    """
    Merge Claude-mined quotes with the existing curated collection.
    Deduplicates, cleans, sorts, and exports the combined dataset.
    """
    print("\n" + "=" * 60)
    print("  🎩 MERGING CLAUDE QUOTES")
    print("=" * 60)

    # Load existing curated quotes
    existing = load_existing_quotes(JSON_OUTPUT)

    # Load Claude quotes
    claude_quotes = load_existing_quotes(CLAUDE_QUOTES_FILE)

    if not claude_quotes:
        print("  [!] No Claude quotes found. Run --mine-claude first.")
        print(f"      Expected: {CLAUDE_QUOTES_FILE}")
        return

    # Merge
    all_quotes = existing + claude_quotes
    print(f"  🔀 Combined before dedup: {len(all_quotes)} quotes")
    print(f"     Existing curated: {len(existing)}")
    print(f"     Claude mined:     {len(claude_quotes)}")

    # Clean, deduplicate, sort
    all_quotes = clean_all(all_quotes)
    all_quotes = deduplicate(all_quotes)
    all_quotes = sort_quotes(all_quotes)

    new_total = len(all_quotes)
    added = new_total - len(existing)
    print(f"  ✅ After dedup: {new_total} unique quotes ({added:+d})")

    # Export
    export_json(all_quotes, JSON_OUTPUT)
    export_csv(all_quotes, CSV_OUTPUT)
    print(f"  💾 Exported to {JSON_OUTPUT} and {CSV_OUTPUT}")

    # Stats
    stats = generate_stats(all_quotes)
    print_stats(stats)

    return all_quotes


def run_claude_miner(seasons=None, model="deepseek-chat"):
    """Run the transcript miner on cached transcripts."""
    from scrapers.claude_miner import mine_transcripts
    return mine_transcripts(seasons=seasons, model=model)


def main():
    """CLI entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="🎩 ReddingtonOnceSaid — Quote Compendium Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py                                # Run all scrapers\n"
            "  python main.py --quotes-only                  # Only curated pages\n"
            "  python main.py --wikiquote-only               # Only Wikiquote\n"
            "  python main.py --imdb-only                    # Only IMDb\n"
            "  python main.py --transcripts-only             # Only transcripts\n"
            "  python main.py --mine                         # Mine local transcripts\n"
            "  python main.py --enrich                       # Enrich all seasons\n"
            "  python main.py --merge-claude                 # Merge Claude quotes\n"
            "  python main.py --mine-claude                  # Run Claude miner\n"
            "  python main.py --mine-claude --seasons 1 2    # Mine specific seasons\n"
            "  python main.py --ingest my_quotes.txt         # Ingest raw text file\n"
        ),
    )

    parser.add_argument(
        "--quotes-only",
        action="store_true",
        help="Only scrape curated quote pages",
    )
    parser.add_argument(
        "--wikiquote-only",
        action="store_true",
        help="Only scrape Wikiquote",
    )
    parser.add_argument(
        "--imdb-only",
        action="store_true",
        help="Only scrape IMDb",
    )
    parser.add_argument(
        "--transcripts-only",
        action="store_true",
        help="Only scrape episode transcripts (slower)",
    )
    parser.add_argument(
        "--mine",
        action="store_true",
        help="Mine local transcripts for internal quotes",
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Cross-reference quotes with transcripts to find season/episode info",
    )
    parser.add_argument(
        "--enrich-seasons",
        nargs="+",
        type=int,
        default=None,
        help="Seasons to enrich (default: all). Example: --enrich-seasons 1 2 3",
    )
    parser.add_argument(
        "--ingest",
        type=str,
        help="Path to a text file containing raw quotes to ingest",
    )
    parser.add_argument(
        "--merge-claude",
        action="store_true",
        help="Merge Claude-mined quotes with the existing collection and export",
    )
    parser.add_argument(
        "--mine-claude",
        action="store_true",
        help="Run Claude miner on all cached transcripts",
    )
    parser.add_argument(
        "--claude-model",
        default="deepseek-chat",
        help="Model for --mine-claude (default: deepseek-chat)",
    )
    parser.add_argument(
        "--seasons",
        nargs="+",
        type=int,
        default=None,
        help="Seasons to process (for --mine-claude). Default: all.",
    )

    args = parser.parse_args()

    try:
        # ── Claude miner mode ─────────────────────────────────
        if args.mine_claude:
            run_claude_miner(seasons=args.seasons, model=args.claude_model)
            print("  🎉 Claude mining complete!\n")
            return

        # ── Claude merge mode ─────────────────────────────────
        if args.merge_claude:
            merge_claude_quotes()
            print("  🎉 Claude merge complete!\n")
            return

        # ── Enrichment mode ───────────────────────────────────
        if args.enrich:
            run_enrichment(seasons=args.enrich_seasons)
            print("  🎉 Enrichment complete!\n")
            return

        # ── Collection mode ───────────────────────────────────
        # Default: everything ON
        run_quotes = True
        run_wikiquote = True
        run_imdb = True
        run_transcripts = True
        run_mining = False # Default off as it's new

        # If any specific flags are set, turn off defaults and only run those
        if args.quotes_only or args.wikiquote_only or args.imdb_only or args.transcripts_only or args.ingest or args.mine:
            run_quotes = args.quotes_only
            run_wikiquote = args.wikiquote_only
            run_imdb = args.imdb_only
            run_transcripts = args.transcripts_only
            run_mining = args.mine

        # If ingest is the ONLY thing, defaults are already off by the check above
        # If no flags set, defaults remain True (run all)
        
        # NOTE: If user just runs 'python main.py', we might want to include mining?
        # For now, let's keep it separate to avoid overwhelming the initial run, unless verified.
        # But wait, if I want to "Maximize Collection", I probably want it on by default eventually.
        # I'll stick to flag for now for testing.

        quotes = run_collection(
            run_quotes=run_quotes,
            run_transcripts=run_transcripts,
            run_wikiquote=run_wikiquote,
            run_imdb=run_imdb,
            run_mining=run_mining,
            ingest_file=args.ingest,
        )
        print(f"  🎉 Done! Collected {len(quotes)} unique Reddington quotes.\n")

    except KeyboardInterrupt:
        print("\n\n  ⚠️  Interrupted! Partial results were NOT saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()

