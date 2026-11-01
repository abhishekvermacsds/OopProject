"""Thin wrapper around the NLP Cloud API (https://nlpcloud.com).

Exposes three features with clean, predictable return types:
    * entities()        -> Named Entity Recognition
    * detect_language() -> Language detection
    * sentiment()       -> Emotion / sentiment classification
"""
from __future__ import annotations

from typing import Callable

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
    "mr": "Marathi", "gu": "Gujarati", "pa": "Punjabi", "ur": "Urdu", "ne": "Nepali",
    "fr": "French", "de": "German", "es": "Spanish", "it": "Italian", "pt": "Portuguese",
    "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)", "ar": "Arabic", "nl": "Dutch", "tr": "Turkish",
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code.lower(), code)


class NLPServiceError(Exception):
    """Any problem talking to the NLP Cloud API. The message is safe to show to the user."""


def _default_client_factory(api_key: str, gpu: bool) -> Callable:
    def factory(model: str, lang: str = ""):
        import nlpcloud  # imported lazily so tests / --help work without the package

        return nlpcloud.Client(model, api_key, gpu=gpu, lang=lang)

    return factory


def _friendly_message(exc: Exception) -> str:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 401:
        return "Invalid API key. Check NLPCLOUD_API_KEY in your .env file."
    if status in (402, 403):
        return "Access denied or quota exceeded for this model on your NLP Cloud plan."
    if status == 404:
        return "Model not found. Check the model name in your configuration."
    if status == 429:
        return "Rate limit reached. Please wait a moment and try again."
    if status and status >= 500:
        return "NLP Cloud is having trouble right now. Please try again later."
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return "Network error. Check your internet connection and try again."
    return f"NLP Cloud request failed: {exc}"


class NLPService:
    def __init__(
        self,
        api_key: str = "",
        ner_model: str = "en_core_web_lg",
        langdetect_model: str = "python-langdetect",
        sentiment_model: str = "distilbert-base-uncased-emotion",
        gpu: bool = False,
        client_factory: Callable | None = None,
    ):
        self.ner_model = ner_model
        self.langdetect_model = langdetect_model
        self.sentiment_model = sentiment_model
        self._factory = client_factory or _default_client_factory(api_key, gpu)

    def _call(self, model: str, method: str, text: str, lang: str = "") -> dict:
        text = (text or "").strip()
        if not text:
            raise NLPServiceError("Text cannot be empty.")
        try:
            client = self._factory(model, lang)
            return getattr(client, method)(text)
        except NLPServiceError:
            raise
        except ImportError as exc:
            raise NLPServiceError(
                "The 'nlpcloud' package is not installed. Run: pip install -r requirements.txt"
            ) from exc
        except Exception as exc:  # requests.HTTPError, timeouts, etc.
            raise NLPServiceError(_friendly_message(exc)) from exc

    # ---- features ----------------------------------------------------
    def entities(self, text: str) -> list[dict]:
        """Named Entity Recognition -> [{'text', 'type', 'start', 'end'}, ...]"""
        response = self._call(self.ner_model, "entities", text)
        return [
            {
                "text": item.get("text", ""),
                "type": item.get("type", ""),
                "start": item.get("start"),
                "end": item.get("end"),
            }
            for item in response.get("entities", [])
        ]

    def detect_language(self, text: str) -> list[tuple[str, float]]:
        """Language detection -> [('en', 0.99), ('fr', 0.01), ...] sorted by confidence."""
        response = self._call(self.langdetect_model, "langdetect", text)
        pairs = [
            (code, float(score))
            for item in response.get("languages", [])
            for code, score in item.items()
        ]
        return sorted(pairs, key=lambda p: p[1], reverse=True)

    def sentiment(self, text: str) -> list[tuple[str, float]]:
        """Emotion classification -> [('joy', 0.93), ('love', 0.04), ...] sorted by score."""
        response = self._call(self.sentiment_model, "sentiment", text, lang="en")
        pairs = [(item["label"], float(item["score"])) for item in response.get("scored_labels", [])]
        return sorted(pairs, key=lambda p: p[1], reverse=True)
