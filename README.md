# 💼 Job Market Intelligence & Salary Prediction

**A salary predictor with ML models built from scratch — plus a Groq-powered AI agent
that explains *why*.** The number comes from real, hand-written regression models (Ridge,
decision tree, random forest, gradient boosting — no scikit-learn, no black box). The
*explanation* — what's actually driving that number, and what would move it — comes from
an optional AI layer that reads the prediction, your profile, and live market skill-demand
data, and writes an actual, specific answer.

Messy real-world job postings in ("₹8-12 LPA", "$80,000", "Not disclosed") → clean
relational data → skill-demand analytics → a salary model → an AI agent that turns the
model's output into career advice.

---

## ✨ What it does

| Stage | What happens |
|---|---|
| 🧹 **Clean** | Free-text salary parsing (`₹8-12 LPA` / `$80,000` / `Not disclosed` → normalized INR min/max/mid), categorical normalization |
| 🔍 **Extract** | Dictionary-based skill extraction from job descriptions into a standardized taxonomy |
| 🗄️ **Store** | PostgreSQL, many-to-many `jobs ↔ skills` schema — real relational modeling, not a flat CSV |
| 📊 **Analyze** | Most in-demand skills, salary by role/location/experience, skill salary premium |
| 🤖 **Predict** | 4 regression models, **all built from scratch in NumPy**, compared head-to-head against a mean baseline |
| 🧠 **Explain (optional)** | A Groq LLM agent turns the raw prediction into a specific, written career insight |

## 🧮 The ML — and why it's hand-written

Ridge regression (closed-form normal equation), a CART decision tree (vectorized split
search), random forest (bagging + feature subsampling), and gradient boosting (additive
trees on residuals) — **all implemented directly on `numpy.linalg`, zero scikit-learn.**

That started as a workaround (scikit-learn/scipy trip a Windows Application Control DLL
block on the dev machine — `scipy.sparse` transitively imports `numpy.fft`, which gets
blocked) but turned into the better story: it shows the actual algorithms, not just
`.fit()`. Verified results on the synthetic dataset:

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Baseline (mean) | 378,514 | 467,491 | −0.003 |
| Linear Regression (Ridge) | 111,712 | 145,617 | 0.903 |
| Decision Tree | 180,156 | 236,626 | 0.743 |
| Random Forest | 158,308 | 206,593 | 0.804 |
| **Gradient Boosting** ⭐ | **106,598** | **139,917** | **0.910** |

Every model clearly beats the "always guess the average" floor — the point of comparing
against a baseline at all.

## 🤖 The agentic AI layer (Groq)

The salary *number* always comes from the from-scratch models above — the LLM never
touches it. But a raw number without context isn't that useful. Set a `GROQ_API_KEY` and
every prediction also gets an **AI Career Insight**: the agent is handed the prediction,
the full profile (role, location, experience, education, skills), *and* the current
top-10 most in-demand skills in the market — and writes 3–4 specific sentences on what's
driving the number and the single most useful thing to do about it.

```bash
cp .env.example .env
# edit .env: GROQ_API_KEY=your-key-here   (free at console.groq.com)
```

Restart the backend after editing `.env`. No key → prediction works exactly the same,
minus the AI panel. No silent failures, no broken requests either way.

---

## 🏗️ Project layout

