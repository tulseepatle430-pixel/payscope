import { useEffect, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api } from "../api/client";

export default function SalaryIntelligence() {
  const [byRole, setByRole] = useState(null);
  const [byExperience, setByExperience] = useState(null);
  const [byLocation, setByLocation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.salaryByRole().then(setByRole).catch((e) => setError(e.message));
    api.salaryByExperience().then(setByExperience).catch((e) => setError(e.message));
    api.salaryByLocation().then(setByLocation).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;

  return (
    <div>
      <h2>Salary Intelligence</h2>

      <div className="panel">
        <h3>Salary by Role</h3>
        {byRole && (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={byRole}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262a38" />
              <XAxis dataKey="job_title" tick={{ fontSize: 11 }} angle={-25} textAnchor="end" height={70} stroke="#8b8fa3" />
              <YAxis stroke="#8b8fa3" />
              <Tooltip contentStyle={{ background: "#1e2230", border: "1px solid #262a38" }} />
              <Bar dataKey="median_salary" fill="#5b8def" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="panel">
        <h3>Salary by Experience</h3>
        {byExperience && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byExperience}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262a38" />
              <XAxis dataKey="experience_bucket" stroke="#8b8fa3" />
              <YAxis stroke="#8b8fa3" />
              <Tooltip contentStyle={{ background: "#1e2230", border: "1px solid #262a38" }} />
              <Bar dataKey="median_salary" fill="#2a9d8f" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="panel">
        <h3>Salary by Location</h3>
        {byLocation && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byLocation}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262a38" />
              <XAxis dataKey="location" stroke="#8b8fa3" />
              <YAxis stroke="#8b8fa3" />
              <Tooltip contentStyle={{ background: "#1e2230", border: "1px solid #262a38" }} />
              <Bar dataKey="median_salary" fill="#f4a261" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
