"""Entry point:  python main.py"""
from nlp_app import config
from nlp_app.auth import UserStore
from nlp_app.cli import NLPApp
from nlp_app.nlp_service import NLPService


def main() -> None:
    if not config.API_KEY:
        raise SystemExit(
            "Missing NLPCLOUD_API_KEY.\n"
            "Copy .env.example to .env and paste your NLP Cloud API key into it."
        )

    service = NLPService(
        api_key=config.API_KEY,
        ner_model=config.NER_MODEL,
        langdetect_model=config.LANGDETECT_MODEL,
        sentiment_model=config.SENTIMENT_MODEL,
        gpu=config.USE_GPU,
    )
    NLPApp(UserStore(config.USERS_FILE), service).run()


if __name__ == "__main__":
    main()
