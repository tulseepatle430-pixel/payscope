"""Skill extraction from job descriptions: dictionary/synonym matching.

Maintains a standardized skill taxonomy so "py", "python programming" and
"python" all resolve to the same canonical skill, preventing the same skill
from fragmenting into unrelated features downstream.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from config.settings import SKILLS_TAXONOMY_PATH

_WHITESPACE_RE = re.compile(r"\s+")


@lru_cache
def _synonym_lookup(path: Path = SKILLS_TAXONOMY_PATH) -> dict[str, str]:
    raw = json.loads(Path(path).read_text())
    lookup: dict[str, str] = {}
    for canonical, synonyms in raw.items():
        lookup[canonical.lower()] = canonical
        for syn in synonyms:
            lookup[syn.strip().lower()] = canonical
    return lookup


@lru_cache
def all_skills(path: Path = SKILLS_TAXONOMY_PATH) -> list[str]:
    return sorted(json.loads(Path(path).read_text()).keys())


def extract_skills(text: str) -> set[str]:
    normalized = _WHITESPACE_RE.sub(" ", text.lower())
    padded = f" {normalized} "

    found: set[str] = set()
    for synonym, canonical in _synonym_lookup().items():
        pattern = r"(?<![a-z0-9])" + re.escape(synonym) + r"(?![a-z0-9])"
        if re.search(pattern, padded):
            found.add(canonical)
    return found
