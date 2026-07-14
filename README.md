# News Signal

Search recent news, trigger an AI summary + sentiment analysis, and browse the
history of everything you've analyzed.

## Stack

- **Backend:** FastAPI (async), Motor (async MongoDB driver), httpx, OpenAI SDK
- **Frontend:** React + TypeScript, Vite, no UI framework — plain CSS with a small
  design-token system
- **DB:** MongoDB, one collection (`analyzed_articles`), unique index on `url`

## Why it's built this way

- **One OpenAI call per article**, not two — a single prompt returns structured
  JSON with both the summary and the sentiment. Cheaper, faster, and there's
  exactly one round trip to reason about.
- **Dedup by URL.** Before calling OpenAI, the backend checks Mongo for an
  existing analysis of that URL and returns it instantly if found. This is the
  product decision that makes article selection "useful, not arbitrary" — the
  UI visibly tells you when something's already been filed, and it protects a
  100-req/day free news API tier from repeat calls.
- **Service layer** (`services/news_service.py`, `services/ai_service.py`) is
  separated from the router, so swapping the news provider or AI vendor later
  doesn't touch the API surface.
- **Pydantic schemas** are the single source of truth for API shape; the
  frontend's `types.ts` mirrors them by hand (small enough project that codegen
  isn't worth the setup time here, but it's a reasonable next step).

## Running with Docker (single command)

```bash
cp .env.example .env   # fill in GNEWS_API_KEY and OPENAI_API_KEY
docker compose up --build
```

That's it. This starts three containers — Mongo, the FastAPI backend, and the
frontend served via Nginx (which proxies `/api` to the backend over the
Docker network) — and wires them together.

- Frontend: http://localhost:8080
- Backend directly (if you want to hit the API or check `/api/health`): http://localhost:8000

Mongo data persists in a named volume (`mongo_data`) across restarts. To wipe it:

```bash
docker compose down -v
```

## Running locally (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GNEWS_API_KEY and OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Requires a local MongoDB instance (or point `MONGODB_URI` at Atlas).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://localhost:8000` in dev (see `vite.config.ts`),
so no CORS setup is needed locally beyond what's already in `main.py`.

Visit `http://localhost:5173`.

## API

| Method | Path                     | Description                                  |
|--------|--------------------------|-----------------------------------------------|
| GET    | `/api/articles/search`   | `?q=...` — search recent articles via GNews  |
| POST   | `/api/articles/analyze`  | Summarize + score sentiment (or return cached result) |
| GET    | `/api/articles/history`  | All previously analyzed articles, newest first |

## Possible next steps

- Pagination on `/history`
- Retry/backoff on the GNews and OpenAI calls
- Swap the hand-written `types.ts` for generated types from the OpenAPI schema
- Rate limiting on `/analyze` if this were public
