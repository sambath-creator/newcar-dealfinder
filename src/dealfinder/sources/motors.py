import requests
from bs4 import BeautifulSoup
from .base import ListingSource
from ..models import VehicleListing
import re

class MotorsSource(ListingSource):
    name = "motors"

    def __init__(self, make="skoda", model="enyaq", postcode="DA11AA", radius=100):
        self.make = make.lower()
        self.model = model.lower()
        self.postcode = postcode
        self.radius = radius

    def collect(self):
        url = f"https://www.motors.co.uk/{self.make}/{self.model}/used-cars/"
        try:
            html = self.fetch_html(url)
        except Exception:
            return []

        import json
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        # Motors.co.uk embeds the actual car listings inside schema.org JSON-LD blocks!
        script_tags = soup.find_all("script", type="application/ld+json")
        for tag in script_tags:
            if not tag.string:
                continue
            try:
                data = json.loads(tag.string)
            except:
                continue
                
            # data could be a list or dict
            if isinstance(data, dict):
                data = [data]
                
            for block in data:
                # Some are wrapped in ItemList
                if block.get("@type") == "ItemList":
                    items = [i.get("item", {}) for i in block.get("itemListElement", [])]
                else:
                    items = [block]
                    
                for item in items:
                    if item.get("@type") != "Product":
                        continue
                    
                    title = item.get("name", "")
                    url = item.get("url", "")
                    if not url or not title:
                        continue
                        
                    offers = item.get("offers", {})
                    price = offers.get("price")
                    if not price:
                        continue
                        
                    # Try to infer registration year
                    year = 2025 # Default
                    for y in [2026, 2025, 2024, 2023, 2022]:
                        if str(y) in title:
                            year = y
                            break
                            
                    source_id = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
                    
                    listings.append(
                        VehicleListing(
                            source=self.name,
                            source_id=f"mt-{source_id}",
                            url=url,
                            title=title,
                            price_gbp=int(price),
                            mileage=0, # Need deeper scraping for mileage
                            registration_year=year,
                            make=self.make.capitalize(),
                            model=self.model.capitalize()
                        )
                    )
                    
        return listings
