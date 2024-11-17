import os
import requests
from typing import Dict, List, Any, Optional

import dotenv
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from scrapegraphai.graphs.smart_scraper_multi_graph import SmartScraperMultiGraph
from src.config.settings import SettingService
from src.prompts.extract_business_profile_prompt import DEFAULT_SCRAPING_PROMPT
from src.utils.parsers import business_profile_parser
from src.db.seeders.business_profile_seeder import get_product_hunt_business_profile
from src.config.constants import FOOTER_CLASSES, NAVBAR_CLASSES
from src.utils.user_agents import UserAgentRotator, get_random_proxy, get_user_agents

dotenv.load_dotenv()

app_env = os.getenv("APP_ENV", "development")


class BusinessProfileService:
    def __init__(
        self,
        setting_service: SettingService,
        source: List[str],
        email: str,
        prompt: str = DEFAULT_SCRAPING_PROMPT,
    ):
        self.setting_service = setting_service
        self.website_url = source[0]
        self.linkedin_url = source[1] if len(source) > 1 else None
        self.prompt = prompt
        self.email = email

        self.user_agent_rotator = UserAgentRotator(get_user_agents())

    def generate_profile(self) -> Optional[Dict[str, Any]]:
        """Extracts business profile data based on the app environment."""
        try:
            if app_env == "production":
                scraper = SmartScraperMultiGraph(
                    source=self.extract_navbar_footer_links(),
                    prompt=self.prompt,
                    config=self.setting_service.scrapegraphai_config,
                )
                data = scraper.run()
            else:
                data = get_product_hunt_business_profile()
            if data and isinstance(data, list):
                data = data[0]
            if data:
                data.update({"request_email": self.email})
                return self.enrich_business_profile_data(data)
            return None
        except Exception as e:
            print(f"Error extracting business profile: {e}")
            return None

    def extract_navbar_footer_links(self) -> List[str]:
        """Extracts all unique links from the navbar and footer of the provided source URL."""
        if not self.source:
            raise ValueError("Source URL list cannot be empty.")

        base_url = self.website_url
        user_agent = self.user_agent_rotator.get()
        headers = {"User-Agent": str(user_agent)}
        proxy = {"http": get_random_proxy(), "https": get_random_proxy()}

        try:
            response = requests.get(base_url, headers=headers, proxies=proxy)
            response.raise_for_status()
        except RequestException as e:
            print(f"Error fetching URL {base_url}: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        navbar_links = self.extract_links_by_classes(soup, base_url, NAVBAR_CLASSES)
        footer_links = self.extract_links_by_classes(soup, base_url, FOOTER_CLASSES)

        all_links = list(set(navbar_links + footer_links))
        if self.linkedin_url:
            all_links.append(self.linkedin_url)

        return all_links

    def enrich_business_profile_data(
        self,
        business_profile: Dict[str, Any],
        additional_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Enriches the business profile data using an additional profile."""
        if additional_profile is None:
            additional_profile = {}
        return business_profile_parser(business_profile, additional_profile)

    def extract_links_by_classes(
        self, soup: BeautifulSoup, base_url: str, classes: List[str]
    ) -> List[str]:
        """Extracts links from HTML elements matching the specified classes."""
        links = []
        for class_name in classes:
            elements = soup.select(f"{class_name} a[href]")
            for a in elements:
                href = a["href"]
                if href.startswith("/"):
                    href = base_url + href
                if href.count("/") <= 1 and "#" not in href:
                    links.append(href)
        return list(set(links))
