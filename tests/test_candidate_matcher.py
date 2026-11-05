
from backend.services.resume_extractor import extract_resume_text
from backend.agents.resume_parser import parse_resume
from backend.agents.job_analyser import analyse_job_description
from backend.agents.candidate_matcher import match_candidate


def test_candidate_matcher():

    # 1. Extract resume text
    resume_path = "data/resumes/my_resume.pdf"

    resume_text = extract_resume_text(resume_path)

    # 2. Parse resume
    candidate_profile = parse_resume(resume_text)

    # 3. Read Job Description
    jd_path = "data/job_descriptions/vasiva_ai_intern.txt"

    with open(jd_path, "r", encoding="utf-8") as file:
        jd_text = file.read()

    # 4. Analyse Job Description
    job_profile = analyse_job_description(jd_text)

    # 5. Match candidate and job
    match_result = match_candidate(
        candidate=candidate_profile,
        job=job_profile
    )

    # 6. Display Candidate Matching Report
    print("\n========== CANDIDATE MATCHING REPORT ==========\n")

    print("Candidate:", candidate_profile.full_name)
    print("Job Role:", job_profile.job_title)

    print("\nOverall Match Score:",
          match_result.overall_match_score, "%")

    print("\nKeyword Match Score:",
          match_result.keyword_match_score)

    print("\nSemantic Match Score:",
          match_result.semantic_match_score)

    print("\nRequired Skills Score:",
          match_result.required_skill_score, "%")

    print("\nPreferred Skills Score:",
          match_result.preferred_skill_score, "%")

    print("\nExperience Score:",
          match_result.experience_score)

    print("\nEducation Eligible:",
          match_result.education_eligible)

    print("\nMatched Required Skills:")
    for skill in match_result.matched_skills:
        print("-", skill)

    print("\nMissing Required Skills:")
    for skill in match_result.missing_required_skills:
        print("-", skill)

    print("\nMatched Preferred Skills:")
    for skill in match_result.matched_preferred_skills:
        print("-", skill)

    print("\nMatching Evidence:")
    for evidence in match_result.matching_evidence:
        print("-", evidence)

    print("\nMissing Requirements:")
    for requirement in match_result.missing_requirements:
        print("-", requirement)

    print("\nMatch Summary:")
    print(match_result.match_summary)

    # 7. Display JSON output
    print("\n========== JSON OUTPUT ==========\n")

    print(match_result.model_dump_json(indent=4))


if __name__ == "__main__":
    test_candidate_matcher()
