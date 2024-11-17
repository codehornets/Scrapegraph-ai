import json
import yaml
from typing import Any, Dict, List

from src.db.seeders.business_profile_seeder import get_product_hunt_business_profile


def load_business_profile(self) -> Dict[str, Any]:
    profile_cache_path = "cache/business_profile.pkl"
    cache_key = self.cache_service.generate_cache_key(profile_cache_path)
    business_profile = self.cache_service.load_from_cache(
        key=cache_key,
        cache_dir=self.setting_service.keyword_storage_dir,
    )
    if not business_profile:
        business_profile = get_product_hunt_business_profile()
        business_profile = (
            business_profile[0]
            if isinstance(business_profile, list)
            else business_profile
        )
        self.cache_service.save_to_cache(
            key=cache_key,
            cache_dir=self.setting_service.keyword_storage_dir,
            data=business_profile,
        )
    return business_profile


def load_marketing_strategies(
    marketing_strategies_file_path: str,
) -> List[Dict[str, Any]]:
    with open(marketing_strategies_file_path, "r") as file:
        strategies = yaml.safe_load(file)
    return strategies["marketing_strategies"]


def load_marketing_goals(marketing_goals_file_path: str) -> List[Dict[str, Any]]:
    with open(marketing_goals_file_path, "r") as file:
        goals = json.load(file)
    return goals
