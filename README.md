# Secure Auth

A small Flask login app with password hashing, CSRF-protected forms, and authenticated routes.

## Run locally

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. Generate a secret with
   `python -c "import secrets; print(secrets.token_hex(32))"` and put the result in
   `SECRET_KEY` in `.env`.

4. Create the database tables and start the app:

   ```powershell
   flask --app run.py db upgrade
   python run.py
   ```

   Visit <http://127.0.0.1:5000>.

## Security notes

- Passwords are hashed with Werkzeug's password-hashing helper; the app never stores the original password.
- New passwords must be at least 12 characters. Login failures use one generic message.
- Flask-WTF validates CSRF tokens on all state-changing forms, including sign out.
- Session cookies are HTTP-only and same-site by default. Set `SESSION_COOKIE_SECURE=true` when serving over HTTPS.
- Keep `SECRET_KEY` private and use HTTPS in production. Configure your production server and database separately; the built-in Flask development server is for local use only.

## Tests

```powershell
python -m unittest discover -s tests
```
