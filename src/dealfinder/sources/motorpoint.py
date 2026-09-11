import requests
import json
from bs4 import BeautifulSoup
from .base import ListingSource
from ..models import VehicleListing

class MotorpointSource(ListingSource):
    name = "motorpoint"

    def __init__(self, make="tesla", model="model y"):
        self.make = make.lower()
        self.model = model.lower()

    def collect(self) -> list[VehicleListing]:
        url = f"https://www.motorpoint.co.uk/vehicle-search/{self.make}/{self.model.replace(' ', '-')}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return []
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if not script:
                return []
                
            data = json.loads(script.string)
            vehicles = data.get('props', {}).get('pageProps', {}).get('initialSearch', {}).get('vehicles', [])
        except Exception as e:
            print(f"[DEBUG] MotorpointSource failed to fetch: {e}")
            return []

        listings = []
        for v in vehicles:
            try:
                vehicle_id = v.get('VehicleId')
                price = v.get('CurrentPrice')
                if not price:
                    continue
                    
                year = v.get('RegYear')
                mileage = v.get('Mileage', 0)
                make = v.get('Make', self.make.capitalize())
                model = v.get('Model', self.model.capitalize())
                trim = v.get('Trim', '')
                title = f"{year} {make} {model} {trim}".strip()
                car_url = v.get('VehicleAdvertUrl', '')
                if not car_url.startswith('http'):
                    car_url = f"https://www.motorpoint.co.uk{car_url}"

                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"mp-{vehicle_id}",
                        url=car_url,
                        title=title,
                        price_gbp=price,
                        mileage=mileage,
                        registration_year=year,
                        make=make,
                        model=model,
                        fuel_type=v.get('FuelType', 'Unknown'),
                        insurance_group=v.get('InsuranceGroup', 'N/A'),
                        road_tax="£0", # EVs are currently £0
                        features=[trim] if trim else []
                    )
                )
            except Exception:
                continue

        return listings
