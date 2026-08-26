import argparse
import json
from .config import load_config
from .filters import eligible
from .scoring import score_listing
from .history import History
from .alerts import send_email
from .sources.demo import DemoSource

def run(config_path, demo=False):
    cfg = load_config(config_path)
    sources = [DemoSource()] if demo else [DemoSource()]
    all_listings = []
    for source in sources:
        all_listings.extend(source.collect())

    deals = []
    history = History()
    try:
        for listing in all_listings:
            ok, reason, distance = eligible(listing, cfg)
            if not ok:
                continue
            deal = score_listing(listing, cfg, distance)
            if deal.classification in {"BUY","NEGOTIATE","WATCH"}:
                deals.append(deal)
                history.upsert(deal)
    finally:
        history.close()

    deals.sort(key=lambda x: x.score, reverse=True)
    payload = [{
        "classification": d.classification,
        "title": d.listing.title,
        "price_gbp": d.listing.price_gbp,
        "mileage": d.listing.mileage,
        "year": d.listing.registration_year,
        "score": d.score,
        "distance_miles": round(d.distance_miles,1),
        "changeover_gbp": d.effective_changeover_gbp,
        "url": d.listing.url,
        "reasons": d.reasons,
    } for d in deals]
    print(json.dumps(payload, indent=2))
    strong = [d for d in deals if d.classification in {"BUY","NEGOTIATE"}]
    if strong:
        send_email(strong)
    return deals

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config/config.yaml")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    run(args.config, args.demo)
