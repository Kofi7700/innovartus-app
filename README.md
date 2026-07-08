# Innovartus SaaS Demo

A minimal Flask "SaaS" app built for the Innovartus case study: version control → CI → automatic
cloud deployment → monitoring → scaling evaluation.

## Run locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

## Endpoints

| Route | Purpose |
|---|---|
| `/` | Home page |
| `/health` | Health check (uptime, request count) — point uptime monitors here |
| `/api/stats` | Basic usage stats, simulates a SaaS metrics API |

## Deploy (Render, free tier)

1. Push this repo to GitHub (see steps below).
2. Go to https://render.com → New → Web Service → connect this GitHub repo.
3. Render auto-detects `render.yaml`. Confirm:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Click **Create Web Service**. First deploy takes ~1-3 minutes.
5. Every future `git push` to `main` triggers an automatic redeploy (this is your CI/CD).

## Deploy (Vercel, alternative)

Vercel is optimized for static/Node apps; for Flask, Render or a free AWS Elastic Beanstalk
tier is simpler. If your instructor requires Vercel specifically, use their Python runtime
(`vercel.json` with `@vercel/python`) — ask if you need that variant instead.
