import re
from typing import Any, Dict, List
from termcolor import colored
from src.models.lead import SegmentationRule


class RuleEvaluator:
    def __init__(self, rules: List[SegmentationRule], feature_flags: Dict[str, bool]):
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.feature_flags = feature_flags

    def evaluate(self, lead: dict) -> Dict[int, List[str]]:
        matched_segments = {}

        for rule in self.rules:
            if not self.feature_flags.get(rule.segment_name, True):
                print(
                    colored(
                        f"\nRule '{rule.name}' is disabled via feature flags.", "yellow"
                    )
                )
                continue

            if self.apply_rule(lead, rule):
                if rule.priority not in matched_segments:
                    matched_segments[rule.priority] = []
                matched_segments[rule.priority].append(rule.segment_name)
                print(
                    colored(
                        f"Rule '{rule.name}' matched for lead '{lead.get('name', 'Unknown')}'.",
                        "green",
                    )
                )
            else:
                print(
                    colored(
                        f"Rule '{rule.name}' not matched for lead '{lead.get('name', 'Unknown')}'.",
                        "red",
                    )
                )

        return matched_segments

    def apply_rule(self, lead: Dict[str, Any], rule: SegmentationRule) -> bool:
        try:
            field_values = self.get_field_value(lead, rule.field)
            rule_value = self.sanitize_value(rule.value)

            if not field_values:
                print(
                    colored(
                        f"\nSkipping rule '{rule.name}' for lead '{lead.get('name', 'Unknown')}' because the field '{rule.field}' is empty.",
                        "yellow",
                    )
                )
                return False

            print(f"\nLead: {lead.get('name', 'Unknown')}")
            print(f"Field: {rule.field}")
            print(f"Field Values: {field_values}")
            print(f"Rule Value: {rule_value}")
            print(f"Rule: {rule.name}")
            print(f"Operator: {rule.operator}")
            print(f"Priority: {rule.priority}")

            if rule.operator == "contains":
                for value in field_values:
                    sanitized_value = self.sanitize_value(value)
                    print(f"Sanitized value: {sanitized_value}")
                    if rule_value in sanitized_value:
                        print(
                            colored(
                                f"Match found for rule: {rule.name} - {value} with operator: {rule.operator}",
                                "green",
                            )
                        )
                        return True
                return False

            elif rule.operator == "==":
                for value in field_values:
                    sanitized_value = self.sanitize_value(value)
                    print(f"Sanitized value: {sanitized_value}")
                    if sanitized_value == rule_value:
                        print(
                            colored(
                                f"Match found for rule: {rule.name} - {value} with operator: {rule.operator}",
                                "green",
                            )
                        )
                        return True
                return False
            elif rule.operator == "not_empty":
                result = bool(field_values)
                print(
                    colored(
                        f"Match found for rule: {rule.name} - {result} with operator: {rule.operator}",
                        "green",
                    )
                )
                return result
            elif rule.operator in [">", "<", ">=", "<="]:
                numeric_field_values = [
                    float(value)
                    for value in field_values
                    if isinstance(value, (int, float, str))
                    and str(value).replace(".", "", 1).isdigit()
                ]
                for value in numeric_field_values:
                    if eval(f"{value} {rule.operator} {float(rule_value)}"):
                        print(
                            colored(
                                f"Match found for rule: {rule.name} - {value} with operator: {rule.operator}",
                                "green",
                            )
                        )
                        return True
                return False
            else:
                raise ValueError(f"Unsupported operator: {rule.operator}")
        except Exception as e:
            print(
                colored(
                    f"Error applying rule '{rule.name}' on lead '{lead.get('name', 'Unknown')}': {e}",
                    "red",
                )
            )
            return False

    def get_field_value(self, lead: Dict[str, Any], field: str) -> List[Any]:
        """
        Recursively fetch field values from nested structures, including lists of dictionaries.
        Returns a flattened list of all matching values.
        """
        keys = field.split(".")
        value = [lead]
        for key in keys:
            next_values = []
            for item in value:
                if isinstance(item, dict) and key in item:
                    next_values.append(item[key])
                elif isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict) and key in sub_item:
                            next_values.append(sub_item[key])
            value = next_values

        # Flatten list if it contains nested lists
        if isinstance(value, list):
            flattened = []
            for item in value:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened
        return [value]

    @staticmethod
    def sanitize_value(value: Any) -> str:
        if isinstance(value, str):
            return re.sub(r"[^\w\s]", "", value.lower().strip())
        return str(value).strip()
