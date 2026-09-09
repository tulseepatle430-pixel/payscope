import { useState } from "react";
import "./App.css";
import MarketOverview from "./pages/MarketOverview";
import SkillDemand from "./pages/SkillDemand";
import SalaryIntelligence from "./pages/SalaryIntelligence";
import SalaryPredictor from "./pages/SalaryPredictor";

const PAGES = {
  "Market Overview": MarketOverview,
  "Skill Demand": SkillDemand,
  "Salary Intelligence": SalaryIntelligence,
  "Salary Predictor": SalaryPredictor,
};

export default function App() {
  const [page, setPage] = useState("Market Overview");
  const Page = PAGES[page];

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Job Market Intelligence</h1>
        <nav>
          {Object.keys(PAGES).map((name) => (
            <button
              key={name}
              className={name === page ? "active" : ""}
              onClick={() => setPage(name)}
            >
              {name}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Page />
      </main>
    </div>
  );
}
