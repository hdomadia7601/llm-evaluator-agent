from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents import evaluate_responses, generate_response_a, generate_response_b
from .prompts import PROMPT_VERSION
from .schemas import (
    AnalyticsResponse,
    EvaluateRequest,
    EvaluateResponse,
    FeedbackRecord,
    FeedbackRequest,
)
from .storage import build_analytics, build_export_payload, save_evaluation, save_feedback


app = FastAPI(title="LLM Evaluator Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    response_a = generate_response_a(req.query)
    response_b = generate_response_b(req.query)
    evaluation = evaluate_responses(req.query, response_a, response_b)

    record = EvaluateResponse(
        query=req.query,
        response_a=response_a,
        response_b=response_b,
        evaluation=evaluation,
        model_a="llama-3.1-8b-instant",
        model_b="mixtral-8x7b-32768",
        prompt_version=PROMPT_VERSION,
        user_feedback=None,
        timestamp=datetime.now(timezone.utc),
    )

    save_evaluation(record)
    return record


@app.post("/api/feedback")
def feedback(req: FeedbackRequest) -> dict[str, str]:
    record = FeedbackRecord(
        **req.model_dump(),
        prompt_version=req.prompt_version or PROMPT_VERSION,
        user_feedback=req.feedback,
        timestamp=datetime.now(timezone.utc),
    )
    save_feedback(record)
    return {"status": "stored"}


@app.get("/api/analytics", response_model=AnalyticsResponse)
def analytics() -> AnalyticsResponse:
    return AnalyticsResponse(**build_analytics())


@app.get("/export")
def export_data() -> dict:
    return build_export_payload()