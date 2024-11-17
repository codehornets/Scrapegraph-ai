import json
from typing import Any, Dict, List

from pydantic import ValidationError

from src.models.lead import LeadSegmentation


class LeadClassifier:
    def __init__(self, llm_service, setting_service, cache_service):
        self.llm_service = llm_service
        self.setting_service = setting_service
        self.cache_service = cache_service

    def categorize(self, lead: dict) -> Dict[str, List[Dict[str, Any]]]:
        try:
            prompt = f"""
                Categorize the following business lead into appropriate segments:
                Lead details: {json.dumps(lead, indent=2)}
                Possible categories: ["Small Business", "Mid-Sized Business", "Enterprise", "Local", "High Revenue", "Consulting", "SEO Needs", "Walk-In Customers"]

                Provide a JSON object where keys are categories and values are lists of lead details.
            """
            response = self.llm_service.chat.completions.create(
                model="gpt-4o",
                response_model=LeadSegmentation,
                messages=[
                    {"role": "system", "content": "You are a marketing expert."},
                    {"role": "user", "content": prompt},
                ],
            )

            llm_output = response.choices[0].message.content.strip()
            categorized_data = json.loads(llm_output)

            validated_data = LeadSegmentation(segments=categorized_data)
            return validated_data.segments
        except ValidationError as e:
            print(f"Validation failed for LLM categorization: {e}")
        except Exception as e:
            print(f"LLM categorization failed: {e}")
        return {}
