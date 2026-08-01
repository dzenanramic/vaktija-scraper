"""HTTP client for vaktija.eu - extracts prayer times from Next.js SSR pages.

URL pattern: https://vaktija.eu/{location-slug}
Data is embedded in <script id="__NEXT_DATA__"> as JSON.
"""

import json
import re
import logging
from typing import Optional

import httpx

from .models import Country, Location, PrayerTimes, VaktijaResult

logger = logging.getLogger(__name__)

BASE_URL = "https://vaktija.eu"
TIMEOUT = 15.0
_NEXT_DATA_RE = re.compile(
    r'<script\s+id="__NEXT_DATA__"[^>]*>\s*(.*?)\s*</script>',
    re.DOTALL,
)


class VaktijaClient:
    """Klijent za dohvaćanje namaskih vremena sa vaktija.eu."""

    def __init__(self, timeout: float = TIMEOUT) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "bs,en;q=0.9",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "VaktijaClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, path: str = "/") -> dict:
        """Fetch a page and return parsed __NEXT_DATA__ as dict."""
        resp = self._client.get(path)
        resp.raise_for_status()
        return self._parse_next_data(resp.text)

    @staticmethod
    def _parse_next_data(html: str) -> dict:
        """Extract and parse the __NEXT_DATA__ JSON from HTML."""
        match = _NEXT_DATA_RE.search(html)
        if not match:
            raise ValueError("__NEXT_DATA__ script not found in HTML")
        return json.loads(match.group(1))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_countries(self) -> list[Country]:
        """Dohvati sve države i njihove gradove."""
        data = self._fetch_page("/")
        country_list = data["props"]["pageProps"].get("countryList", [])
        return [Country(**c) for c in country_list]

    def get_locations(self, country_code: str = "DE") -> list[Location]:
        """Dohvati sve gradove za datu državu (npr. 'DE' za Njemačku)."""
        countries = self.get_countries()
        for country in countries:
            if country.code.upper() == country_code.upper():
                return country.locations
        return []

    def search_location(
        self, name: str, country_code: str = "DE"
    ) -> Optional[Location]:
        """Pretraži grad po imenu (case-insensitive partial match)."""
        locations = self.get_locations(country_code)
        name_lower = name.lower()
        for loc in locations:
            if name_lower in loc.name.lower():
                return loc
        return None

    def get_prayer_times(self, slug: str) -> VaktijaResult:
        """Dohvati namaska vremena za grad po slugu.

        Args:
            slug: URL slug grada (npr. 'landsberg-am-lech')

        Returns:
            VaktijaResult sa lokacijom i vremenima.
        """
        data = self._fetch_page(f"/{slug}")
        pp = data["props"]["pageProps"]

        location_raw = pp.get("locationRes") or {}
        prayers_raw = pp.get("dailyPrayersRes") or {}

        if not prayers_raw:
            raise ValueError(f"No prayer times found for slug '{slug}'")

        location = Location(
            id=location_raw.get("id", 0),
            name=location_raw.get("name", slug),
            slug=location_raw.get("slug", slug),
            latitude=location_raw.get("latitude", 0),
            longitude=location_raw.get("longitude", 0),
        )

        prayers = PrayerTimes(**prayers_raw)

        return VaktijaResult(
            location=location,
            prayers=prayers,
            hijri_date=pp.get("todayHijri"),
        )
