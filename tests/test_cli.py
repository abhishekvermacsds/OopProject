import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nlp_app.auth import UserStore
from nlp_app.cli import NLPApp


class FakeService:
    def entities(self, text):
        return [{"text": "Google", "type": "ORG", "start": 0, "end": 6}]

    def detect_language(self, text):
        return [("en", 0.99), ("fr", 0.01)]

    def sentiment(self, text):
        return [("joy", 0.9), ("sadness", 0.1)]


class CLIFlowTest(unittest.TestCase):
    def test_full_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = NLPApp(UserStore(Path(tmp) / "users.json"), FakeService())
            inputs = iter([
                "1", "Asha", "asha@example.com",      # register
                "2", "asha@example.com",              # login
                "1", "Google is big",                 # NER
                "2", "Hello world",                   # language detection
                "3", "I love this",                   # sentiment
                "4",                                  # logout
                "3",                                  # exit
            ])
            passwords = iter(["password123", "password123", "password123"])

            out = io.StringIO()
            with patch("builtins.input", lambda *_: next(inputs)), \
                 patch("nlp_app.cli.getpass", lambda *_: next(passwords)), \
                 contextlib.redirect_stdout(out):
                app.run()

        text = out.getvalue()
        for expected in ("Registration successful", "Login successful", "Google",
                         "English", "JOY", "Logged out", "Goodbye"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
