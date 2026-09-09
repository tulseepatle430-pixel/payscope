import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api } from "../api/client";

export default function SkillDemand() {
  const [demand, setDemand] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.skillDemand().then(setDemand).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!demand) return <p>Loading…</p>;

  return (
    <div>
      <h2>Skill Demand</h2>

      <div className="panel">
        <h3>Most In-Demand Skills</h3>
        <ResponsiveContainer width="100%" height={420}>
          <BarChart data={demand.slice(0, 20)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262a38" />
            <XAxis dataKey="skill" tick={{ fontSize: 11 }} angle={-40} textAnchor="end" height={90} stroke="#8b8fa3" />
            <YAxis stroke="#8b8fa3" />
            <Tooltip contentStyle={{ background: "#1e2230", border: "1px solid #262a38" }} />
            <Bar dataKey="job_count" fill="#5b8def" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="panel">
        <h3>All Skills</h3>
        <table>
          <thead><tr><th>Skill</th><th>Job Count</th></tr></thead>
          <tbody>
            {demand.map((row) => (
              <tr key={row.skill}><td>{row.skill}</td><td>{row.job_count}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
