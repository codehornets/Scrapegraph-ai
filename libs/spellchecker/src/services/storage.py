import logging
import os
import tempfile
from typing import Set

import boto3
import fitz
import requests

from libs.spellchecker.src.config.settings import Settings


class StorageService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bucket_name = settings.app_bucket

        self.client = boto3.client(
            "s3",
            endpoint_url=(
                settings.aws_endpoint if settings.app_env == "LOCAL" else None
            ),
            aws_access_key_id=(
                settings.aws_access_key if settings.app_env == "LOCAL" else None
            ),
            aws_secret_access_key=(
                settings.aws_secret_key if settings.app_env == "LOCAL" else None
            ),
        )

    def get_pdf_file(self, pdf_temporary_url):
        return fitz.open(self.download_document(pdf_temporary_url)) or exit(
            "PDF file is not valid."
        )

    @staticmethod
    def download_document(
        document_temporary_url: str, suffix: str = ".pdf"
    ) -> str | None:
        try:
            if not document_temporary_url:
                return None

            response = requests.get(document_temporary_url)
            response.raise_for_status()
            temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            temp.write(response.content)
            temp.close()
            return temp.name
        except requests.exceptions.RequestException as error:
            logging.error(f"Error downloading document: {error}")
            return None

    def get_dictionary_words(self, dic_temporary_url) -> Set[str]:
        dic_path = self.download_document(dic_temporary_url, suffix=".txt")
        if dic_path:
            downloaded_words = {
                word.strip()
                for word in open(dic_path, "r", encoding="utf-8")
                if word.strip()
            }
            loaded_words = self.load_words_from_directory(
                self.settings.global_dictionary_path
            )

            os.remove(dic_path)

            return set(downloaded_words.union(loaded_words))
        else:
            logging.error("Failed to download dictionary file.")
            return set()

    @staticmethod
    def load_words_from_directory(directory: str) -> Set[str]:
        return {
            word.strip()
            for root, _, files in os.walk(directory)
            for file in files
            if file.endswith(".txt")
            for word in open(os.path.join(root, file), "r", encoding="utf-8")
            if word.strip()
        }
