import unittest

from app import create_app
from app.extensions import db
from app.models import User


class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def register(self, email="person@example.com", password="correct horse battery"):
        return self.client.post("/register", data={
            "name": "Test Person",
            "email": email,
            "password": password,
            "confirm_password": password,
        }, follow_redirects=True)

    def test_registration_hashes_password_and_normalizes_email(self):
        response = self.register(email="  PERSON@EXAMPLE.COM ")

        self.assertEqual(response.status_code, 200)
        user = User.query.one()
        self.assertEqual(user.email, "person@example.com")
        self.assertNotEqual(user.password_hash, "correct horse battery")
        self.assertTrue(user.check_password("correct horse battery"))

    def test_registration_rejects_short_password(self):
        response = self.client.post("/register", data={
            "name": "Test Person",
            "email": "person@example.com",
            "password": "short",
            "confirm_password": "short",
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Use 12 to 128 characters.", response.data)
        self.assertEqual(User.query.count(), 0)

    def test_login_requires_correct_password_and_logout_is_post_only(self):
        self.register()
        self.client.post("/logout")

        invalid = self.client.post("/login", data={
            "email": "person@example.com",
            "password": "wrong password",
        })
        self.assertIn(b"Email or password is incorrect.", invalid.data)

        valid = self.client.post("/login", data={
            "email": "person@example.com",
            "password": "correct horse battery",
        })
        self.assertEqual(valid.status_code, 302)
        self.assertIn("HttpOnly", valid.headers["Set-Cookie"])
        self.assertIn("SameSite=Lax", valid.headers["Set-Cookie"])
        self.assertEqual(self.client.get("/dashboard").status_code, 200)
        self.assertEqual(self.client.get("/logout").status_code, 405)

        self.client.post("/logout")
        self.assertEqual(self.client.get("/dashboard").status_code, 302)

    def test_unknown_account_uses_generic_login_error(self):
        response = self.client.post("/login", data={
            "email": "unknown@example.com",
            "password": "incorrect password",
        })

        self.assertIn(b"Email or password is incorrect.", response.data)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        self.register()
        self.client.post("/logout")

        response = self.register(email="PERSON@example.com")

        self.assertIn(b"An account with that email already exists.", response.data)
        self.assertEqual(User.query.count(), 1)

    def test_csrf_protects_post_requests(self):
        app = create_app({
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
        })
        response = app.test_client().post("/login", data={
            "email": "person@example.com",
            "password": "a sufficiently long password",
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
