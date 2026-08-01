"""Data models for vaktija.eu scraper."""

from pydantic import BaseModel


class Location(BaseModel):
    """Grad/lokacija za koju su dostupna namaska vremena."""
    id: int
    name: str
    slug: str
    latitude: float
    longitude: float


class Country(BaseModel):
    """Država sa listom gradova."""
    id: int
    name: str
    slug: str
    code: str
    locations: list[Location]


class PrayerTimes(BaseModel):
    """Dnevna namaska vremena."""
    fajr: str
    sunrise: str
    dhuhr: str
    asr: str
    maghrib: str
    isha: str


class VaktijaResult(BaseModel):
    """Kompletan rezultat za jednu lokaciju."""
    location: Location
    prayers: PrayerTimes
    hijri_date: str | None = None
