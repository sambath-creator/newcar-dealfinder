from abc import ABC, abstractmethod
from ..models import VehicleListing
import requests
import os
from urllib.parse import urlencode

class ListingSource(ABC):
    name = "base"

    def fetch_html(self, url: str) -> str:
        api_key = os.environ.get("SCRAPER_API_KEY")
        if api_key:
            payload = {'api_key': api_key, 'url': url, 'render': 'true'}
            proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
            resp = requests.get(proxy_url, timeout=45)
        else:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
            resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text

    @abstractmethod
    def collect(self) -> list[VehicleListing]:
        """Return permitted/public vehicle listings."""
        raise NotImplementedError
