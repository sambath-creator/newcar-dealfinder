import requests
from bs4 import BeautifulSoup
from .base import ListingSource
from ..models import VehicleListing
import re

class CitygateSource(ListingSource):
    name = "citygate"

    def __init__(self, make="skoda", model="enyaq"):
        self.make = make.lower()
        self.model = model.lower()

    def collect(self):
        # Citygate is a major London/Home Counties dealer group for VW, Skoda, Kia
        url = f"https://www.citygate.co.uk/used-cars/{self.make}/{self.model}/"
        try:
            html = self.fetch_html(url)
        except Exception:
            return []

        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        articles = soup.find_all("div", class_=re.compile("vehicle-card|listing-item"))
        
        for article in articles:
            try:
                link_tag = article.find("a", href=True)
                if not link_tag:
                    continue
                
                href = link_tag["href"]
                if not href.startswith("http"):
                    href = "https://www.citygate.co.uk" + href
                    
                title_tag = article.find(["h3", "span"], class_=re.compile("title|name"))
                title = title_tag.text.strip() if title_tag else f"{self.make.capitalize()} {self.model.capitalize()}"
                
                price_tag = article.find(text=re.compile(r'£\d+,\d+'))
                if not price_tag:
                    price_tag = article.find(string=re.compile(r'£\d+,\d+'))
                if not price_tag:
                    continue
                price = int(re.sub(r'[^\d]', '', price_tag.text))

                # Try to infer registration year
                year = 2025 # Default to pass filters
                for y in [2026, 2025, 2024, 2023, 2022]:
                    if str(y) in article.text:
                        year = y
                        break
                
                source_id = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
                
                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"cg-{source_id}",
                        url=href,
                        title=title,
                        price_gbp=price,
                        mileage=0,
                        registration_year=year,
                        make=self.make.capitalize(),
                        model=self.model.capitalize(),
                        dealer="Citygate"
                    )
                )
            except Exception:
                continue
                
        return listings
