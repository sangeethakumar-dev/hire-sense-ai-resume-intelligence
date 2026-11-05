
from unittest.mock import patch

from backend.services.recruitment_pipeline import (
    run_recruitment_pipeline
)


def create_resume_result(candidate_id, candidate_name):
    return {
        "status": "success",
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "file_name": f"{candidate_name}.pdf",
        "candidate_profile": {
            "full_name": candidate_name,
            "technical_skills": ["Python", "Machine Learning"],
            "soft_skills": ["Problem Solving"],
            "education": [],
            "work_experience": [],
            "projects": [],
            "Certifications": []
        }
    }


def create_match_result(score):
    return {
        "overall_match_score": score,
        "keyword_match_score": score,
        "semantic_match_score": score,
        "required_skill_score": score,
        "preferred_skill_score": 0.0,
        "experience_score": None,
        "education_eligible": None,
        "matched_skills": ["Python"],
        "missing_required_skills": [],
        "matched_preferred_skills": [],
        "matching_evidence": ["Python -> Python"],
        "missing_requirements": [],
        "match_summary": "Strong candidate match."
    }


@patch("backend.services.recruitment_pipeline.generate_candidate_report_text")
@patch("backend.services.recruitment_pipeline.generate_candidate_report")
@patch("backend.services.recruitment_pipeline.match_candidate")
@patch("backend.services.recruitment_pipeline.process_resume")
@patch("backend.services.recruitment_pipeline.process_job_description")
def test_successful_recruitment_pipeline(
    mock_jd_processor,
    mock_resume_processor,
    mock_match_candidate,
    mock_generate_report,
    mock_generate_report_text
):

    mock_jd_processor.return_value = {
        "status": "success",
        "job_id": "JOB_001",
        "job_title": "AI Engineer",
        "job_profile": {
            "job_title": "AI Engineer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "minimum_experience": None,
            "education": [],
            "responsibilities": []
        }
    }

    mock_resume_processor.side_effect = [
        create_resume_result("CAND_001", "Candidate A"),
        create_resume_result("CAND_002", "Candidate B")
    ]

    mock_match_candidate.side_effect = [
        create_match_result(75.0),
        create_match_result(90.0)
    ]

    mock_generate_report.return_value = {
        "candidate_information": {}
    }

    mock_generate_report_text.return_value = (
        "Candidate evaluation report"
    )

    result = run_recruitment_pipeline(
        jd_file_path="sample_jd.txt",
        resume_file_paths=[
            "candidate_a.pdf",
            "candidate_b.pdf"
        ]
    )

    assert result["status"] == "success"
    assert result["job_id"] == "JOB_001"
    assert result["total_resumes_submitted"] == 2
    assert result["total_candidates_evaluated"] == 2

    assert result["ranked_candidates"][0]["candidate_name"] == "Candidate B"
    assert result["ranked_candidates"][0]["rank"] == 1

    assert result["ranked_candidates"][1]["candidate_name"] == "Candidate A"
    assert result["ranked_candidates"][1]["rank"] == 2

    assert len(result["candidate_reports"]) == 2

    mock_jd_processor.assert_called_once()
    assert mock_resume_processor.call_count == 2
    assert mock_match_candidate.call_count == 2

    print("PASS: Complete recruitment pipeline executed successfully.")


@patch("backend.services.recruitment_pipeline.generate_candidate_report_text")
@patch("backend.services.recruitment_pipeline.generate_candidate_report")
@patch("backend.services.recruitment_pipeline.match_candidate")
@patch("backend.services.recruitment_pipeline.process_resume")
@patch("backend.services.recruitment_pipeline.process_job_description")
def test_duplicate_resume_is_skipped(
    mock_jd_processor,
    mock_resume_processor,
    mock_match_candidate,
    mock_generate_report,
    mock_generate_report_text
):

    mock_jd_processor.return_value = {
        "status": "success",
        "job_id": "JOB_002",
        "job_title": "AI Intern",
        "job_profile": {
            "job_title": "AI Intern",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "minimum_experience": None,
            "education": [],
            "responsibilities": []
        }
    }

    mock_resume_processor.return_value = {
        "status": "duplicate",
        "message": "This resume has already been uploaded.",
        "file_name": "duplicate.pdf"
    }

    result = run_recruitment_pipeline(
        jd_file_path="sample_jd.txt",
        resume_file_paths=["duplicate.pdf"]
    )

    assert result["total_candidates_evaluated"] == 0
    assert result["total_duplicates_skipped"] == 1
    assert len(result["skipped_resumes"]) == 1
    assert result["ranked_candidates"] == []
    assert result["candidate_reports"] == []

    mock_match_candidate.assert_not_called()
    mock_generate_report.assert_not_called()
    mock_generate_report_text.assert_not_called()

    print("PASS: Duplicate resumes are skipped correctly.")


@patch("backend.services.recruitment_pipeline.generate_candidate_report_text")
@patch("backend.services.recruitment_pipeline.generate_candidate_report")
@patch("backend.services.recruitment_pipeline.match_candidate")
@patch("backend.services.recruitment_pipeline.process_resume")
@patch("backend.services.recruitment_pipeline.process_job_description")
def test_resume_processing_error_does_not_stop_pipeline(
    mock_jd_processor,
    mock_resume_processor,
    mock_match_candidate,
    mock_generate_report,
    mock_generate_report_text
):

    mock_jd_processor.return_value = {
        "status": "success",
        "job_id": "JOB_003",
        "job_title": "AI Engineer",
        "job_profile": {
            "job_title": "AI Engineer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "minimum_experience": None,
            "education": [],
            "responsibilities": []
        }
    }

    mock_resume_processor.side_effect = [
        RuntimeError("Resume parsing failed"),
        create_resume_result("CAND_003", "Candidate C")
    ]

    mock_match_candidate.return_value = create_match_result(85.0)

    mock_generate_report.return_value = {}
    mock_generate_report_text.return_value = "Sample report"

    result = run_recruitment_pipeline(
        jd_file_path="sample_jd.txt",
        resume_file_paths=[
            "failed_resume.pdf",
            "valid_resume.pdf"
        ]
    )

    assert result["total_resumes_submitted"] == 2
    assert result["total_candidates_evaluated"] == 1
    assert result["total_processing_errors"] == 1

    assert result["processing_errors"][0]["file_name"] == "failed_resume.pdf"

    assert result["ranked_candidates"][0]["candidate_name"] == "Candidate C"

    print("PASS: Pipeline continues after an individual resume processing error.")


def test_empty_resume_list():

    try:
        run_recruitment_pipeline(
            jd_file_path="sample_jd.txt",
            resume_file_paths=[]
        )

    except ValueError as error:
        assert str(error) == "At least one resume must be provided."
        print("PASS: Empty resume list handled correctly.")

    else:
        raise AssertionError("Expected ValueError was not raised.")


if __name__ == "__main__":

    test_successful_recruitment_pipeline()
    test_duplicate_resume_is_skipped()
    test_resume_processing_error_does_not_stop_pipeline()
    test_empty_resume_list()

    print("\nAll recruitment pipeline tests passed!")
