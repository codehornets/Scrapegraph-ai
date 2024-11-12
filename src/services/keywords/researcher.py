import argparse
import dotenv
import json, csv
from typing import Any, Dict
from itertools import zip_longest

from src.services.serpapi.google_search import GoogleSearch
from src.config.settings import SettingService

dotenv.load_dotenv()


class SeoKeywordResearch:
    def __init__(
        self,
        settings: SettingService,
        api_key: str,
        query: str = None,
        lang: str = "en",
        country: str = "us",
        domain: str = "google.com",
    ) -> None:
        if not api_key:
            raise ValueError("API key is required")

        self.settings_service = settings
        self.query = query
        self.api_key = api_key
        self.lang = lang
        self.country = country
        self.domain = domain
        self.__related_questions_results = []

    def process_query(
        self,
        query: str,
        lang: str = "en",
        country: str = "us",
        domain: str = "google.com",
    ) -> Dict[str, Any]:
        self.query = query
        self.lang = lang
        self.country = country
        self.domain = domain

        auto_complete_results = self.get_auto_complete()
        related_searches_results = self.get_related_searches()
        related_questions_results = self.get_related_questions()

        data = {
            "auto_complete": auto_complete_results,
            "related_searches": related_searches_results,
            "related_questions": related_questions_results,
        }

        self.save_to_json(data)

        return data

    def get_auto_complete(self) -> list:
        params = {
            "api_key": self.api_key,  # https://serpapi.com/manage-api-key
            "engine": "google_autocomplete",  # search engine
            "q": self.query,  # search query
            "gl": self.country,  # country of the search
            "hl": self.lang,  # language of the search
        }

        search = GoogleSearch(params)  # data extraction on the SerpApi backend
        results = search.get_dict()  # JSON -> Python dict

        auto_complete_results = [
            result.get("value") for result in results.get("suggestions", [])
        ]

        return auto_complete_results

    def get_related_searches(self) -> list:
        params = {
            "api_key": self.api_key,  # https://serpapi.com/manage-api-key
            "engine": "google",  # search engine
            "q": self.query,  # search query
            "google_domain": self.domain,  # Google domain to use
            "gl": self.country,  # country of the search
            "hl": self.lang,  # language of the search
        }

        search = GoogleSearch(params)  # data extraction on the SerpApi backend
        results = search.get_dict()  # JSON -> Python dict

        related_searches_results = [
            result.get("query") for result in results.get("related_searches", [])
        ]

        return related_searches_results

    def __get_depth_results(self, token: str, depth: int) -> None:
        """
        This function allows you to extract more data from People Also Ask.

        The function takes the following arguments:

        :param token: allows access to additional related questions.
        :param depth: limits the input depth for each related question.
        """

        depth_params = {
            "api_key": self.api_key,
            "engine": "google_related_questions",
            "next_page_token": token,
        }

        depth_search = GoogleSearch(depth_params)
        depth_results = depth_search.get_dict()

        self.__related_questions_results.extend(
            [
                result.get("question")
                for result in depth_results.get("related_questions", [])
            ]
        )

        if depth > 1:
            for question in depth_results.get("related_questions", []):
                if question.get("next_page_token"):
                    self.__get_depth_results(question.get("next_page_token"), depth - 1)

    def get_related_questions(self, depth_limit: int = 0) -> list:
        params = {
            "api_key": self.api_key,  # https://serpapi.com/manage-api-key
            "engine": "google",  # search engine
            "q": self.query,  # search query
            "google_domain": self.domain,  # Google domain to use
            "gl": self.country,  # country of the search
            "hl": self.lang,  # language of the search
        }

        search = GoogleSearch(params)  # data extraction on the SerpApi backend
        results = search.get_dict()  # JSON -> Python dict

        self.__related_questions_results = [
            result.get("question") for result in results.get("related_questions", [])
        ]

        if depth_limit > 4:
            depth_limit = 4

        if depth_limit:
            for question in results.get("related_questions", []):
                if question.get("next_page_token"):
                    self.__get_depth_results(
                        question.get("next_page_token"), depth_limit
                    )

        return self.__related_questions_results

    def save_to_csv(self, data: dict) -> None:
        with open(
            f'{self.settings_service.keyword_storage_dir}/{self.query.replace(" ", "_")}.csv',
            "w",
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data.keys())
            writer.writerows(zip_longest(*data.values()))

    def save_to_json(self, data: dict) -> None:
        with open(
            f'{self.settings_service.keyword_storage_dir}/{self.query.replace(" ", "_")}.json',
            "w",
            encoding="utf-8",
        ) as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)

    def save_to_txt(self, data: dict) -> None:
        with open(
            f'{self.settings_service.keyword_storage_dir}/{self.query.replace(" ", "_")}.txt',
            "w",
        ) as txt_file:
            for key in data.keys():
                txt_file.write("\n".join(data.get(key)) + "\n")


