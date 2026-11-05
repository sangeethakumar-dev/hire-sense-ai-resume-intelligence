
import re
from datetime import date, datetime

from backend.models.schemas import (
    ResumeProfile,
    JobDescriptionProfile,
    CandidateMatchResult
)
from backend.services.embedding_service import generate_embeddings


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
# 2. TEXT UTILITIES
# --------------------------------------------------

def normalize_text(text: str) -> str:

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9+#. ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text

def normalize_skill(skill: str) -> str:

    skill = normalize_text(skill)

    skill_aliases = {
        "html": "html5",
        "html 5": "html5",
        "css": "css3",
        "css 3": "css3",
        "scikit learn": "scikit-learn",
        "scikit learn library": "scikit-learn",
    }

    return skill_aliases.get(skill, skill)



def as_text(value) -> str:
    """Convert optional strings or lists into safe text."""

    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(str(item) for item in value if item)

    return str(value)


def cosine_similarity(vector_a, vector_b) -> float:

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return max(
        0.0,
        min(1.0, dot_product / (magnitude_a * magnitude_b))
    )


# --------------------------------------------------
# 3. RESUME EVIDENCE EXTRACTION
# --------------------------------------------------

def build_resume_evidence(candidate: ResumeProfile) -> list[str]:

    evidence = []

    if candidate.professional_summary:
        evidence.append(candidate.professional_summary)

    evidence.extend(candidate.technical_skills)
    evidence.extend(candidate.soft_skills)

    for experience in candidate.work_experience:

        details = " ".join(filter(None, [
            experience.job_title,
            experience.company,
            as_text(experience.description)
        ]))

        if details:
            evidence.append(details)

    for project in candidate.projects:

        details = " ".join(filter(None, [
            project.project_name,
            as_text(project.description),
            as_text(project.technologies)
        ]))

        if details:
            evidence.append(details)

    return list(dict.fromkeys(
        item.strip() for item in evidence if item and item.strip()
    ))


# --------------------------------------------------
# 4. KEYWORD MATCHING
# --------------------------------------------------

def keyword_match(requirement: str, evidence: str) -> float:

    requirement = normalize_skill(requirement)
    evidence = normalize_text(evidence)

    if not requirement or not evidence:
        return 0.0

    # Normalize individual evidence terms
    evidence_skills = [
        normalize_skill(item.strip())
        for item in re.split(r"[,;\n|]", evidence)
    ]

    # Exact skill match
    if requirement in evidence_skills:
        return 1.0

    # Whole-word / phrase matching
    pattern = rf"(?<![a-z0-9+#.]){re.escape(requirement)}(?![a-z0-9+#.])"

    if re.search(pattern, evidence):
        return 1.0

    # Partial word overlap
    requirement_words = set(requirement.split())
    evidence_words = set(evidence.split())

    matched_words = requirement_words.intersection(evidence_words)

    return len(matched_words) / len(requirement_words)

# --------------------------------------------------
# 5. HYBRID SKILL MATCHING
# --------------------------------------------------

def evaluate_skills(
    job_skills: list[str],
    resume_evidence: list[str],
    evidence_embeddings: list[list[float]],
    skill_embeddings: list[list[float]]
) -> dict:

    matched_skills = []
    missing_skills = []
    matching_evidence = []

    hybrid_scores = []
    keyword_scores = []
    semantic_scores = []

    for index, skill in enumerate(job_skills):

        best_result = None

        for evidence_index, evidence in enumerate(resume_evidence):

            keyword_score = keyword_match(skill, evidence)

            semantic_score = cosine_similarity(
                skill_embeddings[index],
                evidence_embeddings[evidence_index]
            )

            hybrid_score = (
                KEYWORD_WEIGHT * keyword_score
                + SEMANTIC_WEIGHT * semantic_score
            )

            result = (
                hybrid_score,
                keyword_score,
                semantic_score,
                evidence
            )

            if best_result is None or result[0] > best_result[0]:
                best_result = result

        if best_result is None:
            hybrid_scores.append(0.0)
            keyword_scores.append(0.0)
            semantic_scores.append(0.0)
            missing_skills.append(skill)
            continue

        hybrid, keyword, semantic, evidence = best_result

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
# 6. EXPERIENCE MATCHING
# --------------------------------------------------

