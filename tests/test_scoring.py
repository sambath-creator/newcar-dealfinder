from dealfinder.scoring import score_listing
from dealfinder.config import load_config
from dealfinder.models import VehicleListing

def test_good_enyaq_scores():
    cfg = load_config("config/config.yaml")
    l = VehicleListing(source="t", url="https://example.com", title="2025 Skoda Enyaq 85 Edition",
                       price_gbp=37000, mileage=1200, registration_year=2025,
                       latitude=51.45, longitude=0.22, seats=5, market_price_gbp=41000)
    d = score_listing(l,cfg,1)
    assert d.score > 70
    assert d.classification in {"BUY","NEGOTIATE"}

def test_seven_seat_bonus():
    cfg = load_config("config/config.yaml")
    l = VehicleListing(source="t", url="https://example.com", title="2025 Peugeot E-5008 GT",
                       price_gbp=39000, mileage=2000, registration_year=2025,
                       latitude=51.45, longitude=0.22, seats=7, market_price_gbp=42000)
    d = score_listing(l,cfg,1)
    assert "7-seat capability" in d.reasons
