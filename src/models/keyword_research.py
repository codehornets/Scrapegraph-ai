from pydantic import BaseModel, HttpUrl
from typing import List


class CompetitorKeywordResearch(BaseModel):
    url: HttpUrl
    category: str
    main_keyword: str
    main_keyword_volume: int
    main_keyword_ranking: int
    best_keyword: str
    best_keyword_volume: int
    best_keyword_ranking: int
    organic_sessions: int
    backlinks: int
    domain_rating: float
    url_rating: float
    content_type: str
    referring_domains: int
    link_velocity: float
    primary_keywords: List[str]
    secondary_keywords: List[str]
    keyword_difficulty: float
    cost_per_click: float
    competitive_density: float
    search_intent: str
    top_competitors: List[str]
    serp_features: List[str]
