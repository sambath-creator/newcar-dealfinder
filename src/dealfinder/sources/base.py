from abc import ABC, abstractmethod
from ..models import VehicleListing
import requests
import os
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright

class ListingSource(ABC):
    name = "base"

    def fetch_html(self, url: str) -> str:
        api_key = os.environ.get("SCRAPER_API_KEY")
        
        with sync_playwright() as p:
            # If we have an API key, use ScraperAPI proxy
            if api_key:
                proxy_settings = {
                    "server": "http://proxy-server.scraperapi.com:8001",
                    "username": "scraperapi",
                    "password": api_key
                }
                browser = p.chromium.launch(proxy=proxy_settings, headless=True)
            else:
                browser = p.chromium.launch(headless=True)
                
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            
            try:
                # wait_until="domcontentloaded" is faster, but "networkidle" guarantees React has loaded
                page.goto(url, wait_until="networkidle", timeout=60000)
                html = page.content()
            except Exception as e:
                print(f"[DEBUG] Playwright failed to fetch {url}: {e}")
                html = ""
            finally:
                browser.close()
                
            return html

    @abstractmethod
    def collect(self) -> list[VehicleListing]:
        """Return permitted/public vehicle listings."""
        raise NotImplementedError