def main():
    parser = argparse.ArgumentParser(
        prog="SerpApi SEO Keyword Research Tool",
        description="Extract keywrods from: Google Autocomplete, People Also Ask, and People Also Search and saves data to CSV/JSON/TXT.",
        epilog="Found a bug? Open issue: https://github.com/chukhraiartur/seo-keyword-research-tool/issues",
    )
    parser.add_argument(
        "-q", "--query", metavar="", required=True, help="Search query (required)."
    )
    parser.add_argument(
        "-e",
        "--engines",
        metavar="",
        required=False,
        type=str,
        default=["ac", "rs", "rq"],
        nargs="+",
        help="Choices of engines to extract: Autocomplete (ac), Related Searches (rs), People Also Ask (rq). You can select multiple engines. All engines are selected by default.",
    )
    parser.add_argument(
        "-dl",
        "--depth-limit",
        metavar="",
        required=False,
        type=int,
        default=0,
        help="Depth limit for People Also Ask. Default is %(default)i, first 2-4 results.",
    )
    parser.add_argument(
        "-st",
        "--save-to",
        metavar="",
        required=False,
        default="CSV",
        help="Saves the results in the current directory in the selected format (CSV, JSON, TXT). Default %(default)s.",
    )
    parser.add_argument(
        "-ak",
        "--api-key",
        metavar="",
        required=False,
        default="5868ece26d41221f5e19ae8b3e355d22db23df1712da675d144760fc30d57988",
        help="Your SerpApi API key: https://serpapi.com/manage-api-key. Default is a test API key to test CLI.",
    )
    parser.add_argument(
        "-gd",
        "--domain",
        metavar="",
        required=False,
        default="google.com",
        help="Google domain: https://serpapi.com/google-domains. Default %(default)s.",
    )
    parser.add_argument(
        "-gl",
        "--country",
        metavar="",
        required=False,
        default="us",
        help="Country of the search: https://serpapi.com/google-countries. Default %(default)s.",
    )
    parser.add_argument(
        "-hl",
        "--lang",
        metavar="",
        required=False,
        default="en",
        help="Language of the search: https://serpapi.com/google-languages. Default %(default)s.",
    )
    args = parser.parse_args()

    keyword_research = SeoKeywordResearch(
        query=args.query,
        api_key=args.api_key,
        lang=args.lang,
        country=args.country,
        domain=args.domain,
    )

    data = {}

    for engine in args.engines:
        if engine.lower() == "ac":
            data["auto_complete"] = keyword_research.get_auto_complete()
        elif engine.lower() == "rs":
            data["related_searches"] = keyword_research.get_related_searches()
        elif engine.lower() == "rq":
            data["related_questions"] = keyword_research.get_related_questions(
                args.depth_limit
            )

    if data:
        keyword_research.print_data(data)
        print(f"Saving data in {args.save_to.upper()} format...")

        if args.save_to.upper() == "CSV":
            keyword_research.save_to_csv(data)
        elif args.save_to.upper() == "JSON":
            keyword_research.save_to_json(data)
        elif args.save_to.upper() == "TXT":
            keyword_research.save_to_txt(data)

        print(
            f'Data successfully saved to {args.query.replace(" ", "_")}.{args.save_to.lower()} file'
        )


if __name__ == "__main__":
    main()


# keyword_research = SeoKeywordResearch(
#     query="starbucks coffee",
#     api_key=os.getenv("SERP_API_KEY"),
#     lang="en",
#     country="us",
#     domain="google.com",
# )

# auto_complete_results = keyword_research.get_auto_complete()
# related_searches_results = keyword_research.get_related_searches()
# related_questions_results = keyword_research.get_related_questions()

# data = {
#     "auto_complete": auto_complete_results,
#     "related_searches": related_searches_results,
#     "related_questions": related_questions_results,
# }

# keyword_research.save_to_json(data)
# keyword_research.print_data(data)
