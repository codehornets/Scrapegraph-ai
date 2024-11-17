from typing import Any, Dict, List

from .classifier import LeadClassifier
from .evaluator import RuleEvaluator


class SegmentLead:
    def __init__(
        self,
        rule_engine: RuleEvaluator,
        llm_categorizer: LeadClassifier,
        segmentation_mode: str = "static",  # "static", "llm", or "hybrid"
    ):
        self.rule_engine = rule_engine
        self.llm_categorizer = llm_categorizer
        self.segmentation_mode = segmentation_mode

    def segment_lead(self, lead: dict) -> Dict[str, List[Dict[str, Any]]]:
        if self.segmentation_mode == "static":
            segments = self.rule_engine.evaluate(lead)
            self.handle_sub_segments(lead, segments)
            return segments

        # TODO: Future support for LLM or hybrid modes
        # elif self.segmentation_mode == "llm":
        #     return self.llm_categorizer.categorize(lead)
        # elif self.segmentation_mode == "hybrid":
        #     static_segments = self.rule_engine.evaluate(lead)
        #     llm_segments = self.llm_categorizer.categorize(lead)
        #     # Combine static and LLM-based segments with priority to static
        #     for category, leads in llm_segments.items():
        #         if category not in static_segments:
        #             static_segments[category] = leads
        #     return static_segments
        # else:
        #     raise ValueError(f"Invalid segmentation mode: {self.segmentation_mode}")

    def handle_sub_segments(self, lead: dict, segments: Dict[int, List[str]]):
        informational_segments = segments.get(1, [])
        if "informational" in informational_segments:
            query = lead.get("query", "").lower()
            if any(
                keyword in query for keyword in ["how", "what", "guide", "overview"]
            ):
                informational_segments.append("researching")
            elif any(
                keyword in query for keyword in ["compare", "best", "alternatives"]
            ):
                informational_segments.append("evaluating")
