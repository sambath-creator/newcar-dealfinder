# New Car Deal Finder

A UK new/nearly-new vehicle deal intelligence agent designed around a 150-mile radius of Dartford.

## Target profile

- Registration: 2025 or 2026
- Mileage: <= 5,000 miles
- Price: £25,000–£42,000
- Annual mileage: 8,000
- Cash purchase
- Spacious 5-seater required
- 7 seats preferred, but not mandatory
- Current PX: 2016 Ford Grand C-Max
- Initial watchlist:
  - Skoda Enyaq 85
  - Peugeot E-5008
  - JAECOO 7 SHS-P
  - OMODA 9
  - Hyundai Ioniq 5
  - Kia EV6
  - Kia Sportage HEV

## Architecture

`collect -> normalise -> filter -> market intelligence -> score -> history/dedupe -> alert`

The first release deliberately keeps the deal engine deterministic. Source adapters are isolated so permitted APIs, feeds, dealer inventory endpoints or public pages can be added without changing scoring.

This project does **not** bypass CAPTCHAs, bot protection, paywalls, authentication or other access controls. Use only sources and access methods you are permitted to use.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
python -m dealfinder --config config/config.yaml --demo
```

## Email

Set these environment variables/secrets:

- `SMTP_HOST`
- `SMTP_PORT` (default 587)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `ALERT_FROM`
- `ALERT_TO`

The GitHub Actions workflow can run in dry-run mode if email credentials are absent.

## Adding a source

Implement `ListingSource` in `src/dealfinder/sources/`. The source must return `VehicleListing` objects. Do not put scoring or user-specific rules in the adapter.

## GitHub Actions

The workflow runs daily at 07:30 Europe/London and can be triggered manually. The SQLite history database is uploaded as an artifact on each run. For persistent history, use an external store or commit a controlled state file in a separate workflow.

## Deal classifications

- `BUY`: unusually strong deal and meets all hard requirements
- `NEGOTIATE`: strong candidate where negotiation is likely worthwhile
- `WATCH`: interesting but not yet compelling
- `REJECT`: fails hard criteria

## Important implementation note

A real production deployment needs one or more permitted listing feeds/sources. The repository includes a demo source and source-adapter contract rather than pretending that a brittle scraper is a reliable production feed.
