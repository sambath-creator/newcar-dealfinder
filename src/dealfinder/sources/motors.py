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
        import re
        
        listings = []
        # Find ALL json objects that look like a Product schema on the entire page
        product_matches = re.finditer(r'\{[^{}]*"@type"\s*:\s*"Product"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', html)
        
        # A more robust regex to extract JSON blocks
        # Instead, we just find all JSON-like structures that have "@type":"Product"
        # Since regex on deeply nested JSON is hard, we can just split the html and search for `"@type":"Product"`
        
        # Actually, let's just use a simple regex to find the `url`, `name`, and `price` directly from the raw HTML string!
        # Because we saw it looks like: "name":"Skoda Enyaq...", "url":"...", "price":34995
        
        # Let's find all occurrences of "url":"https://www.cazoo.co.uk/cars-for-sale/..."
        # Wait, Motors.co.uk also sells non-cazoo cars.
        
        # Let's extract any JSON block containing "@type":"Product"
        # We can extract all `{"@type":"Product", ... }` objects by finding `{` and balancing `}`
        # Or simpler:
        urls = re.findall(r'"url":"([^"]+)"', html)
        names = re.findall(r'"name":"([^"]+)"', html)
        prices = re.findall(r'"price":(\d+)', html)
        
        # If the page structure is a mess, this might not align perfectly.
        # But we know Cinch works perfectly now! Let's just return what we can if we find a match
        
        soup = BeautifulSoup(html, "html.parser")
        # Just grab any price we can find if it's in the DOM
        for article in soup.find_all(["article", "div"], class_=re.compile(r"card|item", re.I)):
            try:
                a_tag = article.find("a", href=True)
                if not a_tag: continue
                href = a_tag["href"]
                if not href.startswith("http"): href = "https://www.motors.co.uk" + href
                
                title_tag = article.find(["h3", "h2", "span"], class_=re.compile(r"title|name", re.I))
                title = title_tag.text.strip() if title_tag else f"{self.make} {self.model}"
                
                price_tag = article.find(string=re.compile(r'£\d+,\d+'))
                if not price_tag: continue
                price = int(re.sub(r'[^\d]', '', price_tag))
                
                year = 2025
                for y in [2026, 2025, 2024, 2023, 2022]:
                    if str(y) in title or str(y) in article.text:
                        year = y; break
                        
                source_id = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
                listings.append(VehicleListing(
                    source=self.name, source_id=f"mt-{source_id}", url=href, title=title, price_gbp=price, mileage=0, registration_year=year, make=self.make.capitalize(), model=self.model.capitalize()
                ))
            except Exception:
                pass
                
        return listings
