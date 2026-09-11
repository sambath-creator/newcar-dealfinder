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
                vehicle_id = car.get('vehicleId')
                price = car.get('price')
                if not price:
                    continue
                    
                year = car.get('vehicleYear')
                mileage = car.get('mileage', 0)
                make = car.get('make')
                model = car.get('model')
                variant = car.get('variant', '')
                title = f"{year} {make.capitalize()} {model.capitalize()} {variant}".strip()
                car_url = f"https://www.cinch.co.uk/used-cars/{make.lower()}/{model.lower()}/details/{vehicle_id}"
                
                features = [variant] if variant else []
                insurance_group = "N/A"
                try:
                    # Deep fetch for detailed features and insurance
                    det_resp = requests.get(car_url, timeout=5)
                    if det_resp.status_code == 200:
                        from bs4 import BeautifulSoup
                        import json
                        soup = BeautifulSoup(det_resp.text, 'html.parser')
                        script = soup.find('script', id='__NEXT_DATA__')
                        if script:
                            next_data = json.loads(script.string)
                            vd = next_data.get('props', {}).get('pageProps', {}).get('vehicleData', {})
                            if vd:
                                features = vd.get('features', features)
                                insurance_group = vd.get('insuranceGroupOneToFifty', insurance_group)
                except Exception as deep_e:
                    print(f"[DEBUG] Cinch deep fetch failed for {vehicle_id}: {deep_e}")
                    
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
                        insurance_group=str(insurance_group),
                        road_tax="£0", # EVs are currently £0
                        features=features
                    )
                )
            except Exception:
                continue

        return listings
