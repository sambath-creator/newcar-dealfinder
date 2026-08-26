import requests
from bs4 import BeautifulSoup

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = "https://www.autotrader.co.uk/car-search?postcode=DA11AA&radius=100&make=Skoda&model=Enyaq&sort=relevance"
    
    print("Fetching AutoTrader HTML...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for script tags with NEXT_DATA or APOLLO_STATE which usually contain the cars
        print("Looking for JSON blobs in script tags...")
        for script in soup.find_all("script"):
            if script.string and ("AT_APOLLO_STATE" in script.string or "NEXT_DATA" in script.string or "window.AT_SPA" in script.string):
                print("-" * 40)
                print(script.string[:500] + "\n... [TRUNCATED] ...")
        
        # Save full HTML
        with open("autotrader_dump.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
            
        print("\nSaved full HTML to autotrader_dump.html")
        print("Please upload or paste a small portion of it to the AI so it can fix the parser!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
