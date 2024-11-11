from typing import List, Optional, Dict

from pydantic import BaseModel


class GmapsPlace(BaseModel):
    place_id: str
    name: str
    description: Optional[str]
    reviews: int
    competitors: List[Dict]
    website: Optional[str]
    can_claim: bool
    owner: Dict
    featured_image: Optional[str]
    main_category: Optional[str]
    categories: List[str]
    rating: float
    workday_timing: Optional[str]
    closed_on: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    review_keywords: List[Dict]
    link: str
    status: Optional[str]
    price_range: Optional[str]
    reviews_per_rating: Dict[int, int]
    featured_question: Optional[Dict]
    reviews_link: str
    coordinates: Dict[str, float]
    plus_code: Optional[str]
    detailed_address: Dict[str, Optional[str]]
    time_zone: Optional[str]
    cid: Optional[str]
    data_id: Optional[str]
    menu: Optional[Dict]
    reservations: List[Dict]
    order_online_links: List[Dict]
    about: List[Dict]
    images: List[Dict]
    hours: List[Dict]
    most_popular_times: List[Dict]
    popular_times: Dict[str, List[Dict]]
    featured_reviews: List[Dict]