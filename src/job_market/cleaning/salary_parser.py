"""Normalize messy free-text salary strings into (min, max, midpoint, currency) in INR.

Real job postings mix formats: "₹8-12 LPA", "8 LPA", "$80,000", "Not disclosed",
"8-12 Lakhs". This is deliberately a small, explicit rule set rather than a
generic parser, because salary data is exactly the kind of messy real-world
field an interviewer expects you to have hit and reasoned about.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from config.settings import INR_PER_LAKH, USD_TO_INR

_DISCLOSED_NEGATIVE = {"not disclosed", "n/a", "na", "undisclosed", "confidential", "-", ""}

_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)")
_SINGLE_RE = re.compile(r"(\d+(?:\.\d+)?)")
_USD_RE = re.compile(r"\$")
_LPA_OR_LAKH_RE = re.compile(r"lpa|lakh", re.IGNORECASE)


@dataclass
class ParsedSalary:
    salary_min_inr: float | None
    salary_max_inr: float | None
    salary_midpoint_inr: float | None
    currency: str | None


def parse_salary(raw: str) -> ParsedSalary:
    if raw is None:
        return ParsedSalary(None, None, None, None)

    text = str(raw).strip()
    if text.lower() in _DISCLOSED_NEGATIVE:
        return ParsedSalary(None, None, None, None)

    cleaned = text.replace(",", "")
    is_usd = bool(_USD_RE.search(cleaned))
    is_lakh_scale = bool(_LPA_OR_LAKH_RE.search(cleaned))

    range_match = _RANGE_RE.search(cleaned)
    if range_match:
        low, high = float(range_match.group(1)), float(range_match.group(2))
    else:
        single_match = _SINGLE_RE.search(cleaned)
        if not single_match:
            return ParsedSalary(None, None, None, None)
        low = high = float(single_match.group(1))

    if is_usd:
        low_inr, high_inr, currency = low * USD_TO_INR, high * USD_TO_INR, "USD"
    elif is_lakh_scale:
        low_inr, high_inr, currency = low * INR_PER_LAKH, high * INR_PER_LAKH, "INR"
    else:
        # Bare numbers with no scale marker are assumed to already be annual INR.
        low_inr, high_inr, currency = low, high, "INR"

    return ParsedSalary(
        salary_min_inr=low_inr,
        salary_max_inr=high_inr,
        salary_midpoint_inr=(low_inr + high_inr) / 2,
        currency=currency,
    )
