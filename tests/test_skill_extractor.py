from job_market.nlp.skill_extractor import extract_skills


def test_extracts_synonyms_to_canonical():
    text = "Looking for a Data Analyst proficient in Python, SQL, Power BI and Tableau."
    skills = extract_skills(text)
    assert {"Python", "SQL", "Power BI", "Tableau"} <= skills


def test_abbreviation_resolves_to_canonical():
    skills = extract_skills("Strong ML and NLP background required")
    assert "Machine Learning" in skills
    assert "NLP" in skills


def test_no_false_positive_on_unrelated_text():
    assert extract_skills("The team enjoys hiking on weekends") == set()
