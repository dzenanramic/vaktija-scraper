#!/usr/bin/env python3
"""Sync prayer times from vaktija.eu to Supabase.

Usage:
    python scripts/sync-to-supabase.py              # default: Landsberg am Lech, today
    python scripts/sync-to-supabase.py --slug stuttgart
    python scripts/sync-to-supabase.py --slug landsberg-am-lech --date 2026-08-02

Environment variables:
    SUPABASE_URL          Supabase project URL (required)
    SUPABASE_SERVICE_KEY  Supabase service_role key (required)
"""

import argparse
import logging
import os
import sys
from datetime import date, datetime, timedelta

from supabase import Client, create_client

# Add src to path so we can import vaktija_scraper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vaktija_scraper.client import VaktijaClient

logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

DEFAULT_SLUG = "landsberg-am-lech"
TABLE = "prayer_times"


def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY env vars required")
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync prayer times from vaktija.eu → Supabase"
    )
    parser.add_argument("--slug", default=DEFAULT_SLUG, help="Location slug")
    parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD (default: today)",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    target_date = date.today()
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    # ── Fetch from vaktija.eu ────────────────────────────────────
    logger.info("Fetching prayer times for slug=%s date=%s", args.slug, target_date)

    with VaktijaClient() as vclient:
        result = vclient.get_prayer_times(args.slug)

    logger.info(
        "Got times: Fajr=%s Dhuhr=%s Asr=%s Maghrib=%s Isha=%s",
        result.prayers.fajr,
        result.prayers.dhuhr,
        result.prayers.asr,
        result.prayers.maghrib,
        result.prayers.isha,
    )

    # ── Upsert into Supabase ────────────────────────────────────
    sb = get_supabase()

    row = {
        "location": result.location.name,
        "slug": args.slug,
        "date": target_date.isoformat(),
        "hijri_date": result.hijri_date,
        "fajr": result.prayers.fajr,
        "sunrise": result.prayers.sunrise,
        "dhuhr": result.prayers.dhuhr,
        "asr": result.prayers.asr,
        "maghrib": result.prayers.maghrib,
        "isha": result.prayers.isha,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }

    # Use upsert: insert if not exists, update if exists (by unique constraint)
    resp = sb.table(TABLE).upsert(row, on_conflict="slug,date").execute()

    if hasattr(resp, "error") and resp.error:
        logger.error("Supabase error: %s", resp.error)
        sys.exit(1)

    logger.info("✅ Upserted %s for %s", args.slug, target_date)


if __name__ == "__main__":
    main()
