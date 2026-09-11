import requests
import json
import urllib.parse
from .base import ListingSource
from ..models import VehicleListing

class ArnoldClarkSource(ListingSource):
    name = "arnoldclark"

    def __init__(self, make="skoda", model="enyaq"):
        self.make = make.lower()
        self.model = model.lower()

    def collect(self) -> list[VehicleListing]:
        url = 'https://6g8av9ejjr-dsn.algolia.net/1/indexes/*/queries'
        params = {
            'x-algolia-api-key': 'MTVkZTY3YWJiMjhlZTlkODdiZTk2NWQ4Yjg3OGEyMzAxNjBiMmQyNWJjYzA5YzNmZWQyN2JmOGM2NGQzZDNjNnVzZXJUb2tlbj0mdmFsaWRVbnRpbD0xNzg5MjE3NjQy',
            'x-algolia-application-id': '6G8AV9EJJR'
        }
        headers = {'Referer': 'https://www.arnoldclark.com/', 'Origin': 'https://www.arnoldclark.com'}
        
        search_query = f"{self.make} {self.model}"
        payload = {
            'requests': [
                {
                    'indexName': 'prd_vehicleRecords_en',
                    'params': f"query={urllib.parse.quote(search_query)}&hitsPerPage=1000"
                }
            ]
        }

        try:
            resp = requests.post(url, headers=headers, params=params, json=payload, timeout=15)
            data = resp.json()
        except Exception as e:
            print(f"[DEBUG] ArnoldClarkSource failed to fetch: {e}")
            return []

        listings = []
        if 'results' not in data or not data['results']:
            return []
            
        for hit in data['results'][0].get('hits', []):
            try:
                vehicle_id = hit.get('objectID')
                price = hit.get('cashPrice')
                if not price:
                    continue
                    
                year = hit.get('year')
                mileage = hit.get('mileage', 0)
                
                title_info = hit.get('titleInfo', {})
                name = title_info.get('name', f"{year} {self.make.capitalize()} {self.model.capitalize()}").replace('\ufffd', 'S')
                variant = title_info.get('variant', '')
                title = f"{name} {variant}".strip()
                
                car_url = hit.get('url')
                if not car_url.startswith("http"):
                    car_url = f"https://www.arnoldclark.com{car_url}"

                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"ac-{vehicle_id}",
                        url=car_url,
                        title=title,
                        price_gbp=price,
                        mileage=mileage,
                        registration_year=year,
                        make=self.make.capitalize(),
                        model=self.model.capitalize()
                    )
                )
            except Exception:
                continue

        return listings
