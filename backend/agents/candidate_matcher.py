from backend.models.schemas import(
    ResumeProfile,
    JobDescriptionProfile,
    CandidateMatchresult,
)

def normalize_skills(skills: list[str]) -> set[str]:
    return{
        skill.strip().lower() for skill in skills if skill.strip()
    }

def match_candidate(
        candidate: ResumeProfile,
        job : JobDescriptionProfile,
        ) -> CandidateMatchresult:
    """
    Compare Candidate Resume with Job description and calculate a matching score
    """

    #Extract Candidate SKills
    candidate_skills = normalize_skills(candidate.technical_skills)

    #Extract Job SKills 
    required_skills = normalize_skills(job.required_skills)

    preferred_skills = normalize_skills(job.preferred_skills)

    #Identify Matching Skills
    matched_required = candidate_skills.intersection(required_skills)

    missing_required = required_skills - candidate_skills

    matched_preffered = candidate_skills.intersection(preferred_skills)

    #Calculate required Skills Matching percentage

    if required_skills :
        skill_match_percentage = (len(matched_required)/len(required_skills))*100
    else:
        skill_match_percentage = 0.0

    #Calculate Overall matching score

    if required_skills or preferred_skills:
        total_job_skills = (len(required_skills) + len(preferred_skills))

        total_matched_skills = (len(matched_required) + len(matched_preffered))

        overall_match_score = (total_matched_skills /total_job_skills)*100

    else:
        overall_match_score = 0.0

    #Generete Matching Summary

    if overall_match_score >= 75:
        summary = "Strong Match Score"
    elif overall_match_score >= 50:
        summary = "Moderate SKill Match"
    else:
        summary = "Low Skill Match"

    #Return Structured Result

    return CandidateMatchresult(
        overall_match_score=round(overall_match_score,2),
        matched_skills=sorted(matched_required),
        missing_required_skills=sorted(missing_required),
        matched_preferred_skills=sorted(matched_preffered),
        skill_match_percentage= round(skill_match_percentage,2),
        match_summary=summary
    )
