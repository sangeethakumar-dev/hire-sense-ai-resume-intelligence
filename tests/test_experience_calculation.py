from datetime import datetime
from types import SimpleNamespace

from backend.agents.candidate_matcher import calculate_experience_years


def create_candidate(experiences):
    return SimpleNamespace(work_experience=[
        SimpleNamespace(
            start_date=start,
            end_date=end
        )
        for start, end in experiences
    ])


def test_single_job():
    candidate = create_candidate([
        ("Jan 2025", "Dec 2025")
    ])

    assert calculate_experience_years(candidate) == 0.92


def test_overlapping_jobs():
    candidate = create_candidate([
        ("Jan 2025", "Dec 2025"),
        ("Jun 2025", "Dec 2025")
    ])

    assert calculate_experience_years(candidate) == 0.92


def test_non_overlapping_jobs():
    candidate = create_candidate([
        ("Jan 2025", "Jun 2025"),
        ("Jul 2025", "Dec 2025")
    ])

    assert calculate_experience_years(candidate) == 0.83


def test_missing_dates():
    candidate = create_candidate([
        (None, "Dec 2025"),
        ("Jan 2025", None)
    ])

    assert calculate_experience_years(candidate) == 0.0

def test_current_employment():
    candidate = create_candidate([
        ("Jan 2025", "Present")
    ])

    result = calculate_experience_years(candidate)

    print("Current employment experience:", result)

    assert result > 0.0


if __name__ == "__main__":
    test_single_job()
    test_overlapping_jobs()
    test_non_overlapping_jobs()
    test_missing_dates()
    test_current_employment()

    print("All experience calculation tests passed!")