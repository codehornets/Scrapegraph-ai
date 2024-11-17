from src.config.settings import SettingService


class ReportService:
    def __init__(self, settings: SettingService):
        self.settings = settings
