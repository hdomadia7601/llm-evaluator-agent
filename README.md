# LLM Evaluator Agent

Production-ready, minimal GenAI system that compares two prompt strategies and evaluates output quality with a structured rubric.

## What this demonstrates

- Multi-agent flow:
  - Response Generation Agent A (baseline prompt)
  - Response Generation Agent B (structured prompt)
  - Evaluation Agent (scores clarity, completeness, correctness)
- Structured JSON evaluation outputs
- Prompt engineering impact (A vs B)
- Feedback loop (thumbs up/down persisted with context)
- Product analytics (query count, common queries, average scores, winner distribution)

## Tech Stack

- Backend: FastAPI + OpenAI API
- Frontend: React (Vite)
- Storage: Local JSON files (`backend/data/*.json`)

## Project Structure

- `backend/app/prompts.py` -> all editable prompts
- `backend/app/agents.py` -> generation + evaluation agent orchestration
- `backend/app/main.py` -> API routes
- `backend/app/storage.py` -> feedback/evaluation persistence + analytics
- `frontend/src/App.jsx` -> UI and API integration

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set your OpenAI key in `.env`:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Run backend:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`).

## Core API

- `POST /api/evaluate`
  - Input: `{ "query": "..." }`
  - Output:
    - `response_a`
    - `response_b`
    - `evaluation`:
      - `clarity_scores`
      - `completeness_scores`
      - `correctness_scores`
      - `winner`
      - `reasoning`
- `POST /api/feedback`
  - Stores thumbs up/down feedback with query, responses, evaluation, timestamp
- `GET /api/analytics`
  - Returns total queries, common queries, average scores, winner distribution

## Prompt Iteration Workflow

1. Edit prompts in `backend/app/prompts.py`.
2. Run sample queries from UI.
3. Compare winner distribution and average scores in analytics.
4. Capture user feedback via thumbs up/down.
5. Iterate prompts and re-evaluate.

## Notes

- If `OPENAI_API_KEY` is not set, backend falls back to deterministic mock responses so the pipeline remains testable.
- The architecture is intentionally lightweight and easy to extend (e.g., add more generation variants, stricter evaluator schema, persistent DB later).
