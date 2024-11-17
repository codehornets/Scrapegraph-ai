import os
from typing import Any, Dict

import dotenv

from src.config.settings import SettingService
from src.services.caches import CacheService

dotenv.load_dotenv()


class ContentService:
    def __init__(
        self,
        settings: SettingService,
        cache_service: CacheService,
        business_profile: Dict[str, Any] = None,
        marketing_goals: Dict[str, Any] = None,
    ):
        self.setting_service = settings
        self.cache_service = cache_service