```
job-market-intelligence/
├── config/settings.py            # paths, currency conversion constants, DB URL
├── data/{raw,processed}/
├── src/job_market/
│   ├── ingestion/load_data.py    # CSV load + profiling
│   ├── cleaning/
│   │   ├── salary_parser.py      # "₹8-12 LPA" / "$80,000" / "Not disclosed" -> INR min/max/mid
│   │   └── clean.py              # categorical normalization + orchestration
│   ├── nlp/
│   │   ├── skills_taxonomy.json  # canonical skill -> synonyms
│   │   └── skill_extractor.py    # dictionary/synonym skill extraction from JDs
│   ├── features/engineer.py      # FeatureBuilder: one-hot categoricals + skill binaries
│   ├── db/                       # connection.py, loader.py (jobs / skills / job_skills)
│   ├── ml/
│   │   ├── metrics.py            # MAE, RMSE, R2 (numpy)
│   │   ├── splitting.py          # train_test_split, StandardScaler (numpy)
│   │   ├── baseline.py           # mean-predictor floor
│   │   ├── linear_regression.py  # Ridge via normal equation
│   │   ├── decision_tree.py      # CART regressor, vectorized split search
│   │   ├── random_forest.py      # bagging + feature subsampling
│   │   ├── gradient_boosting.py  # additive trees on residuals
│   │   ├── feature_importance.py
│   │   └── train.py              # trains + compares all models
│   ├── llm/groq_client.py        # 🤖 the agentic layer — AI Career Insight
│   ├── analysis/market_eda.py    # skill demand, salary by role/location/experience
│   └── pipeline.py               # end-to-end orchestration
├── sql/{schema.sql, queries/}    # most-demanded skills, salary by role/location, skill premium
├── backend/main.py               # FastAPI app: /api/* + POST /api/predict + serves built frontend
├── frontend/                     # React (Vite) SPA: Overview / Skill Demand / Salary Intelligence / Predictor
├── scripts/                      # generate_sample_jobs, run_pipeline, load_to_postgres
├── tests/                        # pytest — 17 tests: salary parsing, skill extraction, metrics, models
├── docker-compose.yml            # local Postgres (port 5433, separate from project 1's)
└── requirements.txt
```

## 📦 Data

`data/raw/job_postings.csv` needs columns: `job_id, job_title, company, location,
experience_years, education, skills_text, salary_text, employment_type, industry,
job_description`. `salary_text` is expected to be messy/inconsistent — that's the point.

Sourcing options: `python scripts/generate_sample_jobs.py` (synthetic, with a real
underlying salary formula + noise so the models have genuine signal to learn, not pure
randomness) for now; swap in a sourced dataset (e.g. Kaggle) later using the same columns.

---

## 🚀 Running it

`run_pipeline.py` must be run at least once before the backend — it produces
`data/processed/jobs_clean.parquet` and the trained models in `models/` that the
`/api/predict` endpoint loads:

```bash
pip install -r requirements.txt
python scripts/generate_sample_jobs.py   # sample data
python scripts/run_pipeline.py           # clean, engineer features, train + compare models
```

Then two terminals — one for the backend, one for the frontend:

```bash
# terminal 1 — backend
cd backend
uvicorn main:app --reload --port 8000

# terminal 2 — frontend
cd frontend
npm install
npm start
```

Open **http://localhost:5173** — Vite's dev server proxies `/api` to the backend on 8000.

<details>
<summary>Optional: SQL analytics layer (Postgres via Docker)</summary>

```bash
docker compose up -d
cp .env.example .env
python scripts/load_to_postgres.py
```
</details>

<details>
<summary>Single-process production build (one port, no hot reload)</summary>

```bash
cd frontend && npm run build && cd ../backend
uvicorn main:app --port 8000
```

`main.py` auto-detects `frontend/dist/` and serves it directly when present.
</details>

## ✅ Tests

```bash
pytest
```

17 tests: salary-string parsing edge cases, skill extraction, metrics correctness, and
sanity checks on every from-scratch model (fits a known linear signal, beats a baseline,
random forest beats a single tree on noisy data, feature importances sum to 1).

---

## 🧠 Design notes — the "why", not just the "what"

- **Why parse salary instead of dropping messy rows?** Real postings mix "₹8-12 LPA",
  "$80,000", "Not disclosed" — the parsing logic itself (`cleaning/salary_parser.py`) is
  the interesting engineering, and dropping them all would throw away most of the dataset.
- **Why one-hot cap + "top-K" skills instead of full dummy encoding?** Job titles/locations
  can have long tails; capping to the top N categories (`FeatureBuilder`) keeps the feature
  space bounded and avoids one-hot columns with a handful of training examples each.
- **Why compare against a mean baseline?** Any model that can't beat "always predict the
  average salary" isn't learning a useful signal — it's the floor every real model must clear.
- **Why MAE *and* RMSE *and* R²?** MAE is robust and interpretable (average rupee error);
  RMSE penalizes large misses more; R² gives a scale-free sense of variance explained. No
  single metric tells the whole story on noisy salary data.
- **Why keep the LLM out of the prediction itself?** The number needs to be reproducible
  and testable; the AI layer earns its place by doing what the model can't — turning a
  number into a specific, contextual explanation — not by quietly replacing the math.
- **Prediction range is not invented.** The UI shows ±10% around the point estimate as a
  stated approximation, not a true prediction interval — documented as exactly that rather
  than presented as more rigorous than it is.
