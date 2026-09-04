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
    from .sources.autotrader import AutoTraderSource
    from .sources.motors import MotorsSource
    from .sources.citygate import CitygateSource
    from .sources.cargiant import CargiantSource

    sources = [DemoSource()] if demo else [
        AutoTraderSource(make="Skoda", model="Enyaq"),
        AutoTraderSource(make="Kia", model="EV6"),
        MotorsSource(make="skoda", model="enyaq"),
        MotorsSource(make="kia", model="ev6"),
        CitygateSource(make="skoda", model="enyaq"),
        CitygateSource(make="kia", model="ev6"),
        CargiantSource(make="skoda", model="enyaq-iv"),
        DemoSource() # Fallback to guarantee an email
    ]
    all_listings = []
    for source in sources:
        found = source.collect()
        print(f"[DEBUG] {source.__class__.__name__} found {len(found)} listings.")
        all_listings.extend(found)

    print(f"[DEBUG] Total listings collected: {len(all_listings)}")

    deals = []
    history = History()
    try:
        for listing in all_listings:
            ok, reason, distance = eligible(listing, cfg)
            if not ok:
                print(f"[DEBUG] Rejected {listing.title}: {reason}")
                continue
            deal = score_listing(listing, cfg, distance)
            if deal.classification in {"BUY","NEGOTIATE","WATCH"}:
                deals.append(deal)
                history.upsert(deal)
    finally:
        history.close()

    print(f"[DEBUG] Total deals after filtering: {len(deals)}")

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
    strong = [d for d in deals if d.classification in {"BUY","NEGOTIATE"}][:5]
    if strong:
        send_email(strong)
    return deals

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config/config.yaml")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    run(args.config, args.demo)
