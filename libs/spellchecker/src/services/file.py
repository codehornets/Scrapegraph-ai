import hashlib
import json
import os
import shutil

from libs.spellchecker.src.config.constants import CACHE_DIRECTORY
from libs.spellchecker.src.config.settings import Settings


class FileService:
    def __init__(self, settings: Settings):
        self.settings = settings

        # for dir_path in [PDF_LOCAL_DIRECTORY, CACHE_DIRECTORY, REPORT_DIRECTORY]:
        for dir_path in [CACHE_DIRECTORY]:
            os.makedirs(dir_path, exist_ok=True)

        for file_path in self.settings.cache_file_paths.values():
            open(file_path, "w").close()

    @staticmethod
    def hash_text(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def cache_operations(self, text, cache_file, result=None, operation="r"):
        hashed_text = self.hash_text(text)
        if isinstance(cache_file, str):
            cache = dict(
                (line.strip().split("||", 1)) for line in open(cache_file, "r")
            )
            if operation == "r" and hashed_text in cache:
                return json.loads(cache[hashed_text])
            elif operation == "w" and result:
                open(cache_file, "a").write(f"{hashed_text}||{json.dumps(result)}\n")
        else:
            print(f"Invalid file path for cache_file: {cache_file}")

    @staticmethod
    def delete_directory(path):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