def parse_date(value: str | None):

    if not value:
        return None

    value = value.strip().lower()

    if value in {"present", "current", "now"}:
        return date.today()

    formats = [
        "%m/%Y",
        "%Y-%m",
        "%Y",
        "%b %Y",
        "%B %Y"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(value, fmt).date()

        except ValueError:
            continue

    return None


def calculate_experience_years(candidate: ResumeProfile) -> float:

    date_ranges = []

    for experience in candidate.work_experience:

        start = parse_date(experience.start_date)
        end = parse_date(experience.end_date)

        if not start or not end:
            continue

        # Convert date objects to datetime for consistent comparisons
        if isinstance(start, date) and not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time())

        if isinstance(end, date) and not isinstance(end, datetime):
            end = datetime.combine(end, datetime.min.time())


        if end < start:
            continue

        date_ranges.append((start, end))

    if not date_ranges:
        return 0.0

    # Sort employment periods by start date
    date_ranges.sort(key=lambda x: x[0])

    # Merge overlapping periods
    merged_ranges = []

    current_start, current_end = date_ranges[0]

    for start, end in date_ranges[1:]:

        if start <= current_end:
            current_end = max(current_end, end)

        else:
            merged_ranges.append((current_start, current_end))
            current_start, current_end = start, end

    merged_ranges.append((current_start, current_end))

    # Calculate total months without double-counting
    total_months = 0

    for start, end in merged_ranges:

        months = (
            (end.year - start.year) * 12
            + end.month - start.month
        )

        total_months += max(0, months)

    return round(total_months / 12, 2)

def evaluate_experience(
    candidate: ResumeProfile,
    job: JobDescriptionProfile
) -> float | None:

    if not job.minimum_experience:
        return None

    experience_requirement = job.minimum_experience.lower().strip()

    # Handle fresher / entry-level requirements
    fresher_terms = [
        "fresher",
        "freshers",
        "entry level",
        "entry-level",
        "no experience",
        "0 years",
        "0 year"
    ]

    if any(term in experience_requirement for term in fresher_terms):
        return 100.0

    # Extract numeric experience requirement
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        experience_requirement
    )

    if not match:
        return None

    required_years = float(match.group(1))

    if required_years <= 0:
        return 100.0

    actual_years = calculate_experience_years(candidate)

    return round(
        min(actual_years / required_years, 1.0) * 100,
        2
    )


# --------------------------------------------------
# 7. EDUCATION ELIGIBILITY
# --------------------------------------------------


def normalize_education_text(value: str | None) -> str:
    """Normalize education text for deterministic comparison."""

    if not value:
        return ""

    return re.sub(
        r"[^a-z0-9 ]",
        " ",
        value.lower()
    ).strip()


def extract_graduation_year(value: str | None) -> int | None:
    """Extract a four-digit graduation year."""

    if not value:
        return None

    match = re.search(r"\b(19|20)\d{2}\b", value)

    return int(match.group()) if match else None


def evaluate_education(candidate, job) -> bool | None:
    """
    Check degree and graduation-year eligibility.
    Returns:
        True  - Candidate satisfies eligibility.
        False - Candidate does not satisfy eligibility.
        None  - Required information is missing.
    """

    if not job.education:
        return None

    accepted_degrees = {
        normalize_education_text(degree).replace(" ", "")
        for degree in job.education
    }

    degree_aliases = {
        "bachelorofengineering": "be",
        "be": "be",
        "bacheloroftechnology": "btech",
        "btech": "btech",
        "bachelorofscience": "bsc",
        "bsc": "bsc",
        "bachelorofcomputerapplications": "bca",
        "bca": "bca",
        "masterofscience": "msc",
        "msc": "msc",
        "masterofcomputerapplications": "mca",
        "mca": "mca"
    }

    accepted_degrees = {
        degree_aliases.get(degree, degree)
        for degree in accepted_degrees
    }

    education_data = candidate.education

    if not education_data:
        return None

    matching_degree_found = False
    missing_year_found = False

    for education in education_data:

        if isinstance(education, dict):
            degree = education.get("degree")
            graduation_year = education.get("graduation_year")
        else:
            degree = getattr(education, "degree", None)
            graduation_year = getattr(
                education, "graduation_year", None
            )

        if not degree:
            continue

        candidate_degree = (
            normalize_education_text(degree).replace(" ", "")
        )

        candidate_degree = degree_aliases.get(
            candidate_degree,
            candidate_degree
        )

        if candidate_degree not in accepted_degrees:
            continue

        matching_degree_found = True

        # If JD has no graduation-year restriction,
        # matching degree is sufficient.
        if not job.graduation_year_eligibility:
            return True

        candidate_year = extract_graduation_year(
            str(graduation_year) if graduation_year else None
        )

        if candidate_year is None:
            missing_year_found = True
            continue

        if candidate_year in job.graduation_year_eligibility:
            return True

    if not matching_degree_found:
        return False

    if missing_year_found:
        return None

    return False


