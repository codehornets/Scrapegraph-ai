from functools import lru_cache

import numpy as np
from keybert import KeyBERT
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation

from src.config.settings import SettingService
from src.services.caches import CacheService
from src.utils.debug import die


class IntentClassification(BaseModel):
    intent: str
    score: float


class IntentClassifier:
    def __init__(
        self, settings: SettingService, cache_service: CacheService
    ):
        self.setting_service = settings
        self.cache_service = cache_service
        
        self.ust_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.keybert_model = KeyBERT("all-MiniLM-L6-v2")
        self.vectorizer = CountVectorizer(stop_words="english")
        self.intent_texts = [
            entry["description"] for entry in self.setting_service.keyword_intents
        ]
        self.intent_categories = [
            entry["intent"] for entry in self.setting_service.keyword_intents
        ]

    def analyze_intent(self, query: str):
        search_intent = self.gpt_analyze_intent(query)
        keywords = self.keybert_model.extract_keywords(
            query, keyphrase_ngram_range=(1, 2), top_n=5
        )
        return search_intent, keywords

    def gpt_analyze_intent(self, query):
        try:
            cache_key = self.cache_service.generate_cache_key(query)
            gpt_analyze_intent = self.cache_service.load_from_cache(
                key=cache_key,
                cache_dir=self.setting_service.intent_analysis_cache_path,
            )

            if gpt_analyze_intent:
                return gpt_analyze_intent

            prompt = (
                "As a marketing expert, classify the primary intent of the following text into one of the categories: "
                "Informational, Commercial, Navigational, or Transactional. "
                "Definitions:\n"
                "- **Informational**: Content aimed at providing guidance, tutorials, information, and insights.\n"
                "- **Commercial**: Content focused on pricing, buying, deals, and subscription options.\n"
                "- **Navigational**: Content that directs users to specific resources, locations, or websites.\n"
                "- **Transactional**: Content focused on actions like ordering, subscribing, signing up, or downloading.\n\n"
                "Text for classification:\n"
                f"{query}"
            )

            intent, _ = self.setting_service.openai.chat.completions.create(
                model="gpt-4o",
                response_model=IntentClassification,
                messages=[
                    {"role": "system", "content": "You are a marketing expert."},
                    {"role": "user", "content": prompt},
                ],
            )

            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.intent_analysis_cache_path,
                data=intent[1],
            )

            return intent[1]
        except Exception as e:
            print(f"LLM Analysis failed: {e}")
            return "Uncertain", 0.0

    def llm_analyze_intent(self, query):
        try:
            # Calculate scores with UST embeddings
            ust_embeddings = self.ust_model.encode(
                self.intent_texts, convert_to_tensor=True
            )
            query_embedding = self.ust_model.encode([query], convert_to_tensor=True)
            ust_scores = cosine_similarity(query_embedding, ust_embeddings).flatten()
            print(f"\nUST Scores: \n {ust_scores}")

            # Calculate KeyBERT scores
            keybert_keywords = self.keybert_model.extract_keywords(
                query, keyphrase_ngram_range=(1, 2), top_n=5
            )
            print(f"\nKeyBERT Keywords: \n {keybert_keywords}")

            flattened_keybert_keywords = [keyword for keyword, _ in keybert_keywords]
            keybert_scores = [
                self.calculate_similarity(
                    flattened_keybert_keywords,
                    [
                        kw
                        for kw, _ in self.keybert_model.extract_keywords(
                            intent, top_n=5
                        )
                    ],
                )
                for intent in self.intent_texts
            ]
            print(f"\nKeyBERT Scores: \n {keybert_scores}")

            # Calculate LDA scores
            lda_topics = self.extract_lda_topics(query)
            print(f"\nLDA Topics: \n {lda_topics}")

            lda_scores = [
                self.calculate_similarity(lda_topics, self.extract_lda_topics(intent))
                for intent in self.intent_texts
            ]
            print(f"\nLDA Scores: \n {lda_scores}")

            # Weighted combined scores
            combined_scores = (
                self.setting_service.intent_classifier_weights[0] * ust_scores
                + self.setting_service.intent_classifier_weights[1]
                * np.array(keybert_scores)
                + self.setting_service.intent_classifier_weights[2]
                * np.array(lda_scores)
            )
            print(f"\nCombined Scores: \n {combined_scores}")

            # Rank intents and apply threshold
            ranked_intents = sorted(
                [
                    (self.setting_service.keyword_intents[i]["intent"], score)
                    for i, score in enumerate(combined_scores)
                    if score >= self.threshold
                ],
                key=lambda x: x[1],
                reverse=True,
            )
            print(f"\nRanked Intents: \n {ranked_intents}")

            best_intent = ranked_intents[0] if ranked_intents else ("Uncertain", 0)
            print(f"\nBest Intent: \n {best_intent}")

            return best_intent, ranked_intents, keybert_keywords
        except Exception as e:
            print(f"LLM Analysis failed: {e}")
            return "Uncertain", 0.0

    def calculate_similarity(self, list1, list2):
        set1, set2 = set(list1), set(list2)
        overlap = set1.intersection(set2)
        return (
            len(overlap) / max(len(set1), len(set2))
            if max(len(set1), len(set2)) > 0
            else 0.0
        )

    @lru_cache(maxsize=128)
    def extract_lda_topics(self, text):
        vectorized = self.vectorizer.fit_transform([text])
        lda_model = LatentDirichletAllocation(n_components=3, random_state=42)
        lda_model.fit(vectorized)

        return [
            self.vectorizer.get_feature_names_out()[i]
            for i in lda_model.components_[0].argsort()[-5:]
        ]
