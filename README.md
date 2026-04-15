# LLM Evaluator Agent

A production-ready Generative AI system that compares multiple prompt strategies and evaluates LLM outputs using structured scoring metrics.

This project simulates how real-world GenAI systems are built, evaluated, and iteratively improved using prompt engineering and data-driven feedback loops.

---

## 🌐 Live Deployment

- **Frontend (Vercel):** https://llm-evaluator-agent.vercel.app  
- **Backend (Render):** https://llm-evaluator-agent.onrender.com  

---

## 🚀 Key Highlights

### Multi-Agent Architecture
- **Agent A** → Baseline prompt response  
- **Agent B** → Structured prompt response  
- **Evaluator Agent** → LLM-based scoring + comparison  

### LLM Evaluation Framework
- Scores outputs across:
  - Clarity  
  - Completeness  
  - Correctness  
- Selects best response with reasoning  

### Prompt Engineering & Iteration
- Compare multiple prompt strategies (A vs B)  
- Track performance using evaluation metrics  
- Iterate prompts using analytics + feedback  

### Feedback Loop
- Capture user feedback (👍 / 👎)  
- Store:
  - Query  
  - Responses  
  - Evaluation  
  - Context  

### Product Analytics Layer
- Total queries  
- Most common queries  
- Average evaluation scores  
- Winner distribution (A vs B)  

---

## 🧠 Why This Project Matters

Modern GenAI systems are not just about generating responses — they require:

- evaluating output quality  
- refining prompts iteratively  
- measuring performance using data  

This system demonstrates a full pipeline for:

**generation → evaluation → feedback → improvement**

---

## 🛠️ Tech Stack

- **Backend:** FastAPI + Groq API  
- **Frontend:** React (Vite)  
- **Storage:** Local JSON (analytics + feedback persistence)  

---

## 📁 Project Structure

```
backend/app/
├── prompts.py # Prompt definitions (easy to modify)
├── agents.py # Generation + evaluation logic
├── main.py # API routes
├── storage.py # Feedback + analytics storage
frontend/src/
├── App.jsx # UI + API integration
---

## ⚙️ Setup Instructions

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set environment variables:

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama3-70b-8192
```

Run server:

```bash
uvicorn app.main:app --reload --port 8000
```

---

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open:
http://localhost:5173

---

## 🔌 Core API

### POST /api/evaluate

Input:

```json
{ "query": "Explain why loans get rejected" }
```

Output:

* response_a
* response_b
* evaluation:

  * clarity_scores
  * completeness_scores
  * correctness_scores
  * winner
  * reasoning

---

### POST /api/feedback

Stores:

* query
* responses
* evaluation
* user feedback
* timestamp

---

### GET /api/analytics

Returns:

* total queries
* common queries
* average scores
* winner distribution

---

## 🔁 Prompt Iteration Workflow

1. Modify prompts in `prompts.py`
2. Run queries via UI
3. Compare evaluation scores (A vs B)
4. Analyze trends via analytics endpoint
5. Refine prompts and repeat

---

## ⚡ Design Philosophy

* Lightweight and fast to iterate
* Minimal infrastructure, maximum signal
* Focus on evaluation and improvement (not just generation)

---

## 📝 Notes

* Falls back to deterministic mock responses if API key is missing (ensures full pipeline works)
* Easily extensible:

  * Add more prompt variants
  * Improve evaluation rubric
  * Replace storage with database
  * Introduce streaming / real-time feedback
