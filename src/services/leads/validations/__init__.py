import json
import json
from typing import Any, Dict

from scrapegraphai.graphs.smart_scraper_multi_graph import SmartScraperMultiGraph
from src.config.settings import SettingService
from src.services.caches import CacheService
from src.utils.debug import die


class LeadValidationService:
    def __init__(self, setting_service: SettingService, cache_service: CacheService):
        self.setting_service = setting_service
        self.cache_service = cache_service

    def validate_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        enriched_data = {}

        if lead.get("name"):
            enriched_data.update(self.fetch_opencorporates_data(lead.get("name")))

        # # WhoisXML API for domain information
        # if lead.get("website"):
        #     enriched_data.update(self.fetch_whois_data(lead.get("website")))

        # # FullContact API for social media and demographic enrichment
        # if lead.get("phone"):
        #     enriched_data.update(self.fetch_fullcontact_data(lead.get("phone")))

        # # Google My Business for enhanced business details
        # if lead.get("place_id"):
        #     enriched_data.update(self.fetch_google_business_data(lead.get("place_id")))

        # lead.update(enriched_data)

        # # Perform additional analysis for enrichment
        # lead["intent"] = self.analyze_intent(lead)
        # lead["competitor_proximity"] = self.analyze_competitor_proximity(lead)
        # lead["industry_vertical_alignment"] = self.analyze_industry_vertical_alignment(
        #     lead
        # )
        # lead["ads_spending_patterns"] = self.analyze_ads_spending_patterns(lead)
        # lead["business_size"] = self.analyze_business_size(lead)
        # lead["engagement_level"] = self.analyze_engagement_level(lead)
        # lead["marketing_goals"] = self.analyze_marketing_goals(lead)
        # lead["marketing_strategies"] = self.analyze_marketing_strategies(lead)

        return lead

    def fetch_opencorporates_data(self, company_name: str) -> dict:
        search_url = (
            f"https://opencorporates.com/companies?q={company_name.replace(' ', '+')}"
        )

        prompt = (
            "Extract the following information for the first company listed on the page:\n"
            "- Registered Name\n"
            "- Incorporation Date\n"
            "- Jurisdiction\n"
            "- Company Number\n"
            "Provide the information in JSON format."
        )

        scraper = SmartScraperMultiGraph(
            prompt=prompt,
            source=[search_url],
            config=self.setting_service.scrapegraphai_config,
        )
        result = scraper.run()

        die(result)

        try:
            company_data = json.loads(result)
            return {
                "registered_name": company_data.get("Registered Name"),
                "incorporation_date": company_data.get("Incorporation Date"),
                "jurisdiction": company_data.get("Jurisdiction"),
                "company_number": company_data.get("Company Number"),
            }
        except json.JSONDecodeError:
            print("Failed to parse the response.")
            return {}

    # def fetch_whois_data(self, domain: str) -> Dict[str, Any]:
    #     """Fetch domain data from WhoisXML API."""
    #     url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService"
    #     params = {
    #         "domainName": domain,
    #         "apiKey": self.setting_service.whoisxml_api_key,
    #         "outputFormat": "JSON",
    #     }
    #     try:
    #         response = requests.get(url, params=params, timeout=10)
    #         if response.status_code == 200:
    #             data = response.json()
    #             return {
    #                 "domain_age": data.get("WhoisRecord", {})
    #                 .get("registryData", {})
    #                 .get("createdDate"),
    #                 "registrar": data.get("WhoisRecord", {}).get("registrarName"),
    #             }
    #     except requests.RequestException as e:
    #         print(f"WhoisXML API error: {e}")
    #     return {}

    # def fetch_fullcontact_data(self, phone: str) -> Dict[str, Any]:
    #     """Fetch contact data from FullContact API."""
    #     url = f"https://api.fullcontact.com/v3/person.enrich"
    #     headers = {
    #         "Authorization": f"Bearer {self.setting_service.fullcontact_api_key}"
    #     }
    #     json_data = {"phone": phone}
    #     try:
    #         response = requests.post(url, headers=headers, json=json_data, timeout=10)
    #         if response.status_code == 200:
    #             data = response.json()
    #             return {
    #                 "linkedin": data.get("linkedin"),
    #                 "twitter": data.get("twitter"),
    #                 "bio": data.get("bio"),
    #                 "location": data.get("location"),
    #             }
    #     except requests.RequestException as e:
    #         print(f"FullContact API error: {e}")
    #     return {}

    # def fetch_google_business_data(self, place_id: str) -> Dict[str, Any]:
    #     """Fetch Google My Business details."""
    #     url = f"https://maps.googleapis.com/maps/api/place/details/json"
    #     params = {"place_id": place_id, "key": self.setting_service.gmaps_api_key}
    #     try:
    #         response = requests.get(url, params=params, timeout=10)
    #         if response.status_code == 200:
    #             data = response.json()
    #             result = data.get("result", {})
    #             return {
    #                 "formatted_address": result.get("formatted_address"),
    #                 "opening_hours": result.get("opening_hours", {}).get(
    #                     "weekday_text"
    #                 ),
    #                 "google_rating": result.get("rating"),
    #                 "reviews_count": result.get("user_ratings_total"),
    #             }
    #     except requests.RequestException as e:
    #         print(f"Google Maps API error: {e}")
    #     return {}

    # def analyze_intent(self, lead: Dict[str, Any]) -> str:
    #     """Analyze the lead's intent."""
    #     # Placeholder logic for intent analysis
    #     return "transactional"

    # def analyze_competitor_proximity(self, lead: Dict[str, Any]) -> Dict[str, int]:
    #     """Analyze the proximity of competitors."""
    #     return {"direct": 1, "indirect": 2, "peripheral": 3}

    # def analyze_industry_vertical_alignment(self, lead: Dict[str, Any]) -> str:
    #     """Analyze industry vertical alignment."""
    #     return lead.get("main_category", "unknown")

    # def analyze_ads_spending_patterns(self, lead: Dict[str, Any]) -> str:
    #     """Analyze ad spending patterns."""
    #     return "organic"

    # def analyze_business_size(self, lead: Dict[str, Any]) -> str:
    #     """Analyze business size."""
    #     return "medium"

    # def analyze_engagement_level(self, lead: Dict[str, Any]) -> str:
    #     """Analyze engagement level."""
    #     return "high"

    # def analyze_marketing_goals(self, lead: Dict[str, Any]) -> str:
    #     """Analyze marketing goals."""
    #     return "brand_awareness"

    # def analyze_marketing_strategies(self, lead: Dict[str, Any]) -> str:
    #     """Analyze marketing strategies."""
    #     return "inbound"
