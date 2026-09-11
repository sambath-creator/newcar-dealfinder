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
    from .sources.cinch import CinchSource
    from .sources.arnoldclark import ArnoldClarkSource

    postcode = cfg["search"].get("postcode", "DA1 5UB")
    radius = cfg["search"].get("radius_miles", 200)

    sources = [DemoSource()] if demo else [
        CinchSource(make="skoda", model="enyaq"),
        CinchSource(make="kia", model="ev6"),
        CinchSource(make="kia", model="ev5"),
        CinchSource(make="bmw", model="ix1"),
        CinchSource(make="tesla", model="model y"),
        CinchSource(make="volkswagen", model="id4"),
        CinchSource(make="audi", model="q4 e-tron"),
        CinchSource(make="nissan", model="ariya"),
        CinchSource(make="toyota", model="rav4"),
        CinchSource(make="hyundai", model="tucson"),
        ArnoldClarkSource(make="skoda", model="enyaq"),
        ArnoldClarkSource(make="kia", model="ev6"),
        ArnoldClarkSource(make="kia", model="ev5"),
        ArnoldClarkSource(make="bmw", model="ix1"),
        ArnoldClarkSource(make="tesla", model="model y"),
        ArnoldClarkSource(make="volkswagen", model="id4"),
        ArnoldClarkSource(make="audi", model="q4 e-tron"),
        ArnoldClarkSource(make="nissan", model="ariya"),
        ArnoldClarkSource(make="toyota", model="rav4"),
        ArnoldClarkSource(make="hyundai", model="tucson")
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
        # First filter out ineligible cars and score them
        valid_deals = []
        for listing in all_listings:
            ok, reason, distance = eligible(listing, cfg)
            if not ok:
                print(f"[DEBUG] Rejected {listing.title}: {reason}")
                continue
            deal = score_listing(listing, cfg, distance)
            if deal.classification in {"BUY","NEGOTIATE","WATCH"}:
                valid_deals.append(deal)
                
        # Deduplicate identical specs (same make, model, insurance, road tax, and features)
        # keeping the one with the best combination of low price and low mileage.
        # We can sort by price first, then mileage to pick the "best" one per group.
        valid_deals.sort(key=lambda d: (d.listing.price_gbp, d.listing.mileage))
        
        seen_specs = set()
        for deal in valid_deals:
            l = deal.listing
            spec_key = (l.make.lower(), l.model.lower(), l.insurance_group, l.road_tax, tuple(sorted(l.features)))
            if spec_key in seen_specs:
                print(f"[DEBUG] Deduplicated {l.title} (identical spec found cheaper/lower mileage)")
                continue
            seen_specs.add(spec_key)
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
    strong = [d for d in deals if d.classification in {"BUY","NEGOTIATE"}][:20]
    if strong:
        send_email(strong)
    return deals

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config/config.yaml")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    run(args.config, args.demo)
