
from backend.models.schemas import RankedCandidate


def generate_candidate_report(candidate: RankedCandidate) -> dict:
    """
    Generate a structured recruiter-friendly report
    for an individual ranked candidate.
    """

    profile = candidate.profile
    result = candidate.match_result

    report = {
        "candidate_information": {
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.candidate_name,
            "job_title": None,
            "rank": candidate.rank,
        },

        "match_overview": {
            "overall_match_score": result.overall_match_score,
            "keyword_match_score": result.keyword_match_score,
            "semantic_match_score": result.semantic_match_score,
            "required_skill_score": result.required_skill_score,
            "preferred_skill_score": result.preferred_skill_score,
            "experience_score": result.experience_score,
            "education_eligible": result.education_eligible,
        },

        "skills_analysis": {
            "matched_required_skills": result.matched_skills,
            "missing_required_skills": result.missing_required_skills,
            "matched_preferred_skills": result.matched_preferred_skills,
        },

        "candidate_strengths": {
            "technical_skills": profile.technical_skills,
            "soft_skills": profile.soft_skills,
            "matching_evidence": result.matching_evidence,
        },

        "requirement_gaps": result.missing_requirements,

        "professional_background": {
            "professional_summary": profile.professional_summary,
            "work_experience": [
                experience.model_dump()
                for experience in profile.work_experience
            ],
            "education": [
                education.model_dump()
                for education in profile.education
            ],
            "projects": [
                project.model_dump()
                for project in profile.projects
            ],
        },

        "final_assessment": result.match_summary,
    }

    return report


def generate_candidate_report_text(candidate: RankedCandidate) -> str:
    """
    Generate a readable text report for recruiters.
    """

    report = generate_candidate_report(candidate)

    information = report["candidate_information"]
    overview = report["match_overview"]
    skills = report["skills_analysis"]
    strengths = report["candidate_strengths"]

    lines = [
        "========== CANDIDATE EVALUATION REPORT ==========",
        "",
        f"Candidate: {information['candidate_name'] or 'Not available'}",
        f"Rank: {information['rank']}",
        f"Overall Match Score: {overview['overall_match_score']:.2f}%",
        "",
        "MATCH OVERVIEW",
        f"Keyword Match: {overview['keyword_match_score']:.2f}%",
        f"Semantic Match: {overview['semantic_match_score']:.2f}%",
        f"Required Skills: {overview['required_skill_score']:.2f}%",
        f"Preferred Skills: {overview['preferred_skill_score']:.2f}%",
        f"Experience Score: {overview['experience_score']}",
        f"Education Eligible: {overview['education_eligible']}",
        "",
        "MATCHED REQUIRED SKILLS",
    ]

    lines.extend(
        f"- {skill}" for skill in skills["matched_required_skills"]
    )

    lines.extend(["", "MISSING REQUIRED SKILLS"])

    lines.extend(
        f"- {skill}" for skill in skills["missing_required_skills"]
    )

    lines.extend(["", "MATCHED PREFERRED SKILLS"])

    lines.extend(
        f"- {skill}" for skill in skills["matched_preferred_skills"]
    )

    lines.extend(["", "CANDIDATE TECHNICAL SKILLS"])

    lines.extend(
        f"- {skill}" for skill in strengths["technical_skills"]
    )

    lines.extend(["", "MATCHING EVIDENCE"])

    lines.extend(
        f"- {evidence}" for evidence in strengths["matching_evidence"]
    )

    lines.extend([
        "",
        "MISSING REQUIREMENTS",
    ])

    lines.extend(
        f"- {requirement}"
        for requirement in report["requirement_gaps"]
    )

    lines.extend([
        "",
        "FINAL ASSESSMENT",
        report["final_assessment"],
        "",
        "=================================================",
    ])

    return "\n".join(lines)
