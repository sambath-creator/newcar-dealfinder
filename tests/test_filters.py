from dealfinder.filters import eligible
from dealfinder.models import VehicleListing
from dealfinder.config import load_config

def listing(**kwargs):
    base = dict(source="t",url="https://example.com",title="Skoda Enyaq 85",
                price_gbp=38000,mileage=2000,registration_year=2025,
                latitude=51.45,longitude=0.22)
    base.update(kwargs)
    return VehicleListing(**base)

def test_eligible():
    cfg = load_config("config/config.yaml")
    ok, reason, _ = eligible(listing(), cfg)
    assert ok
    assert reason == ""

def test_price_rejected():
    cfg = load_config("config/config.yaml")
    ok, reason, _ = eligible(listing(price_gbp=45000), cfg)
    assert not ok and reason == "price"

def test_mileage_rejected():
    cfg = load_config("config/config.yaml")
    ok, reason, _ = eligible(listing(mileage=5001), cfg)
    assert not ok and reason == "mileage"
