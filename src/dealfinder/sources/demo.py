from .base import ListingSource
from ..models import VehicleListing

class DemoSource(ListingSource):
    name = "demo"
    def collect(self):
        return [
            VehicleListing(
                source=self.name,
                source_id="demo-modely-001",
                url="https://example.com/modely",
                title="2026 Tesla Model Y Long Range AWD",
                price_gbp=38500,
                mileage=45,
                registration_year=2026,
                latitude=51.50,
                longitude=0.12,
                dealer="Demo Tesla Centre",
                location="London",
                seats=5,
                propulsion="BEV",
                make="Tesla",
                model="Model Y",
                trim="Long Range",
                market_price_gbp=42000,
                specification_score=95,
                dealer_score=90,
                image_url="https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=600&auto=format&fit=crop",
            ),
            VehicleListing(
                source=self.name,
                source_id="demo-ev5-001",
                url="https://example.com/ev5",
                title="2026 Kia EV5 Air",
                price_gbp=32000,
                mileage=10,
                registration_year=2026,
                latitude=51.75,
                longitude=0.10,
                dealer="Demo Kia Dealership",
                location="Essex",
                seats=5,
                propulsion="BEV",
                make="Kia",
                model="EV5",
                trim="Air",
                market_price_gbp=35000,
                specification_score=88,
                dealer_score=85,
                image_url="https://images.unsplash.com/photo-1619682817481-e994891cd1f5?q=80&w=600&auto=format&fit=crop",
            ),
        ]
