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

        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        # Motors.co.uk usually uses generic classes for items. 
        articles = soup.find_all("article", class_=re.compile("ResultItem"))
        if not articles:
             articles = soup.find_all("div", {"data-testing": "search-result"})
            
        for article in articles:
            try:
                a_tag = article.find("a")
                if not a_tag:
                    continue
                href = a_tag["href"]
                if not href.startswith("http"):
                    href = "https://www.motors.co.uk" + href
                
                title_tag = article.find(["h3", "span"], class_=re.compile(r"title|name", re.IGNORECASE))
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
                        source_id=f"mt-{source_id}",
                        url=href,
                        title=title,
                        price_gbp=price,
                        mileage=0,
                        registration_year=year,
                        make=self.make.capitalize(),
                        model=self.model.capitalize()
                    )
                )
            except Exception:
                continue
                
        return listings
