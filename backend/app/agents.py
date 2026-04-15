import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from .prompts import PROMPT_AGENT_A, PROMPT_AGENT_B, PROMPT_EVALUATOR
from .schemas import EvaluationResult


load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self.model = "llama-3.1-8b-instant"
        api_key = os.getenv("GROQ_API_KEY")
        self.enabled = bool(api_key)
        self.client = Groq(api_key=api_key) if self.enabled else None

    def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.enabled or self.client is None:
            return self._mock_response(system_prompt=system_prompt, user_prompt=user_prompt)

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return resp.choices[0].message.content or ""

    @staticmethod
    def _mock_response(system_prompt: str, user_prompt: str) -> str:
        if "Evaluation Agent" in system_prompt:
            return json.dumps(
                {
                    "clarity_scores": {"a": 6, "b": 8},
                    "completeness_scores": {"a": 6, "b": 8},
                    "correctness_scores": {"a": 7, "b": 8},
                    "winner": "B",
                    "reasoning": "Mock evaluator output: Response B is more structured and complete.",
                }
            )
        if "Agent B" in system_prompt:
            return (
                "- Mock structured answer for testing\n"
                "- Includes clearer formatting and practical explanation\n"
                "- Example: This is where a real LLM answer appears\n"
                "- Now powered by Groq (free LLM)\n"
            )
        return "Mock baseline answer (Groq key missing). Add GROQ_API_KEY to get live outputs."


llm_client = LLMClient()


def generate_response_a(query: str) -> str:
    return llm_client.complete(system_prompt=PROMPT_AGENT_A, user_prompt=query, temperature=0.5).strip()


def generate_response_b(query: str) -> str:
    return llm_client.complete(system_prompt=PROMPT_AGENT_B, user_prompt=query, temperature=0.4).strip()


def _coerce_json_block(raw_text: str) -> dict[str, Any]:
    raw_text = raw_text.strip()
    if raw_text.startswith("{") and raw_text.endswith("}"):
        return json.loads(raw_text)

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(raw_text[start : end + 1])
    raise ValueError("No JSON object found in evaluator response")


def evaluate_responses(query: str, response_a: str, response_b: str) -> EvaluationResult:
    eval_prompt = (
        f"User Query:\n{query}\n\n"
        f"Response A:\n{response_a}\n\n"
        f"Response B:\n{response_b}\n\n"
        "Return JSON only."
    )
    raw = llm_client.complete(system_prompt=PROMPT_EVALUATOR, user_prompt=eval_prompt, temperature=0.0)
    try:
        parsed = _coerce_json_block(raw)
        return EvaluationResult.model_validate(parsed)
    except (ValueError, json.JSONDecodeError, ValidationError):
        return EvaluationResult(
            clarity_scores={"a": 5, "b": 5},
            completeness_scores={"a": 5, "b": 5},
            correctness_scores={"a": 5, "b": 5},
            winner="B",
            reasoning="Evaluator returned non-parseable output. Fallback scores were used.",
        )