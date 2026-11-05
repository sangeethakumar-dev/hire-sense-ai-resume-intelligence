from pathlib import Path
import json
import os
import uuid

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Use a fresh database for every real pipeline test
os.environ["CHROMA_DB_PATH"] = str(
    PROJECT_ROOT / "data" / f"chroma_db_test_{uuid.uuid4().hex[:8]}"
)

# Import only AFTER setting the database path
from backend.services.recruitment_pipeline import (
    run_recruitment_pipeline
)

# CloudData Technologies AI/ML Developer job description
JD_PATH = PROJECT_ROOT / "data" / "job_descriptions" / "CloudData_Technologies_AIML_Developer.txt"

# Three real PDF resumes
RESUME_PATHS = [
    PROJECT_ROOT / "data" / "resumes" / "my_resume.pdf",
    PROJECT_ROOT / "data" / "resumes" / "mohamed_hasif_AI_Engineer.pdf",
    PROJECT_ROOT / "data" / "resumes" / "Selvasri_K_Resume.pdf"
]


def main():

    print("\n========== HIRESENSE AI ==========")
    print("REAL END-TO-END RECRUITMENT TEST")
    print("=================================\n")

    # Validate input files
    if not JD_PATH.exists():
        raise FileNotFoundError(f"JD not found: {JD_PATH}")

    for resume_path in RESUME_PATHS:
        if not resume_path.exists():
            raise FileNotFoundError(
                f"Resume not found: {resume_path}"
            )

    print(f"Job Description: {JD_PATH.name}")
    print(f"Total Resumes: {len(RESUME_PATHS)}")

    print("\nStarting real recruitment pipeline...")
    print("Gemini API and ChromaDB will be used.")
    print("This may take some time.\n")

    result = run_recruitment_pipeline(
        jd_file_path=str(JD_PATH),
        resume_file_paths=[
            str(path) for path in RESUME_PATHS
        ]
    )

    # Display summary
    print("\n========== PIPELINE SUMMARY ==========")

    print("Status:", result["status"])
    print("Job Title:", result["job_title"])
    print("Total Resumes:", result["total_resumes_submitted"])
    print("Candidates Evaluated:", result["total_candidates_evaluated"])
    print("Duplicates Skipped:", result["total_duplicates_skipped"])
    print("Processing Errors:", result["total_processing_errors"])

    # Display ranked candidates
    print("\n========== RANKED CANDIDATES ==========")

    for candidate in result["ranked_candidates"]:

        print(f"\nRank: {candidate['rank']}")
        print(f"Name: {candidate['candidate_name']}")
        print(
            f"Match Score: "
            f"{candidate['overall_match_score']:.2f}%"
        )

    # Display skipped resumes
    print("\n========== SKIPPED RESUMES ==========")

    for resume in result["skipped_resumes"]:
        print(resume)

    # Display processing errors
    print("\n========== PROCESSING ERRORS ==========")

    for error in result["processing_errors"]:
        print(error)

    # Save complete results
    output_path = (
        PROJECT_ROOT / "data" / "recruitment_test_results.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nResults saved to:", output_path)

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