# --------------------------------------------------
# 8. MAIN CANDIDATE MATCHING FUNCTION
# --------------------------------------------------

def match_candidate(
    candidate: ResumeProfile,
    job: JobDescriptionProfile
) -> CandidateMatchResult:

    resume_evidence = build_resume_evidence(candidate)

    # Collect all text inputs for one local embedding batch.
    all_texts = (
        resume_evidence
        + job.required_skills
        + job.preferred_skills
        + job.education
    )

    if not all_texts:
        raise ValueError("No candidate or job information available.")

    # Generate local embeddings in one batch.
    all_embeddings = generate_embeddings(all_texts)

    evidence_count = len(resume_evidence)
    required_count = len(job.required_skills)
    preferred_count = len(job.preferred_skills)

    evidence_embeddings = all_embeddings[:evidence_count]

    required_embeddings = all_embeddings[
        evidence_count:evidence_count + required_count
    ]

    preferred_embeddings = all_embeddings[
        evidence_count + required_count:
        evidence_count + required_count + preferred_count
    ]

    education_embeddings = all_embeddings[
        evidence_count + required_count + preferred_count:
    ]

    # Required skills
    required_result = evaluate_skills(
        job.required_skills,
        resume_evidence,
        evidence_embeddings,
        required_embeddings
    )

    # Preferred skills
    preferred_result = evaluate_skills(
        job.preferred_skills,
        resume_evidence,
        evidence_embeddings,
        preferred_embeddings
    )

    # Experience
    experience_score = evaluate_experience(candidate, job)

    # Education
    candidate_education_texts = [
        " ".join(filter(None, [
            education.degree,
            education.field_of_study,
            education.institution
        ]))
        for education in candidate.education
    ]

    candidate_education_texts = [
        text for text in candidate_education_texts if text.strip()
    ]

    # Generate candidate education vectors in a separate local batch.
    candidate_education_embeddings = (
        generate_embeddings(candidate_education_texts)
        if candidate_education_texts else []
    )

    education_eligible = evaluate_education(
        candidate,
        job,
    )

    # Aggregate diagnostic scores across individual skill requirements.
    diagnostic_results = []

    if job.required_skills:
        diagnostic_results.append(required_result)

    if job.preferred_skills:
        diagnostic_results.append(preferred_result)

    keyword_match_score = (
        sum(r["keyword_score"] for r in diagnostic_results)
        / len(diagnostic_results)
        if diagnostic_results else 0.0
    )

    semantic_match_score = (
        sum(r["semantic_score"] for r in diagnostic_results)
        / len(diagnostic_results)
        if diagnostic_results else 0.0
    )

    # Weighted overall score.
    active_weights = []

    if experience_score is not None:
        active_weights.append(
            (EXPERIENCE_WEIGHT, experience_score)
        )

    if job.required_skills:
        active_weights.append(
            (REQUIRED_SKILLS_WEIGHT, required_result["match_score"])
        )

    if job.preferred_skills:
        active_weights.append(
            (PREFERRED_SKILLS_WEIGHT, preferred_result["match_score"])
        )

    total_weight = sum(weight for weight, _ in active_weights)

    overall_match_score = (
        sum(weight * score for weight, score in active_weights)
        / total_weight
        if total_weight else 0.0
    )

    # Match summary.
    if overall_match_score >= 75:
        summary = "Strong candidate match."
    elif overall_match_score >= 50:
        summary = "Moderate candidate match."
    else:
        summary = "Low candidate match."

    if education_eligible is False:
        summary += " Education requirement not verified."

    # Structured result.
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
