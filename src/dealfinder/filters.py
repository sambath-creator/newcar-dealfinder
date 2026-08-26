from .geo import distance_miles
from .models import VehicleListing

def eligible(listing: VehicleListing, cfg: dict) -> tuple[bool, str, float | None]:
    s = cfg["search"]
    if listing.price_gbp < s["min_price_gbp"] or listing.price_gbp > s["max_price_gbp"]:
        return False, "price", None
    if listing.mileage > s["max_mileage"]:
        return False, "mileage", None
    if listing.registration_year not in s["registrations"]:
        return False, "registration_year", None
    d = distance_miles(s["centre"]["latitude"], s["centre"]["longitude"],
                       listing.latitude, listing.longitude)
    if d is not None and d > s["radius_miles"]:
        return False, "distance", d
    return True, "", d
