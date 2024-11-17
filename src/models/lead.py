from typing import Any, List, Dict, Optional
from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str


class Task(BaseModel):
    id: int
    task_name: str
    scraper_name: str
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    created_at: str
    updated_at: str


class Query(BaseModel):
    id: int
    task_id: int
    query: str


class Competitor(BaseModel):
    id: int
    lead_id: int
    name: str
    link: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    main_category: Optional[str] = None


class Image(BaseModel):
    id: int
    lead_id: int
    link: str
    about: Optional[str] = None


class ReviewKeyword(BaseModel):
    id: int
    lead_id: int
    keyword: str
    count: int


class Hour(BaseModel):
    day: str
    times: List[str]


class About(BaseModel):
    id: Optional[str]
    name: Optional[str]
    options: List[Dict[str, bool]]


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None


class Lead(BaseModel):
    id: Optional[int] = None
    task_id: Optional[int] = None
    place_id: Optional[str] = None
    name: Optional[str] = None
    query: Optional[str] = None
    keyword: Optional[str] = None
    intent: Optional[str] = None
    score: Optional[float] = None
    scraper_name: Optional[str] = None
    filename: Optional[str] = None
    results: Optional[Dict] = None
    segmented_leads: Optional[Dict] = None
    description: Optional[str] = None
    is_spending_on_ads: Optional[bool] = None
    reviews: Optional[int] = None
    main_category: Optional[str] = None
    categories: List[str]
    rating: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    workday_timing: Optional[str] = None
    time_zone: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    address: Optional[Address | str] = None
    status: Optional[str] = None
    link: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class LeadsResult(BaseModel):
    count: Optional[int] = None
    total_pages: Optional[int] = None
    results: List[Lead]


class LeadSegmentation(BaseModel):
    segments: Dict[str, List[Dict[str, Any]]]


class SegmentationRule(BaseModel):
    name: str
    field: str  # Field to evaluate (e.g., "rating", "categories")
    operator: str  # Condition (e.g., ">", "contains", "==")
    value: Any  # Value to match against (e.g., 4.0, ["Consultant"])
    segment_name: str  # Name of the segment this rule applies to
    priority: int  # Priority of the segment
    sub_segments: Optional[List[Dict[str, Any]]] = None
