from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class VehicleListing:
    source: str
    url: str
    title: str
    price_gbp: float
    mileage: int
    registration_year: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    dealer: str = ""
    location: str = ""
    seats: Optional[int] = None
    propulsion: str = ""
    make: str = ""
    model: str = ""
    trim: str = ""
    market_price_gbp: Optional[float] = None
    warranty_score: Optional[float] = None
    dealer_score: Optional[float] = None
    specification_score: Optional[float] = None
    source_id: str = ""
    image_url: Optional[str] = None
    fuel_type: str = "Unknown"
    insurance_group: str = "N/A"
    road_tax: str = "N/A"
    features: list[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ScoredDeal:
    listing: VehicleListing
    distance_miles: float
    discount_pct: float
    score: float
    classification: str
    reasons: list[str]
    effective_changeover_gbp: Optional[float] = None
    original_list_price_gbp: Optional[float] = None
