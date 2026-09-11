import requests
from .base import ListingSource
from ..models import VehicleListing

class CinchSource(ListingSource):
    name = "cinch"

    def __init__(self, make="Skoda", model="Enyaq"):
        self.make = make.lower()
        self.model = model.lower().replace(" ", "-")

    def collect(self) -> list[VehicleListing]:
        url = f"https://search-api.snc-prod.aws.cinch.co.uk/used-cars?url={self.make}%2F{self.model}"
        try:
            resp = requests.get(url, timeout=15)
            data = resp.json()
        except Exception as e:
            print(f"[DEBUG] CinchSource failed to fetch: {e}")
            return []

        listings = []
        for car in data.get("vehicleListings", []):
            try:
                vehicle_id = car.get("vehicleId")
                price = car.get("price")
                year = car.get("vehicleYear")
                mileage = car.get("mileage", 0)
                make = car.get("make")
                model = car.get("model")
                variant = car.get("variant", "")
                
                title = f"{year} {make} {model} {variant}".strip()
                car_url = f"https://www.cinch.co.uk/used-cars/{self.make}/{self.model}/details/{vehicle_id}"

                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"cinch-{vehicle_id}",
                        url=car_url,
                        title=title,
                        price_gbp=price,
                        mileage=mileage,
                        registration_year=year,
                        make=make,
                        model=model,
                        fuel_type=car.get('fuelType', 'Unknown'),
                        insurance_group="N/A",
                        road_tax="£0", # EVs are currently £0
                        features=[variant] if variant else []
                    )
                )
            except Exception:
                continue

        return listings
