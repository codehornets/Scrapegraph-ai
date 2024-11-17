import hashlib
import json
import traceback
from typing import Any, Dict, List, Optional

from termcolor import colored

from src.config.settings import SettingService
from src.models.lead import SegmentationRule
from src.services.caches import CacheService
from src.services.leads.validations import LeadValidationService
from .classifier import LeadClassifier
from .evaluator import RuleEvaluator
from .segmenter import SegmentLead

from src.utils.debug import die

class SegmentService:
    def __init__(
        self,
        setting_service: SettingService,
        cache_service: CacheService,
        marketing_goals: List[str],
        marketing_strategies: List[str],
    ):
        self.setting_service = setting_service
        self.cache_service = cache_service
        self.marketing_goals = marketing_goals
        self.marketing_strategies = marketing_strategies

        self.validation_service = LeadValidationService(
            setting_service=self.setting_service,
            cache_service=self.cache_service,
        )
        self.segmenter = SegmentLead(
            rule_engine=RuleEvaluator(
                rules=self.load_rules_from_config("segments.json"),
                feature_flags=self.setting_service.feature_flags_segmentation,
            ),
            llm_categorizer=LeadClassifier(
                llm_service=self.setting_service.openai,
                setting_service=self.setting_service,
                cache_service=self.cache_service,
            ),
            segmentation_mode="static",
        )

    def load_rules_from_config(
        self, config_path: Optional[str] = None, json_data: Optional[dict] = None
    ) -> List[SegmentationRule]:
        if json_data:
            rules_data = json_data
        elif config_path:
            with open(config_path, "r") as f:
                rules_data = json.load(f)
        else:
            raise ValueError("Either 'config_path' or 'json_data' must be provided.")
        return [
            SegmentationRule(**rule)
            for category in rules_data.values()
            for rule in category
        ]

    def segment_leads_in_batches(self, leads: list) -> dict:
        return self.process_leads_in_batches(leads)

    def process_leads_in_batches(self, leads: List[dict], batch_size: int = 100):
        segmented_leads = []
        for i in range(0, len(leads), batch_size):
            batch = leads[i : i + batch_size]
            segmented_leads.extend(self.process_leads(batch))
        return segmented_leads

    def process_leads(self, leads: List[dict]):
        segmented_leads = []
        for lead in leads:
            try:
                validated_lead = self.validation_service.validate_lead(lead)
                segments = self.segmenter.segment_lead(validated_lead)
                lead_hash = self.generate_lead_hash(validated_lead)
                segmented_leads.append(
                    {
                        "lead_id": validated_lead.get("place_id"),
                        "name": validated_lead.get("name"),
                        "segments": segments,
                        "hash": lead_hash,
                    }
                )

                lead["segments"] = segments
                lead["hash"] = lead_hash

                print(
                    colored(f"\nSegmented lead: {json.dumps(lead, indent=2)}", "green")
                )

                die("\ngot here...")
            except Exception as e:
                print(f"Failed to process lead: {e}")
                traceback.print_exc()
        return segmented_leads

    @staticmethod
    def generate_lead_hash(lead: Dict[str, Any]) -> str:
        unique_string = f"{lead.get('place_id')}_{lead.get('phone')}_{lead.get('name')}"
        return hashlib.sha256(unique_string.encode()).hexdigest()