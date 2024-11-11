import traceback
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from src.services.scrapers.leads.api import Api, ApiException
from src.config.settings import SettingService
from src.services.caches import CacheService
from src.utils.debug import die


class SearchQuery(BaseModel):
    query: str


class GoogleMapsScraperService:
    def __init__(
        self,
        settings: SettingService,
        marketing_strategy: str,
        locations: List[str],
        industry: str,
        company_name: str,
        min_rating: float = 4.0,
        max_reviews: int = 50,
        review_sort: str = "newest",
        api: Optional[Api] = None,
    ):
        self.setting_service = settings
        self.marketing_strategy = marketing_strategy
        self.base_city = locations[0]  # TODO: Extend for multiple locations
        self.industry = industry
        self.company_name = company_name
        self.min_rating = min_rating
        self.max_reviews = max_reviews
        self.review_sort = review_sort

        self.api = api if api else Api()
        self.cache_service = CacheService(settings=self.setting_service)

    def generate_leads(
        self,
        seo_keywords: List[Tuple[str, str, float]],
        max_results: int = 100,
        enable_reviews_extraction: bool = False,
        zoom_level: int = 14,
        max_keywords: int = 1000,  # TODO: Optional limit on the number of keywords processed remove
    ) -> List[Dict[str, Any]]:
        all_leads = []
        lead_tracking = []  # To store leads with associated metadata

        # Limit the number of keywords processed if max_keywords is specified
        keywords_to_process = (
            seo_keywords[:max_keywords] if max_keywords else seo_keywords
        )

        for keyword, intent, score in keywords_to_process:
            cache_key = self.cache_service.generate_cache_key(
                f"{keyword}_{intent}_{self.industry}_{self.base_city}_{self.marketing_strategy}"
            )
            queries = self.cache_service.load_from_cache(
                cache_key, cache_dir=self.setting_service.gmaps_queries_dir
            ) or self.gpt_generate_search_query(
                keyword=keyword,
                intent=intent,
                business_type=self.industry,
            )
            self.cache_service.save_to_cache(
                cache_key,
                cache_dir=self.setting_service.gmaps_queries_dir,
                data=queries,
            )

            validated_queries = [
                query for query in queries if self.validate_query(query)
            ]

            found_leads = []
            for query in validated_queries:
                leads = self.search_places(
                    query=query,
                    max_results=max_results,
                    enable_reviews_extraction=enable_reviews_extraction,
                    zoom_level=zoom_level,
                )
                leads = leads["results"]
                found_leads.extend(leads)

                lead_with_metadata = {
                    "lead_data": leads,
                    "keyword": keyword,
                    "intent": intent,
                    "score": score,
                    "query": query,
                }

                lead_tracking.append(lead_with_metadata)
                all_leads.append(leads)

        return lead_tracking, all_leads

    def gpt_generate_search_query(
        self,
        keyword: str,
        intent: str,
        business_type: Optional[str] = None,
        marketing_strategy: Optional[str] = "general lead generation",
    ) -> List[str]:
        cache_key = self.cache_service.generate_cache_key(
            f"{keyword}_{intent}_{self.industry}_{self.base_city}_{self.marketing_strategy}"
        )
        search_queries = self.cache_service.load_from_cache(
            cache_key, cache_dir=self.setting_service.gmaps_queries_dir
        )

        if search_queries:
            return search_queries

        try:
            prompt = f"""
            As a marketing expert, generate several Google Maps search queries based on the following details:
            - Keyword: {keyword}
            - Location: {self.base_city}
            - Industry: {business_type or "General"}
            - Marketing Strategy: {marketing_strategy}
            - Search Intent: {intent}
            
            Each query should be highly relevant to the marketing strategy and intent, reflecting phrases and language common to local search in Google Maps.
            Example queries:
            - "{keyword} {business_type} in {self.base_city}"
            - "Highly-rated {business_type} for {keyword} near {self.base_city}"
            """

            search_queries = self.setting_service.openai.chat.completions.create(
                model="gpt-4o",
                response_model=SearchQuery,
                messages=[
                    {"role": "system", "content": "You are a marketing expert."},
                    {"role": "user", "content": prompt},
                ],
            )

            search_queries = [line for line in search_queries.query.split("\n") if line]
            if not search_queries:
                print(
                    "Warning: No queries generated by LLM; using fallback query method."
                )
                return self.build_query(keyword, intent, business_type)

            self.cache_service.save_to_cache(
                cache_key,
                cache_dir=self.setting_service.gmaps_queries_dir,
                data=search_queries,
            )

            return search_queries
        except Exception as e:
            print(f"LLM query generation failed: {e}")
            return self.build_query(keyword, intent, business_type)

    def build_query(
        self,
        keyword: str,
        intent: str,
        business_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_reviews: Optional[int] = None,
    ) -> List[str]:
        queries = []
        modifiers = self.setting_service.gmaps_search_query_intent_modifiers.get(
            intent, []
        )
        for modifier in modifiers:
            modified_keyword = f"{modifier} {keyword}"
            query_parts = [modified_keyword]
            if business_type:
                query_parts.append(business_type)
            query_parts.append(f"in {self.base_city}")
            if min_rating:
                query_parts.append(f"with rating above {min_rating}")
            if max_reviews:
                query_parts.append(f"up to {max_reviews} reviews")
            queries.append(" ".join(query_parts))

        base_query = f"{keyword} in {self.base_city}"
        if business_type:
            base_query += f" for {business_type}"
        if min_rating:
            base_query += f" with rating above {min_rating}"
        queries.append(base_query)

        return queries

    def validate_query(self, query: str) -> bool:
        return 10 <= len(query) <= 80

    def search_places(
        self,
        query: str,
        country: str = None,
        business_type: str = "",
        max_cities: int = None,
        randomize_cities: bool = True,
        max_reviews: int = 20,
        reviews_sort: str = "newest",
        language: str = None,
        max_results: int = None,
        enable_reviews_extraction: bool = True,
        coordinates: str = "",
        zoom_level: int = 14,
    ) -> List[Dict[str, Any]]:
        data = {
            "queries": [query],
            "country": country,
            "business_type": business_type,
            "max_cities": max_cities,
            "randomize_cities": randomize_cities,
            "api_key": self.setting_service.gmaps_api_key,
            "enable_reviews_extraction": enable_reviews_extraction,
            "max_reviews": max_reviews,
            "reviews_sort": reviews_sort,
            "lang": language,
            "max_results": max_results,
            "coordinates": coordinates,
            "zoom_level": zoom_level,
        }

        # cache_key = self.cache_service.generate_cache_key(data)
        # cached_result = self.cache_service.load_from_cache(
        #     cache_key, cache_dir=self.setting_service.gmaps_queries_dir
        # )
        # if cached_result:
        #     print(f"Cache hit for query: {query}")
        #     return cached_result

        result = self.execute_task(query, data)

        # self.cache_service.save_to_cache(
        #     cache_key,
        #     cache_dir=self.setting_service.gmaps_queries_dir,
        #     data=result,
        # )

        return result

    def execute_task(self, query: str, data, scraper_name="google_maps_scraper"):
        try:
            task_list = self.api.create_sync_task(data, scraper_name=scraper_name)
            if not task_list:
                print(f"Failed to create task for query: {query}")
                return []
            task = (
                task_list[0] if isinstance(task_list, list) and task_list else task_list
            )
            task = self.api.get_task(task["id"])
            results = self.api.get_task_results(task["id"])

            results_bytes, filename = self.api.download_task_results(
                task["id"], format="csv"
            )
            self.api.abort_task(task["id"])
            self.api.delete_task(task["id"])

            # store_lead(query, scraper_name, results, filename)

            return {
                "query": query,
                "data": data,
                "scraper_name": scraper_name,
                "task": task,
                "results": results,
                "results_bytes": results_bytes,
                "filename": filename,
            }
        except ApiException as e:
            raise RuntimeError(f"API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")


# -----------------------------------------------------------------------------
# TESTING EXAMPLE
# -----------------------------------------------------------------------------

# test_data: List[Tuple[str, str, float]] = [
#     ("product discovery", "informational", 0.458),
#     ("product discovery process", "informational", 0.458),
#     ("product discovery jira", "informational", 0.458),
# ]

# scraper_service = GoogleMapsScraperService(
#     settings=SettingService(),
#     marketing_strategy="general lead generation",
#     locations=["us", "ca"],
#     industry="consulting",
#     company_name="Code Hornets",
# )

# leads = scraper_service.generate_leads(seo_keywords=test_data)
# die(f"Lead generation complete. Total leads: {len(leads)}")

# -----------------------------------------------------------------------------
# END OF FILE
# -----------------------------------------------------------------------------
