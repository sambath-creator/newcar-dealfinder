import requests
from bs4 import BeautifulSoup
from .base import ListingSource
from ..models import VehicleListing
import urllib.parse
import re

class AutoTraderSource(ListingSource):
    name = "autotrader"

    def __init__(self, postcode="DA11AA", radius=100, make="Skoda", model="Enyaq"):
        self.postcode = postcode
        self.radius = radius
        self.make = make
        self.model = model

    def collect(self):
        url = f"https://www.autotrader.co.uk/car-search?postcode={self.postcode}&radius={self.radius}&make={self.make}&model={self.model}&sort=relevance"
        try:
            html = self.fetch_html(url)
        except Exception:
            return []

        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        # This is a generic parser for demonstration. AutoTrader HTML structure changes frequently.
        # Currently, they often use a specific data attribute for listings.
        articles = soup.find_all("section", {"data-testid": "regular-adverts"})
        if not articles:
            articles = soup.find_all("article")
            
        for article in articles:
            try:
                link_tag = article.find("a", href=True)
                if not link_tag:
                    continue
                
                href = link_tag["href"]
                if not href.startswith("http"):
                    href = "https://www.autotrader.co.uk" + href
                    
                # Clean URL
                href = href.split("?")[0]
                
                title_tag = article.find(["h3", "h2"])
                title = title_tag.text.strip() if title_tag else f"{self.make} {self.model}"
                
                price_tag = article.find(text=re.compile(r'£\d+,\d+'))
                if not price_tag:
                    continue
                price = int(re.sub(r'[^\d]', '', price_tag.text))
                
                # We need to extract an ID from the URL
                source_id = href.split("/")[-1]
                
                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"at-{source_id}",
                        url=href,
                        title=title,
                        price_gbp=price,
                        mileage=0,  # Default, need deeper scraping to parse mileage reliably
                        registration_year=2023, # Default
                        make=self.make,
                        model=self.model,
                    )
                )
            except Exception:
                continue
                
        return listings
