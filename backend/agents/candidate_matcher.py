
import os
import re
from datetime import date

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.models.schemas import (
    ResumeProfile,
    JobDescriptionProfile,
    CandidateMatchResult
)

load_dotenv()


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

KEYWORD_WEIGHT = 0.40
SEMANTIC_WEIGHT = 0.60

EXPERIENCE_WEIGHT = 0.35
REQUIRED_SKILLS_WEIGHT = 0.35
PREFERRED_SKILLS_WEIGHT = 0.30

SEMANTIC_THRESHOLD = 0.70


# --------------------------------------------------
# 2. INITIALIZE EMBEDDING MODEL
# --------------------------------------------------

def get_embedding_model():

    api_key = os.getenv("GOOGLE_API_KEY")

    model_name = os.getenv(
        "GEMINI_EMBEDDING_MODEL",
        "gemini-embedding-001"
    )

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env")

    return GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=api_key
    )


# --------------------------------------------------
# 3. NORMALIZE TEXT
# --------------------------------------------------

def normalize_text(text: str) -> str:

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9+#. ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


# --------------------------------------------------
# 4. KEYWORD MATCHING
# --------------------------------------------------

def keyword_match(requirement: str, resume_text: str) -> float:

    requirement = normalize_text(requirement)
    resume_text = normalize_text(resume_text)

    if requirement and requirement in resume_text:
        return 1.0

    return 0.0


# --------------------------------------------------
# 5. SEMANTIC MATCHING
# --------------------------------------------------

def semantic_match(
    requirement: str,
    resume_text: str,
    embedding_model
) -> float:

    embeddings = embedding_model.embed_documents(
        [requirement, resume_text]
    )

    vector_a = embeddings[0]
    vector_b = embeddings[1]

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    similarity = dot_product / (magnitude_a * magnitude_b)

    return max(0.0, min(1.0, similarity))


# --------------------------------------------------
# 6. HYBRID MATCHING
# --------------------------------------------------

def hybrid_match(
    requirement: str,
    resume_text: str,
    embedding_model
) -> tuple[float, float, float]:

    keyword_score = keyword_match(
        requirement,
        resume_text
    )

    semantic_score = semantic_match(
        requirement,
        resume_text,
        embedding_model
    )

    hybrid_score = (
        KEYWORD_WEIGHT * keyword_score
        + SEMANTIC_WEIGHT * semantic_score
    )

    return (
        round(hybrid_score, 4),
        keyword_score,
        semantic_score
    )


# --------------------------------------------------
# 7. SKILL MATCHING
# --------------------------------------------------

