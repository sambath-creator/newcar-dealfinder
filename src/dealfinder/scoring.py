from .models import VehicleListing, ScoredDeal

def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def score_listing(listing: VehicleListing, cfg: dict, distance_miles: float | None) -> ScoredDeal:
    vehicle_cfg = _match_vehicle(listing, cfg["vehicles"])
    if vehicle_cfg:
        base = vehicle_cfg
    else:
        base = {
            "seats": listing.seats or 5, "durability": 70, "servicing": 70,
            "warranty": listing.warranty_score or 70, "running_cost": 70,
            "depreciation": 65
        }

    market = listing.market_price_gbp or listing.price_gbp
    discount_pct = max(0, (market - listing.price_gbp) / market * 100) if market else 0

    price_score = _clamp(100 - ((listing.price_gbp - cfg["search"]["min_price_gbp"]) /
                                (cfg["search"]["max_price_gbp"] - cfg["search"]["min_price_gbp"]) * 100))
    discount_score = _clamp(discount_pct * 10)
    mileage_score = _clamp(100 - listing.mileage / cfg["search"]["max_mileage"] * 35)
    age_score = 100 if listing.registration_year == max(cfg["search"]["registrations"]) else 88
    age_mileage = (mileage_score + age_score) / 2

    spec = listing.specification_score if listing.specification_score is not None else 75
    durability = base.get("durability", 70)
    warranty = listing.warranty_score if listing.warranty_score is not None else base.get("warranty", 70)
    servicing = base.get("servicing", 70)
    running = base.get("running_cost", 70)
    dealer = listing.dealer_score if listing.dealer_score is not None else 70
    depreciation = base.get("depreciation", 65)

    seats = listing.seats or base.get("seats", 5)
    seven_bonus = 100 if seats >= 7 else 72
    # Specification includes the user's "spacious 5-seat / occasional 7-seat" preference.
    spec = (spec * 0.75) + (seven_bonus * 0.25)

    w = cfg["weights"]
    total = (
        price_score*w["purchase_price"] +
        discount_score*w["market_discount"] +
        age_mileage*w["age_mileage"] +
        spec*w["specification"] +
        durability*w["durability"] +
        warranty*w["warranty"] +
        servicing*w["servicing"] +
        running*w["running_cost"] +
        70*w["insurance"] +
        dealer*w["dealer"] +
        depreciation*w["depreciation"]
    ) / sum(w.values())

    t = cfg["thresholds"]
    classification = "BUY" if total >= t["buy"] else "NEGOTIATE" if total >= t["negotiate"] else "WATCH" if total >= t["watch"] else "REJECT"

    reasons = []
    if discount_pct >= 5: reasons.append(f"{discount_pct:.1f}% below supplied market price")
    if listing.mileage <= 3000: reasons.append("very low mileage")
    if seats >= 7: reasons.append("7-seat capability")
    if durability >= 85: reasons.append("strong durability profile")
    if running >= 88: reasons.append("low running-cost profile")
    if price_score >= 75: reasons.append("within target purchase sweet spot")

    px = cfg.get("px", {}).get("estimated_value_gbp")
    changeover = listing.price_gbp - px if px else None
    
    list_price = base.get("list_price_gbp")
    
    return ScoredDeal(listing, distance_miles or 0, discount_pct, round(total, 1),
                      classification, reasons, changeover, list_price)

def _match_vehicle(listing, vehicles):
    text = f"{listing.title} {listing.make} {listing.model} {listing.trim}".lower()
    for v in vehicles:
        if any(alias.lower() in text for alias in v.get("aliases", [])):
            return v
    return None
