from job_market.cleaning.salary_parser import parse_salary


def test_inr_range_with_symbol():
    result = parse_salary("₹8-12 LPA")
    assert result.salary_min_inr == 800_000
    assert result.salary_max_inr == 1_200_000
    assert result.salary_midpoint_inr == 1_000_000
    assert result.currency == "INR"


def test_single_lpa_value():
    result = parse_salary("8 LPA")
    assert result.salary_midpoint_inr == 800_000


def test_lakh_range():
    result = parse_salary("8-12 Lakhs")
    assert result.salary_midpoint_inr == 1_000_000


def test_usd_value_converted():
    result = parse_salary("$80,000")
    assert result.currency == "USD"
    assert result.salary_midpoint_inr == 80_000 * 83.0


def test_not_disclosed_returns_none():
    result = parse_salary("Not disclosed")
    assert result.salary_midpoint_inr is None


def test_none_input():
    result = parse_salary(None)
    assert result.salary_midpoint_inr is None
