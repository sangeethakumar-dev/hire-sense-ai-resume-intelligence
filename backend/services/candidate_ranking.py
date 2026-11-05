
from backend.models.schemas import CandidateEvaluation, RankedCandidate


def rank_candidates(
    candidates: list[CandidateEvaluation]
) -> list[RankedCandidate]:
    """
    Rank candidates based on their overall match scores.

    Candidates with higher scores receive better ranks.
    Candidates with equal scores receive the same rank.
    """

    if not candidates:
        return []

    # Sort candidates by overall match score (highest first)
    sorted_candidates = sorted(
        candidates,
        key=lambda candidate: candidate.match_result.overall_match_score,
        reverse=True
    )

    ranked_candidates = []

    previous_score = None
    current_rank = 0

    for index, candidate in enumerate(sorted_candidates, start=1):

        score = candidate.match_result.overall_match_score

        # Assign the same rank to candidates with equal scores
        if previous_score is None or score != previous_score:
            current_rank = index

        ranked_candidate = RankedCandidate(
            rank=current_rank,
            candidate_id=candidate.candidate_id,
            candidate_name=candidate.profile.full_name,
            overall_match_score=score,
            profile=candidate.profile,
            match_result=candidate.match_result
        )

        ranked_candidates.append(ranked_candidate)
        previous_score = score

    return ranked_candidates
