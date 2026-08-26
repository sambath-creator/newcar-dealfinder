from .base import ListingSource
from ..models import VehicleListing

class DemoSource(ListingSource):
    name = "demo"

    def collect(self):
        return [
            VehicleListing(
                source=self.name,
                source_id="demo-enyaq-001",
                url="https://example.com/enyaq",
                title="2025 Skoda Enyaq 85 Edition",
                price_gbp=37995,
                mileage=2200,
                registration_year=2025,
                latitude=51.48,
                longitude=0.05,
                dealer="Demo Skoda Dealer",
                location="London",
                seats=5,
                propulsion="BEV",
                make="Skoda",
                model="Enyaq",
                trim="85 Edition",
                market_price_gbp=41000,
                specification_score=90,
                dealer_score=90,
                image_url="https://images.unsplash.com/photo-1629897048514-3dd741428f58?q=80&w=600&auto=format&fit=crop",
            ),
            VehicleListing(
                source=self.name,
                source_id="demo-jaecoo-001",
                url="https://example.com/jaecoo",
                title="2026 JAECOO 7 SHS-P Luxury",
                price_gbp=27995,
                mileage=1800,
                registration_year=2026,
                latitude=51.75,
                longitude=0.10,
                dealer="Demo JAECOO Dealer",
                location="Essex",
                seats=5,
                propulsion="PHEV",
                make="JAECOO",
                model="7",
                trim="SHS-P Luxury",
                market_price_gbp=31000,
                specification_score=88,
                dealer_score=85,
                image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=600&auto=format&fit=crop",
            ),
        ]
