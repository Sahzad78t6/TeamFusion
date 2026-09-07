# GrowthOS Backend — Environment Variables Checklist

> Use this file to fill in environment variables in **Render → Dashboard → Environment**.  
> **Never commit real secrets to this file or any other tracked file.**  
> The `.env` file in `backend/` is git-ignored and is safe for local development only.

---

## How to apply on Render
1. Go to your Render service → **Environment** tab.
2. Click **Add Environment Variable** for each row below.
3. After adding all variables, click **Save Changes** → Render will automatically redeploy.

---

## Required Variables (core function broken without these)

| Variable | Current Default | Required For | Where to Get It |
|----------|----------------|-------------|-----------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | **All data storage** | MongoDB Atlas → Connect → "Connect your application" → copy the connection string. Use Atlas free tier (M0). |
| `SECRET_KEY` | `development-only-change-me-before-deploying` | **JWT auth** | Run `python -c "import secrets; print(secrets.token_hex(32))"` locally — paste the output. |
| `OPENAI_API_KEY` | `YOUR_OPENAI_API_KEY` | **All LLM agent calls** (planner, reflection, opportunity, curator re-ranking) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys). Free $5 credit on new accounts; `gpt-4o-mini` is very cheap. |

> [!CAUTION]
> If `OPENAI_API_KEY` is missing or still `YOUR_OPENAI_API_KEY`, **every agent falls back to hardcoded deterministic data**. You will see `FALLBACK TRIGGER:` error lines in Render's log stream. The health endpoint at `GET /health` will show `"llm_configured": false`.

---

## Search Provider Variables (at least ONE required for curator live-search)

The curator needs at least one of these to fetch real resources. On cloud hosts like Render, DuckDuckGo scraping is unreliable — set a real API key.

| Variable | Required For | Tier / Cost | Where to Get It |
|----------|-------------|-------------|-----------------|
| `YOUTUBE_API_KEY` | YouTube video search in curator | Free (10,000 units/day quota) | [console.cloud.google.com](https://console.cloud.google.com) → Create project → APIs & Services → Enable "YouTube Data API v3" → Credentials → API Key |
| `SERPER_API_KEY` | Web article/course search | 2,500 free queries/month | [serper.dev](https://serper.dev) → Sign up → Dashboard → API Key |
| `TAVILY_API_KEY` | Web article search (alternative to Serper) | 1,000 free searches/month | [tavily.com](https://tavily.com) → Sign up → API Keys |
| `GOOGLE_SEARCH_KEY` | Google Custom Search (alternative) | 100 free queries/day | [console.cloud.google.com](https://console.cloud.google.com) → Custom Search JSON API → Credentials |
| `GOOGLE_CX` | Paired with `GOOGLE_SEARCH_KEY` | — | [programmablesearchengine.google.com](https://programmablesearchengine.google.com) → New engine → Search engine ID |

> [!IMPORTANT]
> If **all** search provider keys are missing, `GET /health` will show `"any_configured": false` under `search`. The curator will raise `YouTubeUnavailableError` and return no results. You must set at least `YOUTUBE_API_KEY` or `SERPER_API_KEY`.

**Recommended minimum**: Set `YOUTUBE_API_KEY` (free, instant) + `SERPER_API_KEY` (free tier generous).

---

## Optional Variables (graceful degradation when missing)

| Variable | Default | Degrades To | Where to Get It |
|----------|---------|-------------|-----------------|
| `MEM0_API_KEY` | `""` (empty) | In-memory local dict store (ephemeral, lost on restart) | [mem0.ai](https://mem0.ai) → Sign up → API Keys |
| `GOOGLE_CLIENT_ID` | `""` | Google OAuth login disabled | [console.cloud.google.com](https://console.cloud.google.com) → Credentials → OAuth 2.0 Client IDs |
| `GOOGLE_CLIENT_SECRET` | `""` | Google OAuth login disabled | Same as above |
| `GROQ_API_KEY` | `""` | Not used (legacy — runtime uses OpenAI) | Not needed. This field is a leftover from an earlier migration. |
| `MONGODB_DB_NAME` | `growthos` | Uses default | Change if you want a different Atlas database name |
| `OPENAI_MODEL` | `gpt-4o-mini` | — | Override to use `gpt-4o` or `gpt-4-turbo` if budget allows |

---

## Variables with Fixed Values (do not change without code review)

| Variable | Value | Notes |
|----------|-------|-------|
| `GOOGLE_OAUTH_REDIRECT_URI` | `https://teamfusion-96bi.onrender.com` | Must match exactly what's registered in Google Cloud Console |
| `FRONTEND_URL` | `https://team-fusion-psi.vercel.app` | Used for CORS and OAuth redirect |
| `ENV` | `production` | Set this to `production` on Render (controls logging verbosity) |

---

## Quick Verification After Applying Keys

After saving env vars and waiting for Render to redeploy, hit:

```
GET https://teamfusion-96bi.onrender.com/health
```

Expected response when keys are correctly set:

```json
{
  "integrations": {
    "llm": {
      "provider": "openai",
      "configured": true,
      "warning": null
    },
    "search": {
      "youtube": true,
      "serper": true,
      "any_configured": true,
      "warning": null
    }
  }
}
```

If `configured: false` or `warning` is non-null, the variable is not set correctly.

---

## Known Gaps (Separate Tasks — Not Fixed in Phase 0)

| Gap | Location | Status |
|-----|----------|--------|
| ML growth predictor is a hardcoded formula, not a trained model | `backend/app/ml/growth_predictor.py` | Documented. Requires real training pipeline. |
| ML burnout predictor is a hardcoded formula, not a trained model | `backend/app/ml/burnout_predictor.py` | Documented. Requires labelled burnout dataset + sklearn pipeline. |
| Embeddings fall back to hash-based vectors when OpenAI key missing | `backend/app/llm/embeddings.py` | Acceptable for MVP; requires `OPENAI_API_KEY` for real semantic matching. |
| Notification agent is fully deterministic (no LLM) | `backend/app/agents/notification/tools.py` | By design — template notifications, not a fallback. Low priority. |
| User understanding agent falls back to raw field normalization | `backend/app/agents/user_understanding/tools.py` | Sensible graceful degrade for no-chat-history case. Low priority. |
