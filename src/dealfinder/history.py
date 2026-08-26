import sqlite3
from pathlib import Path
from .models import ScoredDeal

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
  fingerprint TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_id TEXT,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  price REAL NOT NULL,
  mileage INTEGER NOT NULL,
  registration_year INTEGER NOT NULL,
  score REAL NOT NULL,
  classification TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);
"""

def fingerprint(deal: ScoredDeal) -> str:
    l = deal.listing
    raw = f"{l.source}|{l.source_id or l.url}|{l.title}".lower().strip()
    import hashlib
    return hashlib.sha256(raw.encode()).hexdigest()

class History:
    def __init__(self, path="data/deals.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(SCHEMA)
        self.db.commit()

    def upsert(self, deal: ScoredDeal):
        fp = fingerprint(deal)
        l = deal.listing
        now = l.first_seen.isoformat()
        self.db.execute("""
        INSERT INTO listings
        (fingerprint,source,source_id,url,title,price,mileage,registration_year,score,classification,first_seen,last_seen)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(fingerprint) DO UPDATE SET
          price=excluded.price, mileage=excluded.mileage, score=excluded.score,
          classification=excluded.classification, last_seen=excluded.last_seen
        """, (fp,l.source,l.source_id,l.url,l.title,l.price_gbp,l.mileage,l.registration_year,
              deal.score,deal.classification,now,now))
        self.db.commit()

    def close(self):
        self.db.close()
