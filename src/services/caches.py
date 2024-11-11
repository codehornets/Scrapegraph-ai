import hashlib
import json
import os
import pickle
import yaml
import csv
from typing import List, Dict, Any, Union

from src.config.settings import SettingService


class CacheService:
    def __init__(self, settings: SettingService):
        self.settings = settings

    @staticmethod
    def generate_cache_key(data: Dict[str, Any]) -> str:
        sorted_data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(sorted_data_str.encode()).hexdigest()

    def save_to_cache(
        self,
        key: str,
        cache_dir: str,
        data: Any,
        website: str = "https://www.example.com",
        device: str = "desktop",
        cache_format: str = "pickle",
    ):
        key = key.replace(" ", "_")

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        cache_file = self.get_cache_filename(
            key=key,
            cache_dir=cache_dir,
            website=website,
            device=device,
            cache_format=cache_format,
        )

        if cache_format == "pickle":
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
        elif cache_format == "json":
            with open(cache_file, "w") as f:
                json.dump(data, f, default=str)
        elif cache_format == "csv":
            self.save_as_csv(cache_file, data)
        elif cache_format == "txt":
            with open(cache_file, "w") as f:
                f.write(str(data))
        else:
            raise ValueError(f"Unsupported cache format: {cache_format}")

    def load_from_cache(
        self,
        key: str,
        cache_dir: str,
        website: str = "https://www.example.com",
        device: str = "desktop",
        cache_format: str = "pickle",
    ) -> Union[Dict, List, str, None]:
        key = key.replace(" ", "_")

        cache_file = self.get_cache_filename(
            key=key,
            cache_dir=cache_dir,
            website=website,
            device=device,
            cache_format=cache_format,
        )

        if os.path.exists(cache_file):
            if cache_format == "json":
                with open(cache_file, "r") as f:
                    return json.load(f)
            elif cache_format == "pickle":
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            elif cache_format == "csv":
                return self.load_from_csv(cache_file)
            elif cache_format == "txt":
                with open(cache_file, "r") as f:
                    return f.read()
        return None

    def get_cache_filename(
        self, key: str, cache_dir: str, website: str, device: str, cache_format: str
    ) -> str:
        query_hash = hashlib.md5(f"{key}_{website}_{device}".encode()).hexdigest()
        return os.path.join(cache_dir, f"{query_hash}.{cache_format}")

    def save_as_csv(self, file_path: str, data: List[Dict[str, Any]]):
        if not data or not isinstance(data, list):
            raise ValueError("Data for CSV must be a non-empty list of dictionaries.")

        keys = data[0].keys()
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    def load_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def cache_data(
        self,
        file_path: str,
        data: Any = None,
        load_only: bool = False,
        cache_format: str = "pickle",
    ) -> Any:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if load_only and os.path.exists(file_path):
            return self.load_generic(file_path, cache_format)
        elif data is not None:
            self.save_generic(file_path, data, cache_format)
        return data

    def save_generic(self, file_path: str, data: Any, cache_format: str):
        if cache_format == "json":
            with open(file_path, "w") as f:
                json.dump(data, f, default=str)
        elif cache_format == "pickle":
            with open(file_path, "wb") as f:
                pickle.dump(data, f)
        elif cache_format == "csv":
            self.save_as_csv(file_path, data)
        elif cache_format == "txt":
            with open(file_path, "w") as f:
                f.write(str(data))
        else:
            raise ValueError(f"Unsupported cache format: {cache_format}")

    def load_generic(self, file_path: str, cache_format: str) -> Any:
        if cache_format == "json":
            with open(file_path, "r") as f:
                return json.load(f)
        elif cache_format == "pickle":
            with open(file_path, "rb") as f:
                return pickle.load(f)
        elif cache_format == "csv":
            return self.load_from_csv(file_path)
        elif cache_format == "txt":
            with open(file_path, "r") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported cache format: {cache_format}")

    def load_marketing_strategies(self) -> List[Dict[str, Any]]:
        with open(self.settings.marketing_strategies_file_path, "r") as file:
            strategies = yaml.safe_load(file)
        return strategies["marketing_strategies"]
