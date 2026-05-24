# Cyber-ctr Startup Website v2

Premium Flask + PostgreSQL startup website for Cyber-ctr.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Deploy on Render

1. Push to GitHub.
2. Create a Web Service from the repo.
3. Add PostgreSQL or use `render.yaml`.
4. Set `SECRET_KEY` and `DATABASE_URL`.
5. Deploy.

## Included

- Responsive premium landing page
- Secure contact form with CSRF protection
- PostgreSQL-ready persistence
- Security headers via Flask-Talisman
- Mobile navigation
- SEO-friendly structure
- Your logo in `static/img/logo.png`
