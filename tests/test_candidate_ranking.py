
from backend.services.candidate_ranking import rank_candidates
from backend.models.schemas import (
    ResumeProfile,
    CandidateMatchResult,
    CandidateEvaluation
)


def create_candidate(name, score):
    """Create a sample candidate with a matching result."""

    profile = ResumeProfile(
        full_name=name,
        technical_skills=["Python", "Machine Learning"]
    )

    match_result = CandidateMatchResult(
        overall_match_score=score,
        keyword_match_score=score,
        semantic_match_score=score,
        required_skill_score=score,
        preferred_skill_score=0.0,
        experience_score=None,
        education_eligible=None,
        matched_skills=["Python"],
        missing_required_skills=["TensorFlow"],
        matched_preferred_skills=[],
        matching_evidence=["Python -> Python"],
        missing_requirements=["TensorFlow"],
        match_summary="Candidate evaluation completed."
    )

    return CandidateEvaluation(
        candidate_id=name.lower().replace(" ", "_"),
        profile=profile,
        match_result=match_result
    )


def test_candidates_are_ranked_correctly():
    candidates = [
        create_candidate("Candidate A", 75.0),
        create_candidate("Candidate B", 92.5),
        create_candidate("Candidate C", 81.0)
    ]

    ranked = rank_candidates(candidates)

    assert len(ranked) == 3
    assert ranked[0].candidate_name == "Candidate B"
    assert ranked[0].rank == 1
    assert ranked[1].candidate_name == "Candidate C"
    assert ranked[1].rank == 2
    assert ranked[2].candidate_name == "Candidate A"
    assert ranked[2].rank == 3

    print("PASS: Candidates ranked by score.")


def test_equal_scores_receive_same_rank():
    candidates = [
        create_candidate("Candidate A", 90.0),
        create_candidate("Candidate B", 90.0),
        create_candidate("Candidate C", 80.0)
    ]

    ranked = rank_candidates(candidates)

    assert ranked[0].rank == 1
    assert ranked[1].rank == 1
    assert ranked[2].rank == 3

    print("PASS: Equal scores receive the same rank.")


def test_empty_candidate_list():
    ranked = rank_candidates([])

    assert ranked == []

    print("PASS: Empty candidate list handled correctly.")


def test_single_candidate():
    candidates = [
        create_candidate("Candidate A", 88.0)
    ]

    ranked = rank_candidates(candidates)

    assert len(ranked) == 1
    assert ranked[0].rank == 1
    assert ranked[0].overall_match_score == 88.0

    print("PASS: Single candidate ranked correctly.")


def test_candidate_details_are_preserved():
    candidates = [
        create_candidate("Candidate A", 85.0)
    ]

    ranked = rank_candidates(candidates)

    assert ranked[0].candidate_id == "candidate_a"
    assert ranked[0].profile.full_name == "Candidate A"
    assert ranked[0].match_result.matched_skills == ["Python"]

    print("PASS: Candidate details preserved.")


if __name__ == "__main__":
    test_candidates_are_ranked_correctly()
    test_equal_scores_receive_same_rank()
    test_empty_candidate_list()
    test_single_candidate()
    test_candidate_details_are_preserved()

    print("\nAll candidate ranking tests passed!")
