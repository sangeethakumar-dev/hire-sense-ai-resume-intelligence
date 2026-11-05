
from pathlib import Path

from backend.models.schemas import (
    ResumeProfile,
    JobDescriptionProfile,
    CandidateEvaluation
)

from backend.agents.candidate_matcher import match_candidate

from backend.services.resume_processor import process_resume
from backend.services.jd_processor import process_job_description
from backend.services.candidate_ranking import rank_candidates
from backend.services.candidate_report import (
    generate_candidate_report,
    generate_candidate_report_text
)


def run_recruitment_pipeline(
    jd_file_path: str,
    resume_file_paths: list[str]
) -> dict:
    """
    Execute the complete recruitment workflow:

    JD Processing
    -> Resume Processing
    -> Candidate Matching
    -> Candidate Ranking
    -> Report Generation
    """

    if not resume_file_paths:
        raise ValueError("At least one resume must be provided.")

    # ----------------------------------------
    # 1. Process Job Description
    # ----------------------------------------

    jd_result = process_job_description(jd_file_path)

    job_profile = JobDescriptionProfile(
        **jd_result["job_profile"]
    )

    # ----------------------------------------
    # 2. Process Resumes
    # ----------------------------------------

    candidate_evaluations = []
    skipped_resumes = []
    processing_errors = []

    for resume_path in resume_file_paths:

        try:
            resume_result = process_resume(resume_path)

            if resume_result["status"] == "duplicate":
                skipped_resumes.append({
                    "file_name": Path(resume_path).name,
                    "reason": "Duplicate resume"
                })
                continue

            candidate_profile = ResumeProfile(
                **resume_result["candidate_profile"]
            )

            # ----------------------------------------
            # 3. Match Candidate Against JD
            # ----------------------------------------

            match_result = match_candidate(
                candidate=candidate_profile,
                job=job_profile
            )

            candidate_evaluation = CandidateEvaluation(
                candidate_id=resume_result["candidate_id"],
                profile=candidate_profile,
                match_result=match_result
            )

            candidate_evaluations.append(candidate_evaluation)

        except Exception as error:

            processing_errors.append({
                "file_name": Path(resume_path).name,
                "error": str(error)
            })

    # ----------------------------------------
    # 4. Rank Candidates
    # ----------------------------------------

    ranked_candidates = rank_candidates(
        candidate_evaluations
    )

    # ----------------------------------------
    # 5. Generate Candidate Reports
    # ----------------------------------------

    candidate_reports = []

    for candidate in ranked_candidates:

        report = generate_candidate_report(candidate)

        report_text = generate_candidate_report_text(candidate)

        candidate_reports.append({
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.candidate_name,
            "rank": candidate.rank,
            "report": report,
            "report_text": report_text
        })

    # ----------------------------------------
    # 6. Return Recruitment Results
    # ----------------------------------------

    return {
        "status": "success",
        "job_id": jd_result["job_id"],
        "job_title": jd_result["job_title"],
        "total_resumes_submitted": len(resume_file_paths),
        "total_candidates_evaluated": len(candidate_evaluations),
        "total_duplicates_skipped": len(skipped_resumes),
        "total_processing_errors": len(processing_errors),
        "ranked_candidates": [
            candidate.model_dump()
            for candidate in ranked_candidates
        ],
        "candidate_reports": candidate_reports,
        "skipped_resumes": skipped_resumes,
        "processing_errors": processing_errors
    }
