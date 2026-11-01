# TITAN AI — Starter v0.1

A small cloud-deployable dashboard for tracking tasks, opportunities and income. It is intentionally a safe foundation, not an autonomous money-making bot.

## Deploy from your Tecno Spark 8

1. Create/sign in to a GitHub account in your phone browser.
2. Create a new repository named `titan-ai-starter`.
3. Upload all files and folders from this project ZIP, preserving the `static` folder.
4. Create/sign in to Render in your phone browser.
5. In Render, choose **New > Web Service**, connect the GitHub repository, and use the settings in `render.yaml` (or enter the build and start commands shown there).
6. Open the deployed service URL. The dashboard should load. Visit `/health` to check the service.

## Important limitations

- Free hosting can sleep, impose limits, or change its free tier. This does not guarantee 24/7 operation.
- The starter uses SQLite. On many free cloud hosts, local files are ephemeral and can be lost on restart/redeploy. Do not use it as the only record of important financial data. Before relying on it, connect a persistent database such as a properly secured hosted PostgreSQL/Supabase database.
- It does not yet connect to an AI model or automatically search job sites. Those integrations need API access, terms-of-service checks, and often paid usage. Start with free/manual opportunity tracking.
- It does not create bank/Binance accounts, handle credentials, submit applications, place bets, trade, or transfer money.
- Never share passwords, OTP codes, mobile-money PINs, bank credentials or crypto seed phrases with an AI.

## Local test (optional)

Python 3.10+:
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```
Then open `http://127.0.0.1:8000`.

## Roadmap

1. Add persistent database.
2. Add a vetted job-search connector and Rwanda eligibility checks.
3. Add an AI planning assistant with human approval.
4. Add customer-approved work tools (document drafting, translation, image/video workflows).
5. Add payment reconciliation using official provider integrations only.
