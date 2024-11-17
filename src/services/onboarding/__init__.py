from typing import Any, Dict, List

from src.config.settings import SettingService


class OnboardingService:
    def __init__(self, setting_service: SettingService, source: List[str], email: str):
        self.settings = setting_service
        self.source = source
        self.email = email

    def onboard_user(self) -> Dict[str, Any]:
        pass
