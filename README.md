# Vaktija Scraper

Dohvaćanje namaskih vremena sa [vaktija.eu](https://vaktija.eu) - zvanična vremena Islamske Zajednice Bošnjaka za Evropu.

## Instalacija

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Korištenje

### Dohvati namaska vremena za grad (pretraga po imenu)

```bash
.venv/bin/vaktija "Landsberg am Lech"
# ili
.venv/bin/python -m vaktija_scraper.cli "Landsberg am Lech"
```

### Direktno preko sluga

```bash
.venv/bin/vaktija --slug landsberg-am-lech
```

### Drugi gradovi/države

```bash
# Grad u Austriji
.venv/bin/vaktija "Wien" --country AT

# Grad u Švicarskoj
.venv/bin/vaktija "Zürich" --country CH
```

### Lista svih gradova u državi

```bash
.venv/bin/vaktija --list              # default: DE (Njemačka)
.venv/bin/vaktija --list --country AT  # Austrija
.venv/bin/vaktija --list --country BA  # Bosna i Hercegovina
```

### Debug ispis

```bash
.venv/bin/vaktija "Landsberg am Lech" --verbose
```

## API

Glavni klijent je `VaktijaClient`:

```python
from vaktija_scraper.client import VaktijaClient

with VaktijaClient() as client:
    # Dohvati sve države i gradove
    countries = client.get_countries()

    # Dohvati gradove za jednu državu
    locations = client.get_locations("DE")

    # Pretraži grad
    loc = client.search_location("Landsberg", "DE")

    # Dohvati namaska vremena
    result = client.get_prayer_times("landsberg-am-lech")
    print(result.prayers.fajr)    # 04:01:00
    print(result.prayers.maghrib) # 21:00:00
```

## Kako radi

Stranica [vaktija.eu](https://vaktija.eu) je Next.js SSR aplikacija. Podaci o namaskim vremenima su embedovani u `<script id="__NEXT_DATA__">` JSON objektu unutar HTML-a. URL pattern je `https://vaktija.eu/{slug}` gdje je `{slug}` slug grada.

Scraper koristi samo `httpx` - nije potreban headless browser.

## Struktura projekta

```
vaktija-scraper/
├── pyproject.toml
├── src/vaktija_scraper/
│   ├── __init__.py
│   ├── client.py    # httpx klijent, parser __NEXT_DATA__ JSON-a
│   ├── models.py    # Pydantic modeli (Location, Country, PrayerTimes)
│   └── cli.py       # CLI sa argparse
└── README.md
```

## Dostupne države

| Kod | Država              |
| --- | ------------------- |
| DE  | Njemačka            |
| AT  | Austrija            |
| CH  | Švicarska           |
| BA  | Bosna i Hercegovina |
| HR  | Hrvatska            |
| SI  | Slovenija           |
| RS  | Srbija              |
| IT  | Italija             |
| FR  | Francuska           |
| SE  | Švedska             |
| NL  | Nizozemska          |
| BE  | Belgija             |
| DK  | Danska              |
| NO  | Norveška            |
| LU  | Luksemburg          |
| LI  | Lihtenštajn         |
| ME  | Crna Gora           |

## GitHub Actions (automatski sync)

Workflow [`sync-prayer-times.yml`](.github/workflows/sync-prayer-times.yml) pokreće sync svaku ponoć (22:00 UTC).

### Setup

```bash
# 1. Inicijaliziraj git i pushaj na GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:TVOJ_USERNAME/vaktija-scraper.git
git push -u origin main

# 2. Dodaj secrets na GitHub:
#    GitHub repo → Settings → Secrets and variables → Actions → New repository secret
#    - SUPABASE_URL: https://hrmiztsnijhiwnozbucu.supabase.co
#    - SUPABASE_SERVICE_KEY: eyJhbGciOi... (service_role key)
```

Workflow se može i ručno pokrenuti: GitHub → Actions → Sync Prayer Times → Run workflow.
