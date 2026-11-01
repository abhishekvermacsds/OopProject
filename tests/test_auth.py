import tempfile
import unittest
from pathlib import Path

from nlp_app.auth import AuthError, UserStore


class UserStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "users.json"
        self.store = UserStore(self.path)

    def test_register_and_login(self):
        self.store.register("Asha", "Asha@Example.com", "supersecret1")
        self.assertEqual(self.store.authenticate("asha@example.com", "supersecret1"), "Asha")

    def test_password_is_not_stored_in_plain_text(self):
        self.store.register("Asha", "asha@example.com", "supersecret1")
        self.assertNotIn("supersecret1", self.path.read_text())

    def test_duplicate_email_rejected(self):
        self.store.register("Asha", "asha@example.com", "supersecret1")
        with self.assertRaises(AuthError):
            self.store.register("Other", "ASHA@example.com", "anotherpass1")

    def test_wrong_password_rejected(self):
        self.store.register("Asha", "asha@example.com", "supersecret1")
        with self.assertRaises(AuthError):
            self.store.authenticate("asha@example.com", "wrongpassword")

    def test_unknown_email_rejected(self):
        with self.assertRaises(AuthError):
            self.store.authenticate("nobody@example.com", "whatever123")

    def test_validation(self):
        with self.assertRaises(AuthError):
            self.store.register("", "a@b.com", "supersecret1")
        with self.assertRaises(AuthError):
            self.store.register("Asha", "not-an-email", "supersecret1")
        with self.assertRaises(AuthError):
            self.store.register("Asha", "a@b.com", "short")

    def test_accounts_persist_between_sessions(self):
        self.store.register("Asha", "asha@example.com", "supersecret1")
        self.assertEqual(UserStore(self.path).authenticate("asha@example.com", "supersecret1"), "Asha")


if __name__ == "__main__":
    unittest.main()
