
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from backend.agents.job_analyser import analyse_job_description
from backend.services.vector_store import store_job_description


def process_job_description(file_path: str) -> dict:
    """
    Process a job description:
    Read -> Analyse -> Embed -> Store.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Job description not found: {file_path}"
        )

    if path.suffix.lower() not in [".txt", ".md"]:
        raise ValueError(
            "Only TXT and Markdown job descriptions are supported."
        )

    # Step 1: Read job description
    with open(path, "r", encoding="utf-8") as file:
        jd_text = file.read()

    if not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    # Step 2: Analyse using Gemini
    job_profile = analyse_job_description(jd_text)

    # Step 3: Collect job requirements
    requirements = (
        job_profile.required_skills
        + job_profile.preferred_skills
        + job_profile.responsibilities
    )

    if job_profile.minimum_experience:
        requirements.append(
            f"Minimum experience: {job_profile.minimum_experience}"
        )

    requirements.extend(job_profile.education)

    # Step 4: Generate job ID
    job_id = f"JOB_{uuid4().hex[:12].upper()}"

    # Step 5: Prepare metadata
    metadata = {
        "file_name": path.name,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }

    # Step 6: Store requirements and local embeddings
    storage_result = store_job_description(
        job_id=job_id,
        job_title=job_profile.job_title or "Unknown Job",
        requirements=requirements,
        jd_metadata=metadata
    )

    return {
        "status": "success",
        "job_id": job_id,
        "job_title": job_profile.job_title,
        "total_requirements": len(requirements),
        "job_profile": job_profile.model_dump(),
        "storage": storage_result
    }
