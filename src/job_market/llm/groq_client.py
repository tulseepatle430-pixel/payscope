"""Optional Groq LLM integration: turns a raw salary prediction into a short,
specific written career insight (what's driving the number, what would move it).

Entirely optional and additive — the prediction itself always comes from the
from-scratch NumPy models (see ml/), never the LLM. When GROQ_API_KEY isn't set
(or a call fails), this returns None and the API/UI simply omit the AI section.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


@lru_cache
def _client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    from groq import Groq

    return Groq(api_key=api_key)


def is_available() -> bool:
    return _client() is not None


def generate_career_insight(
    job_title: str,
    location: str,
    experience_years: float,
    education: str,
    skills: list[str],
    predicted_salary: float,
    top_demand_skills: list[str],
) -> str | None:
    """Ask Groq for a short, concrete take on this prediction and how to improve it.

    Returns None if Groq isn't configured or the call fails.
    """
    client = _client()
    if client is None:
        return None
    try:
        missing_in_demand = [s for s in top_demand_skills if s not in skills][:5]
        prompt = (
            f"A salary model predicted INR {predicted_salary:,.0f}/year for this profile:\n"
            f"Role: {job_title}\nLocation: {location}\nExperience: {experience_years} years\n"
            f"Education: {education}\nSkills: {', '.join(skills) or 'none listed'}\n\n"
            f"The most in-demand skills in this market right now: {', '.join(top_demand_skills)}\n"
            f"Of those, this profile is missing: {', '.join(missing_in_demand) or 'none — good coverage'}\n\n"
            "In 3-4 sentences: explain what's likely driving this salary estimate, and give "
            "one concrete, specific action that would most plausibly increase it. Be direct, "
            "not generic — reference the actual role/location/skills given."
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None
