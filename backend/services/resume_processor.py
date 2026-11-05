
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from backend.services.resume_extractor import extract_resume_text
from backend.services.text_chunker import chunk_text
from backend.services.vector_store import (
    calculate_file_hash,
    resume_exists,
    store_resume
)
from backend.agents.resume_parser import parse_resume


def process_resume(file_path: str) -> dict:
    """
    Complete resume processing pipeline:
    Extract -> Parse -> Chunk -> Embed -> Store.
    """

    path = Path(file_path)

    # Validate uploaded file
    if not path.exists():
        raise FileNotFoundError(f"Resume not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF resumes are supported.")

    # Step 1: Calculate file hash
    file_hash = calculate_file_hash(file_path)

    # Step 2: Check duplicate before making API calls
    if resume_exists(file_hash):
        return {
            "status": "duplicate",
            "message": "This resume has already been uploaded.",
            "file_name": path.name
        }

    # Step 3: Extract resume text using PyMuPDF
    resume_text = extract_resume_text(file_path)

    # Step 4: Parse resume using Gemini
    candidate_profile = parse_resume(resume_text)

    candidate_name = (
        candidate_profile.full_name or "Unknown Candidate"
    )

    # Step 5: Chunk extracted resume text
    resume_chunks = chunk_text(resume_text)

    # Step 6: Generate candidate ID
    candidate_id = f"CAND_{uuid4().hex[:12].upper()}"

    # Step 7: Prepare metadata
    candidate_metadata = {
        "candidate_id": candidate_id,
        "file_name": path.name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "email": candidate_profile.email or "",
        "location": candidate_profile.location or ""
    }

    # Step 8: Generate embeddings and store in ChromaDB
    storage_result = store_resume(
        file_path=file_path,
        candidate_name=candidate_name,
        resume_chunks=resume_chunks,
        file_hash=file_hash,
        candidate_metadata=candidate_metadata
    )

    return {
        "status": storage_result["status"],
        "message": storage_result["message"],
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "file_name": path.name,
        "total_chunks": len(resume_chunks),
        "file_hash": file_hash,
        "candidate_profile": candidate_profile.model_dump()
    }