def evaluate_skills(
    job_skills: list[str],
    resume_evidence: list[str],
    embedding_model
):

    matched_skills = []
    missing_skills = []
    matching_evidence = []

    hybrid_scores = []
    keyword_scores = []
    semantic_scores = []

    for skill in job_skills:

        evidence_scores = []

        for evidence in resume_evidence:

            hybrid, keyword, semantic = hybrid_match(
                skill,
                evidence,
                embedding_model
            )

            evidence_scores.append(
                (hybrid, keyword, semantic, evidence)
            )

        if not evidence_scores:
            missing_skills.append(skill)
            hybrid_scores.append(0.0)
            keyword_scores.append(0.0)
            semantic_scores.append(0.0)
            continue

        best_match = max(
            evidence_scores,
            key=lambda result: result[0]
        )

        hybrid, keyword, semantic, evidence = best_match

        hybrid_scores.append(hybrid)
        keyword_scores.append(keyword)
        semantic_scores.append(semantic)

        if hybrid >= SEMANTIC_THRESHOLD:

            matched_skills.append(skill)

            matching_evidence.append(
                f"{skill} -> {evidence}"
            )

        else:
            missing_skills.append(skill)

    def average(values):
        return (
            sum(values) / len(values) * 100
            if values else 0.0
        )

    return {
        "match_score": round(average(hybrid_scores), 2),
        "keyword_score": round(average(keyword_scores), 2),
        "semantic_score": round(average(semantic_scores), 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matching_evidence": matching_evidence
    }


# --------------------------------------------------
# 8. EXPERIENCE MATCHING
# --------------------------------------------------

def evaluate_experience(
    candidate: ResumeProfile,
    job: JobDescriptionProfile,
    embedding_model
) -> float | None:

    if not job.minimum_experience:
        return None

    # Collect employment evidence separately.
    # This preliminary version does not count projects as employment.

    candidate_experience = []

    for experience in candidate.work_experience:

        details = " ".join(filter(None, [
            experience.job_title,
            experience.company,
            " ".join(experience.description)
        ]))

        if details:
            candidate_experience.append(details)

    if not candidate_experience:
        return 0.0

    # Compare the JD requirement with individual work entries.
    scores = []

    for experience in candidate_experience:

        score = semantic_match(
            job.minimum_experience,
            experience,
            embedding_model
        )

        scores.append(score)

    return round(max(scores) * 100, 2)


# --------------------------------------------------
# 9. EDUCATION ELIGIBILITY
# --------------------------------------------------

def evaluate_education(
    candidate: ResumeProfile,
    job: JobDescriptionProfile,
    embedding_model
) -> bool | None:

    if not job.education:
        return None

    candidate_education = []

    for education in candidate.education:

        details = " ".join(filter(None, [
            education.degree,
            education.field_of_study,
            education.institution
        ]))

        if details:
            candidate_education.append(details)

    if not candidate_education:
        return None

    for requirement in job.education:

        for qualification in candidate_education:

            score = semantic_match(
                requirement,
                qualification,
                embedding_model
            )

            if score >= SEMANTIC_THRESHOLD:
                return True

    return False


# --------------------------------------------------
# 10. MAIN CANDIDATE MATCHING FUNCTION
# --------------------------------------------------

def match_candidate(
    candidate: ResumeProfile,
    job: JobDescriptionProfile
) -> CandidateMatchResult:

    embedding_model = get_embedding_model()

    # Build separate resume evidence entries.

    resume_evidence = []

    if candidate.professional_summary:
        resume_evidence.append(
            candidate.professional_summary
        )

    resume_evidence.extend(candidate.technical_skills)
    resume_evidence.extend(candidate.soft_skills)

    for experience in candidate.work_experience:

        if experience.job_title:
            resume_evidence.append(experience.job_title)

        resume_evidence.extend(experience.description)

    for project in candidate.projects:

        if project.project_name:
            resume_evidence.append(project.project_name)

        resume_evidence.extend(project.description)
        resume_evidence.extend(project.technologies)

    # Required skills

    required_result = evaluate_skills(
        job.required_skills,
        resume_evidence,
        embedding_model
    )

    # Preferred skills

    preferred_result = evaluate_skills(
        job.preferred_skills,
        resume_evidence,
        embedding_model
    )

    # Experience

    experience_score = evaluate_experience(
        candidate,
        job,
        embedding_model
    )

    # Education

    education_eligible = evaluate_education(
        candidate,
        job,
        embedding_model
    )

    # Aggregate keyword and semantic scores
    all_skill_results = [
        result
        for result in [required_result, preferred_result]
        if result["matched_skills"] or result["missing_skills"]
    ]

    keyword_match_score = (
        sum(result["keyword_score"] for result in all_skill_results)
        / len(all_skill_results)
        if all_skill_results else 0.0
    )

    semantic_match_score = (
        sum(result["semantic_score"] for result in all_skill_results)
        / len(all_skill_results)
        if all_skill_results else 0.0
    )

    # Weighted scoring

    active_weights = []

    if experience_score is not None:
        active_weights.append(
            (EXPERIENCE_WEIGHT, experience_score)
        )

    if job.required_skills:
        active_weights.append(
            (
                REQUIRED_SKILLS_WEIGHT,
                required_result["match_score"]
            )
        )

    if job.preferred_skills:
        active_weights.append(
            (
                PREFERRED_SKILLS_WEIGHT,
                preferred_result["match_score"]
            )
        )

    total_weight = sum(
        weight for weight, score in active_weights
    )

    if total_weight:

        overall_match_score = sum(
            weight * score
            for weight, score in active_weights
        ) / total_weight

    else:
        overall_match_score = 0.0

    # Summary

    if overall_match_score >= 75:
        summary = "Strong candidate match."

    elif overall_match_score >= 50:
        summary = "Moderate candidate match."

    else:
        summary = "Low candidate match."

    if education_eligible is False:
        summary += " Education requirement not verified."

    # Return structured result

    return CandidateMatchResult(

        overall_match_score=round(overall_match_score, 2),

        keyword_match_score=round(keyword_match_score, 2),

        semantic_match_score=round(semantic_match_score, 2),

        required_skill_score=required_result["match_score"],

        preferred_skill_score=preferred_result["match_score"],

        experience_score=experience_score,

        education_eligible=education_eligible,

        matched_skills=required_result["matched_skills"],

        missing_required_skills=required_result["missing_skills"],

        matched_preferred_skills=preferred_result["matched_skills"],

        matching_evidence=(
            required_result["matching_evidence"]
            + preferred_result["matching_evidence"]
        ),

        missing_requirements=(
            required_result["missing_skills"]
            + preferred_result["missing_skills"]
        ),

        match_summary=summary
    )
