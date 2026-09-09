import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function SalaryPredictor() {
  const [options, setOptions] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [form, setForm] = useState({
    job_title: "", location: "", education: "", experience_years: 3,
    employment_type: "", industry: "", skills: ["Python", "SQL"],
  });
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.options().then((opts) => {
      setOptions(opts);
      setForm((f) => ({
        ...f,
        job_title: opts.job_titles[0],
        location: opts.locations[0],
        education: opts.education[0],
        employment_type: opts.employment_types[0],
        industry: opts.industries[0],
      }));
    }).catch((e) => setError(e.message));
    api.modelComparison().then(setComparison).catch((e) => setError(e.message));
  }, []);

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const toggleSkill = (skill) => {
    setForm((f) => ({
      ...f,
      skills: f.skills.includes(skill) ? f.skills.filter((s) => s !== skill) : [...f.skills, skill],
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      setPrediction(await api.predict(form));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (error && !options) return <p className="error">{error}</p>;
  if (!options) return <p>Loading…</p>;

  return (
    <div>
      <h2>Salary Predictor {comparison && `(model: ${comparison.best_model})`}</h2>

      <div className="panel">
        <div className="form-grid">
          <div className="field">
            <label>Role</label>
            <select value={form.job_title} onChange={(e) => update("job_title", e.target.value)}>
              {options.job_titles.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Location</label>
            <select value={form.location} onChange={(e) => update("location", e.target.value)}>
              {options.locations.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Education</label>
            <select value={form.education} onChange={(e) => update("education", e.target.value)}>
              {options.education.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Experience (years)</label>
            <input
              type="number" min={0} max={20} step={0.5}
              value={form.experience_years}
              onChange={(e) => update("experience_years", parseFloat(e.target.value))}
            />
          </div>
          <div className="field">
            <label>Employment Type</label>
            <select value={form.employment_type} onChange={(e) => update("employment_type", e.target.value)}>
              {options.employment_types.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Industry</label>
            <select value={form.industry} onChange={(e) => update("industry", e.target.value)}>
              {options.industries.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
        </div>

        <div className="field">
          <label>Skills</label>
          <div className="chip-row">
            {options.skills.map((skill) => (
              <button
                key={skill}
                className={`chip ${form.skills.includes(skill) ? "selected" : ""}`}
                onClick={() => toggleSkill(skill)}
              >
                {skill}
              </button>
            ))}
          </div>
        </div>

        <button className="predict-btn" disabled={loading} onClick={handlePredict}>
          {loading ? "Predicting…" : "Predict Salary"}
        </button>

        {error && <p className="error">{error}</p>}

        {prediction && (
          <div className="prediction-result">
            <div className="label" style={{ fontSize: 12, color: "#8b8fa3", textTransform: "uppercase" }}>
              Estimated Salary (INR/year)
            </div>
            <div className="value">{prediction.predicted_salary.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            <div className="range">
              Range: {prediction.range_low.toLocaleString(undefined, { maximumFractionDigits: 0 })} - {prediction.range_high.toLocaleString(undefined, { maximumFractionDigits: 0 })} (±10% around the point prediction)
            </div>
          </div>
        )}

        {prediction?.llm_available && prediction.llm_insight && (
          <div className="llm-panel">
            <h4>AI Career Insight <span className="ai-badge">Groq</span></h4>
            <p className="llm-summary">{prediction.llm_insight}</p>
          </div>
        )}
      </div>

      {comparison && (
        <div className="panel">
          <h3>Model Comparison</h3>
          <table>
            <thead>
              <tr><th>Model</th><th>MAE</th><th>RMSE</th><th>R²</th></tr>
            </thead>
            <tbody>
              {Object.entries(comparison.comparison).map(([name, metrics]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{metrics.MAE.toLocaleString()}</td>
                  <td>{metrics.RMSE.toLocaleString()}</td>
                  <td>{metrics.R2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
