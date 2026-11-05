
from backend.services.candidate_report import (
    generate_candidate_report,
    generate_candidate_report_text
)

from backend.models.schemas import (
    ResumeProfile,
    CandidateMatchResult,
    CandidateEvaluation,
    RankedCandidate
)


def create_sample_candidate():
    """Create a sample ranked candidate for testing."""

    profile = ResumeProfile(
        full_name="Sangeetha S",
        professional_summary="AI Engineer with experience in Python and Generative AI.",
        technical_skills=[
            "Python",
            "Machine Learning",
            "Generative AI",
            "FastAPI"
        ],
        soft_skills=[
            "Problem Solving",
            "Communication"
        ]
    )

    match_result = CandidateMatchResult(
        overall_match_score=85.5,
        keyword_match_score=80.0,
        semantic_match_score=89.0,
        required_skill_score=90.0,
        preferred_skill_score=75.0,
        experience_score=80.0,
        education_eligible=True,
        matched_skills=["Python", "Machine Learning"],
        missing_required_skills=["TensorFlow"],
        matched_preferred_skills=["FastAPI"],
        matching_evidence=[
            "Python -> Python",
            "Machine Learning -> Machine Learning"
        ],
        missing_requirements=["TensorFlow"],
        match_summary="Strong candidate match."
    )

    evaluation = CandidateEvaluation(
        candidate_id="sangeetha_s",
        profile=profile,
        match_result=match_result
    )

    return RankedCandidate(
        rank=1,
        candidate_id=evaluation.candidate_id,
        candidate_name=profile.full_name,
        overall_match_score=match_result.overall_match_score,
        profile=profile,
        match_result=match_result
    )


def test_generate_candidate_report():
    candidate = create_sample_candidate()

    report = generate_candidate_report(candidate)

    assert report["candidate_information"]["candidate_name"] == "Sangeetha S"
    assert report["candidate_information"]["rank"] == 1

    assert report["match_overview"]["overall_match_score"] == 85.5

    assert "Python" in report["skills_analysis"]["matched_required_skills"]
    assert "TensorFlow" in report["skills_analysis"]["missing_required_skills"]

    assert "FastAPI" in report["candidate_strengths"]["technical_skills"]

    assert report["final_assessment"] == "Strong candidate match."

    print("PASS: Structured candidate report generated correctly.")


def test_generate_candidate_report_text():
    candidate = create_sample_candidate()

    report_text = generate_candidate_report_text(candidate)

    assert "CANDIDATE EVALUATION REPORT" in report_text
    assert "Sangeetha S" in report_text
    assert "85.50%" in report_text
    assert "Python" in report_text
    assert "TensorFlow" in report_text
    assert "Strong candidate match." in report_text

    print("PASS: Readable candidate report generated correctly.")


def test_candidate_report_with_empty_sections():
    candidate = create_sample_candidate()

    candidate.profile.technical_skills = []
    candidate.profile.soft_skills = []
    candidate.match_result.matched_skills = []
    candidate.match_result.missing_required_skills = []
    candidate.match_result.matched_preferred_skills = []
    candidate.match_result.matching_evidence = []
    candidate.match_result.missing_requirements = []

    report = generate_candidate_report(candidate)
    report_text = generate_candidate_report_text(candidate)

    assert report["candidate_strengths"]["technical_skills"] == []
    assert report["skills_analysis"]["matched_required_skills"] == []
    assert isinstance(report_text, str)

    print("PASS: Empty report sections handled correctly.")


if __name__ == "__main__":
    test_generate_candidate_report()
    test_generate_candidate_report_text()
    test_candidate_report_with_empty_sections()

    print("\nAll candidate report tests passed!")
