import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api } from "../api/client";

function toHistogramBins(values, nBins = 40) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const width = (max - min) / nBins || 1;
  const bins = Array.from({ length: nBins }, (_, i) => ({
    bucket: Math.round(min + i * width),
    count: 0,
  }));
  for (const v of values) {
    let idx = Math.floor((v - min) / width);
    if (idx >= nBins) idx = nBins - 1;
    if (idx < 0) idx = 0;
    bins[idx].count += 1;
  }
  return bins;
}

export default function MarketOverview() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.overview().then(setOverview).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!overview) return <p>Loading…</p>;

  const histogram = toHistogramBins(overview.salary_histogram);

  return (
    <div>
      <h2>Job Market Intelligence & Salary Prediction</h2>

      <div className="kpi-row">
        <div className="kpi-card">
          <div className="label">Total Jobs</div>
          <div className="value">{overview.total_jobs.toLocaleString()}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Median Salary (INR/yr)</div>
          <div className="value">{overview.median_salary.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Top Location</div>
          <div className="value">{overview.top_location}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Top Role</div>
          <div className="value">{overview.top_role}</div>
        </div>
      </div>

      <div className="panel">
        <h3>Salary Distribution</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={histogram}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262a38" />
            <XAxis dataKey="bucket" tick={{ fontSize: 10 }} stroke="#8b8fa3" />
            <YAxis stroke="#8b8fa3" />
            <Tooltip contentStyle={{ background: "#1e2230", border: "1px solid #262a38" }} />
            <Bar dataKey="count" fill="#5b8def" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
