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
  const [darkMode, setDarkMode] = useState(false);

  const fetchAnalytics = async () => {
    const resp = await fetch(`${API_BASE}/api/analytics`);
    const data = await resp.json();
    setAnalytics(data);
  };

  useEffect(() => {
    fetchAnalytics().catch(() => null);
  }, []);

  const runEvaluation = async () => {
    if (!query.trim()) return;

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

  return (
    <div className={`container ${darkMode ? "dark" : "light"}`}>
      
      {/* HEADER */}
      <div className="header">
        <div>
          <h1>LLM Evaluator</h1>
          <p className="subtitle">
            Compare outputs from multiple LLMs and evaluate quality
          </p>
        </div>

        <button
          onClick={() => setDarkMode(!darkMode)}
          className="toggle-btn"
        >
          {darkMode ? "🌙 Dark" : "🌞 Light"}
        </button>
      </div>

      {/* INPUT */}
      <div className="input-panel">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          placeholder="Enter your query..."
        />

        <div className="button-row">
          <button onClick={runEvaluation} disabled={loading}>
            {loading ? "Evaluating..." : "Evaluate"}
          </button>
        </div>
      </div>

      {/* RESPONSES */}
      {result && (
        <div className="responses">
          <section>
            <h2>Response A</h2>
            <p className="model-name">{result.model_a}</p>
            <pre>{result.response_a}</pre>
          </section>

          <section>
            <h2>Response B</h2>
            <p className="model-name">{result.model_b}</p>
            <pre>{result.response_b}</pre>
          </section>
        </div>
      )}

      {/* EVALUATION */}
      {result && (
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

          <p className="meta-text">
            Prompt version: {result.prompt_version}
          </p>

          <p>{result.evaluation.reasoning}</p>

          <div className="button-row">
            <button onClick={() => submitFeedback("up")}>👍</button>
            <button onClick={() => submitFeedback("down")}>👎</button>
          </div>

          {feedbackMessage && (
            <p className="feedback-msg">{feedbackMessage}</p>
          )}
        </div>
      )}

      {/* ANALYTICS */}
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
            Avg completeness: A{" "}
            {analytics.average_evaluation_scores.completeness.a} / B{" "}
            {analytics.average_evaluation_scores.completeness.b}
          </p>

          <p>
            Avg correctness: A{" "}
            {analytics.average_evaluation_scores.correctness.a} / B{" "}
            {analytics.average_evaluation_scores.correctness.b}
          </p>
        </div>
      )}
    </div>
  );
}