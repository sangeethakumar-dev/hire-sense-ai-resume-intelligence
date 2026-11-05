
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import json

from backend.services.resume_extractor import extract_resume_text
from backend.services.text_chunker import chunk_text

from backend.services.vector_store import (
    calculate_file_hash,
    get_cached_resume,
    update_resume_metadata,
    store_resume
)

from backend.agents.resume_parser import parse_resume


def process_resume(file_path: str) -> dict:
    """
    Process a new resume or reuse an existing cached resume.

    New resume:
        Extract -> Parse -> Chunk -> Embed -> Store

    Duplicate resume:
        Retrieve cached profile -> Reuse existing vectors

    Legacy duplicate without cached profile:
        Extract -> Parse -> Update metadata
        Existing embeddings are preserved.
    """

    path = Path(file_path)

    # --------------------------------------------------
    # 1. Validate uploaded file
    # --------------------------------------------------

    if not path.exists():
        raise FileNotFoundError(
            f"Resume not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF resumes are supported."
        )

    # --------------------------------------------------
    # 2. Calculate SHA-256 hash
    # --------------------------------------------------

    file_hash = calculate_file_hash(file_path)

    # --------------------------------------------------
    # 3. Check existing resume cache
    # --------------------------------------------------

    cached_resume = get_cached_resume(file_hash)

    if cached_resume:

        candidate_id = (
            cached_resume.get("candidate_id")
            or f"CAND_{uuid4().hex[:12].upper()}"
        )

        candidate_profile_data = cached_resume.get(
            "candidate_profile"
        )

        # ----------------------------------------------
        # Existing profile found: reuse it
        # ----------------------------------------------

        if candidate_profile_data:

            print(
                f"Using cached resume profile: {path.name}"
            )

            return {
                "status": "cached",
                "message": "Existing resume profile and vectors reused.",
                "candidate_id": candidate_id,
                "candidate_name": (
                    cached_resume.get("candidate_name")
                    or candidate_profile_data.get("full_name")
                    or "Unknown Candidate"
                ),
                "file_name": path.name,
                "file_hash": file_hash,
                "candidate_profile": candidate_profile_data,
                "cached": True
            }

        # ----------------------------------------------
        # Legacy record: profile not previously stored
        # ----------------------------------------------

        print(
            f"Cached vectors found, but profile is missing. "
            f"Extracting profile once: {path.name}"
        )

        resume_text = extract_resume_text(file_path)

        candidate_profile = parse_resume(resume_text)

        candidate_name = (
            candidate_profile.full_name
            or cached_resume.get("candidate_name")
            or "Unknown Candidate"
        )

        profile_metadata = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "candidate_profile_json": json.dumps(
                candidate_profile.model_dump()
            )
        }

        updated = update_resume_metadata(
            file_hash=file_hash,
            extra_metadata=profile_metadata
        )

        if not updated:
            raise RuntimeError(
                "Unable to update cached resume metadata."
            )

        return {
            "status": "cached",
            "message": "Legacy resume profile recovered. Existing vectors reused.",
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "file_name": path.name,
            "file_hash": file_hash,
            "candidate_profile": candidate_profile.model_dump(),
            "cached": True
        }

    # --------------------------------------------------
    # 4. New resume: extract text
    # --------------------------------------------------

    print(
        f"Processing new resume: {path.name}"
    )

    resume_text = extract_resume_text(file_path)

    # --------------------------------------------------
    # 5. Parse resume using Gemini
    # --------------------------------------------------

    candidate_profile = parse_resume(resume_text)

    candidate_name = (
        candidate_profile.full_name
        or "Unknown Candidate"
    )

    # --------------------------------------------------
    # 6. Chunk resume text
    # --------------------------------------------------

    resume_chunks = chunk_text(resume_text)

    if not resume_chunks:
        raise ValueError(
            "No text chunks could be generated from the resume."
        )

    # --------------------------------------------------
    # 7. Generate candidate ID
    # --------------------------------------------------

    candidate_id = (
        f"CAND_{uuid4().hex[:12].upper()}"
    )

    # --------------------------------------------------
    # 8. Prepare candidate metadata
    # --------------------------------------------------

    candidate_metadata = {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "file_name": path.name,
        "uploaded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "email": candidate_profile.email or "",
        "location": candidate_profile.location or "",

        # Store structured profile as JSON string.
        # ChromaDB metadata supports scalar values.
        "candidate_profile_json": json.dumps(
            candidate_profile.model_dump()
        )
    }

    # --------------------------------------------------
    # 9. Generate embeddings and store vectors
    # --------------------------------------------------

    storage_result = store_resume(
        file_path=file_path,
        candidate_name=candidate_name,
        resume_chunks=resume_chunks,
        file_hash=file_hash,
        candidate_metadata=candidate_metadata
    )

    # --------------------------------------------------
    # 10. Return processed candidate
    # --------------------------------------------------

    return {
        "status": storage_result["status"],
        "message": storage_result["message"],
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "file_name": path.name,
        "total_chunks": len(resume_chunks),
        "file_hash": file_hash,
        "candidate_profile": candidate_profile.model_dump(),
        "cached": False
    }
