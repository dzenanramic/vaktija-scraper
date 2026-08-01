"""CLI za vaktija-scraper."""

import argparse
import logging
import sys

from .client import VaktijaClient

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dohvati namaska vremena sa vaktija.eu",
    )
    parser.add_argument(
        "city",
        nargs="?",
        default="Landsberg am Lech",
        help="Ime grada za pretragu (default: 'Landsberg am Lech')",
    )
    parser.add_argument(
        "--slug",
        help="Direktni URL slug grada (npr. 'landsberg-am-lech') - preskače pretragu",
    )
    parser.add_argument(
        "--country",
        default="DE",
        help="Kod države (default: 'DE' za Njemačku)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listaj sve dostupne gradove za državu",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Detaljniji ispis",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        with VaktijaClient() as client:
            if args.list:
                locations = client.get_locations(args.country)
                print(f"\nGradovi u {args.country} ({len(locations)}):\n")
                for loc in locations:
                    print(f"  {loc.id:5d}  {loc.name:<30s}  {loc.slug}")
                return

            if args.slug:
                slug = args.slug
            else:
                print(f"Pretražujem: '{args.city}' (država: {args.country})...")
                location = client.search_location(args.city, args.country)
                if not location:
                    print(f"Grad '{args.city}' nije pronađen u {args.country}.")
                    print(
                        "Koristi --list za pregled svih gradova ili --slug za direktan pristup."
                    )
                    sys.exit(1)
                slug = location.slug
                print(f"Pronađen: {location.name} (slug: {slug})")

            result = client.get_prayer_times(slug)
            print(f"\n📍 {result.location.name}")
            if result.hijri_date:
                print(f"🕌 Hidžretski datum: {result.hijri_date}")
            print(f"\n  Sabah (Fajr):     {result.prayers.fajr}")
            print(f"  Izlazak sunca:    {result.prayers.sunrise}")
            print(f"  Podne (Dhuhr):    {result.prayers.dhuhr}")
            print(f"  Ikindija (Asr):   {result.prayers.asr}")
            print(f"  Akšam (Maghrib):  {result.prayers.maghrib}")
            print(f"  Jacija (Isha):    {result.prayers.isha}")

    except Exception as e:
        logger.error("Greška: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
