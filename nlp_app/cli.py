"""Interactive command-line interface."""
from __future__ import annotations

from collections import Counter
from getpass import getpass

from .auth import AuthError, UserStore
from .nlp_service import NLPService, NLPServiceError, language_name

SENTIMENT_EMOJI = {
    "joy": "😊", "sadness": "😢", "anger": "😠",
    "fear": "😨", "love": "❤️", "surprise": "😲",
}

BANNER = """
==============================================
        NLP Cloud Toolkit  |  CLI Edition
==============================================
"""

AUTH_MENU = """
How would you like to proceed?
  1. Not a member? Register
  2. Already a member? Login
  3. Galti se aa gaye? Exit
> """

MAIN_MENU = """
Welcome, {name}! What would you like to do?
  1. Named Entity Recognition (NER)
  2. Language Detection
  3. Sentiment Analysis
  4. Logout
> """


class NLPApp:
    def __init__(self, store: UserStore, service: NLPService):
        self._store = store
        self._service = service
        self._user: str | None = None

    # ---- main loop (iterative, so long sessions never hit recursion limits) ----
    def run(self) -> None:
        print(BANNER)
        try:
            while True:
                if self._user is None:
                    if not self._auth_menu():
                        break
                else:
                    self._main_menu()
        except (KeyboardInterrupt, EOFError):
            print()
        print("Goodbye! 👋")

    # ---- menus -------------------------------------------------------
    def _auth_menu(self) -> bool:
        """Return False when the user chooses to exit."""
        choice = input(AUTH_MENU).strip()
        if choice == "1":
            self._register()
        elif choice == "2":
            self._login()
        elif choice == "3":
            return False
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")
        return True

    def _main_menu(self) -> None:
        choice = input(MAIN_MENU.format(name=self._user)).strip()
        actions = {"1": self._ner, "2": self._language_detection, "3": self._sentiment_analysis}
        if choice in actions:
            actions[choice]()
        elif choice == "4":
            self._user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")

    # ---- auth actions ------------------------------------------------
    def _register(self) -> None:
        name = input("Enter name: ")
        email = input("Enter email: ")
        password = getpass("Enter password (min 8 characters): ")
        confirm = getpass("Confirm password: ")

        if password != confirm:
            print("❌ Passwords do not match.")
            return
        try:
            self._store.register(name, email, password)
        except AuthError as exc:
            print(f"❌ {exc}")
            return
        print("✅ Registration successful. Please log in.")

    def _login(self) -> None:
        email = input("Enter email: ")
        password = getpass("Enter password: ")
        try:
            self._user = self._store.authenticate(email, password)
        except AuthError as exc:
            print(f"❌ {exc}")
            return
        print("✅ Login successful.")

    # ---- NLP actions -------------------------------------------------
    @staticmethod
    def _ask_text(prompt: str) -> str:
        return input(prompt).strip()

    def _run(self, func, text: str):
        try:
            return func(text)
        except NLPServiceError as exc:
            print(f"❌ {exc}")
            return None

    def _ner(self) -> None:
        text = self._ask_text("Enter the paragraph: ")
        entities = self._run(self._service.entities, text)
        if entities is None:
            return
        if not entities:
            print("No named entities found.")
            return

        print(f"\nFound {len(entities)} entities:\n")
        print(f"{'ENTITY':<32}{'TYPE':<14}POSITION")
        print("-" * 58)
        for e in entities:
            print(f"{e['text']:<32}{e['type']:<14}{e['start']}-{e['end']}")

        summary = ", ".join(f"{t}: {n}" for t, n in Counter(e["type"] for e in entities).most_common())
        print(f"\nSummary -> {summary}")

    def _language_detection(self) -> None:
        text = self._ask_text("Enter the text: ")
        languages = self._run(self._service.detect_language, text)
        if languages is None:
            return
        if not languages:
            print("Could not detect the language.")
            return

        code, score = languages[0]
        print(f"\n🌐 Detected language: {language_name(code)} ({code}) - {score:.1%} confidence")
        if len(languages) > 1:
            print("Other candidates:")
            for code, score in languages[1:4]:
                print(f"  - {language_name(code)} ({code}): {score:.1%}")

    def _sentiment_analysis(self) -> None:
        text = self._ask_text("Enter the paragraph: ")
        scores = self._run(self._service.sentiment, text)
        if scores is None:
            return
        if not scores:
            print("Could not analyse the sentiment.")
            return

        label, score = scores[0]
        print(f"\n{SENTIMENT_EMOJI.get(label, '🙂')} Dominant emotion: {label.upper()} ({score:.1%})\n")
        for label, score in scores:
            bar = "█" * round(score * 30)
            print(f"  {label:<10}{bar:<30} {score:6.1%}")
