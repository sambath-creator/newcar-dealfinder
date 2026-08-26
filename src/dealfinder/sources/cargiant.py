import requests
from bs4 import BeautifulSoup
from .base import ListingSource
from ..models import VehicleListing
import re

class CargiantSource(ListingSource):
    name = "cargiant"

    def __init__(self, make="skoda", model="enyaq-iv"):
        self.make = make.lower()
        self.model = model.lower()

    def collect(self):
        url = f"https://www.cargiant.co.uk/search/{self.make}/{self.model}"
        try:
            html = self.fetch_html(url)
        except Exception:
            return []

        soup = BeautifulSoup(html, "html.parser")
        listings = []
        
        articles = soup.find_all("div", class_=re.compile(r"car-listing-item|product-card|vehicle-card", re.IGNORECASE))
        if not articles:
             articles = soup.find_all("a", href=re.compile(r"/car/" + self.make, re.IGNORECASE))

        for article in articles:
            try:
                if article.name == "a":
                    href = article["href"]
                else:
                    a_tag = article.find("a", href=True)
                    if not a_tag:
                        continue
                    href = a_tag["href"]
                    
                if not href.startswith("http"):
                    href = "https://www.cargiant.co.uk" + href
                    
                title_tag = article.find(["h3", "h2", "span"], class_=re.compile(r"title|name", re.IGNORECASE))
                title = title_tag.text.strip() if title_tag else f"{self.make.capitalize()} {self.model.capitalize()}"
                
                price_text = ""
                price_match = re.search(r'£\d+,\d+', article.text)
                if price_match:
                    price_text = price_match.group(0)
                else:
                    continue
                    
                price = int(re.sub(r'[^\d]', '', price_text))
                
                img_tag = article.find("img")
                img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else None
                if img_url and not img_url.startswith("http"):
                    img_url = "https://www.cargiant.co.uk" + img_url
                
                source_id = href.split("/")[-1].split("?")[0]
                
                listings.append(
                    VehicleListing(
                        source=self.name,
                        source_id=f"cg-{source_id}",
                        url=href,
                        title=title,
                        price_gbp=price,
                        mileage=0,
                        registration_year=2023,
                        make=self.make.capitalize(),
                        model=self.model.capitalize(),
                        image_url=img_url,
                        dealer="Cargiant"
                    )
                )
            except Exception:
                continue
                
        return listings
