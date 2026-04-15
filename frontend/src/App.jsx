import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function ScoreRow({ label, a, b }) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <span>A: {a}</span>
      <span>B: {b}</span>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("What is retrieval-augmented generation?");
  const [result, setResult] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");

  const fetchAnalytics = async () => {
    const resp = await fetch(`${API_BASE}/api/analytics`);
    const data = await resp.json();
    setAnalytics(data);
  };

  useEffect(() => {
    fetchAnalytics().catch(() => null);
  }, []);

  const runEvaluation = async () => {
    if (!query.trim()) {
      return;
    }
    setLoading(true);
    setFeedbackMessage("");
    try {
      const resp = await fetch(`${API_BASE}/api/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await resp.json();
      setResult(data);
      await fetchAnalytics();
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (feedback) => {
    if (!result) return;
    await fetch(`${API_BASE}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: result.query,
        response_a: result.response_a,
        response_b: result.response_b,
        evaluation: result.evaluation,
        feedback,
        prompt_version: result.prompt_version,
      }),
    });
    setFeedbackMessage("Feedback saved.");
  };

  const downloadExportData = async () => {
    const resp = await fetch(`${API_BASE}/export`);
    const data = await resp.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "evaluation-export.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container">
      <h1>LLM Evaluator Agent</h1>
      <p className="subtitle">Compare two prompt strategies and score quality.</p>

      <div className="input-panel">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          placeholder="Enter your query"
        />
        <div className="button-row">
          <button onClick={runEvaluation} disabled={loading}>
            {loading ? "Evaluating responses..." : "Evaluate"}
          </button>
          <button onClick={runEvaluation} disabled={loading}>
            Regenerate
          </button>
          <button onClick={downloadExportData} disabled={loading}>
            Download Evaluation Data
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="responses">
            <section>
              <h2>Response A (Baseline)</h2>
              <pre>{result.response_a}</pre>
            </section>
            <section>
              <h2>Response B (Structured Prompt)</h2>
              <pre>{result.response_b}</pre>
            </section>
          </div>

          <div className="evaluation">
            <h2>Evaluation</h2>
            <ScoreRow
              label="Clarity"
              a={result.evaluation.clarity_scores.a}
              b={result.evaluation.clarity_scores.b}
            />
            <ScoreRow
              label="Completeness"
              a={result.evaluation.completeness_scores.a}
              b={result.evaluation.completeness_scores.b}
            />
            <ScoreRow
              label="Correctness"
              a={result.evaluation.correctness_scores.a}
              b={result.evaluation.correctness_scores.b}
            />
            <p>
              <strong>Winner:</strong> {result.evaluation.winner}
            </p>
            <p className="meta-text">Prompt version: {result.prompt_version}</p>
            <p>{result.evaluation.reasoning}</p>
            <div className="button-row">
              <button onClick={() => submitFeedback("up")}>Thumbs Up</button>
              <button onClick={() => submitFeedback("down")}>Thumbs Down</button>
            </div>
            {feedbackMessage && <p className="feedback-msg">{feedbackMessage}</p>}
          </div>
        </>
      )}

      {analytics && (
        <div className="analytics">
          <h2>Analytics</h2>
          <p>Total queries: {analytics.total_queries}</p>
          <p>
            Winner distribution: A {analytics.winner_distribution.A} / B{" "}
            {analytics.winner_distribution.B}
          </p>
          <p>
            Avg clarity: A {analytics.average_evaluation_scores.clarity.a} / B{" "}
            {analytics.average_evaluation_scores.clarity.b}
          </p>
          <p>
            Avg completeness: A {analytics.average_evaluation_scores.completeness.a} / B{" "}
            {analytics.average_evaluation_scores.completeness.b}
          </p>
          <p>
            Avg correctness: A {analytics.average_evaluation_scores.correctness.a} / B{" "}
            {analytics.average_evaluation_scores.correctness.b}
          </p>
        </div>
      )}
    </div>
  );
}
