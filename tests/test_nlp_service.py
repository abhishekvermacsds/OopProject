import unittest

from nlp_app.nlp_service import NLPService, NLPServiceError, language_name


class FakeClient:
    def entities(self, text):
        return {"entities": [
            {"start": 0, "end": 6, "text": "Google", "type": "ORG"},
            {"start": 22, "end": 31, "text": "Bengaluru", "type": "GPE"},
        ]}

    def langdetect(self, text):
        return {"languages": [{"fr": 0.1}, {"en": 0.9}]}

    def sentiment(self, text):
        return {"scored_labels": [
            {"label": "sadness", "score": 0.05},
            {"label": "joy", "score": 0.95},
        ]}


class BrokenClient:
    def entities(self, text):
        raise ConnectionError("boom")


def make_service(client):
    return NLPService(client_factory=lambda model, lang="": client)


class NLPServiceTests(unittest.TestCase):
    def test_entities(self):
        result = make_service(FakeClient()).entities("Google opened an office in Bengaluru")
        self.assertEqual([e["text"] for e in result], ["Google", "Bengaluru"])
        self.assertEqual(result[0]["type"], "ORG")

    def test_language_detection_sorted_by_confidence(self):
        result = make_service(FakeClient()).detect_language("Hello there")
        self.assertEqual(result[0][0], "en")

    def test_sentiment_sorted_by_score(self):
        result = make_service(FakeClient()).sentiment("I love this")
        self.assertEqual(result[0][0], "joy")

    def test_empty_text_rejected(self):
        with self.assertRaises(NLPServiceError):
            make_service(FakeClient()).entities("   ")

    def test_missing_api_key_is_reported_when_using_default_client(self):
        with self.assertRaisesRegex(NLPServiceError, "Missing NLPCLOUD_API_KEY"):
            NLPService().entities("some text")

    def test_api_errors_are_wrapped(self):
        with self.assertRaises(NLPServiceError) as ctx:
            make_service(BrokenClient()).entities("some text")
        self.assertIn("Network error", str(ctx.exception))

    def test_language_name(self):
        self.assertEqual(language_name("hi"), "Hindi")
        self.assertEqual(language_name("xx"), "xx")


if __name__ == "__main__":
    unittest.main()
