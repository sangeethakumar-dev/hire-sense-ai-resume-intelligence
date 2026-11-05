
import chromadb
import hashlib
import os
from pathlib import Path
from typing import Any
import json

from backend.services.embedding_service import generate_embeddings


# Persistent ChromaDB storage directory
CHROMA_DB_PATH = Path(
    os.getenv("CHROMA_DB_PATH", "data/chroma_db")
)

CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

# Initialize persistent ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)

# Create or retrieve resume collection
resume_collection = chroma_client.get_or_create_collection(
    name="resume_collection",
    metadata={"hnsw:space": "cosine"}
)

#Seperate Collection for Job Descriptions
jd_collection = chroma_client.get_or_create_collection(
    name="job_description_collection",
    metadata={"hnsw:space": "cosine"}
)

def calculate_file_hash(file_path: str) -> str:
    """
    Generate SHA-256 hash to identify duplicate resume files.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def resume_exists(file_hash: str) -> bool:
    """
    Check whether a resume with the same file hash already exists.
    """

    result = resume_collection.get(
        where={"file_hash": file_hash},
        limit=1
    )

    return len(result["ids"]) > 0


def store_resume(
    file_path: str,
    candidate_name: str,
    resume_chunks: list[str],
    file_hash: str,
    candidate_metadata: dict[str, Any] | None = None
) -> dict:
    """
    Generate and store resume chunk embeddings in ChromaDB.
    """

    if not resume_chunks:
        raise ValueError("Resume chunks cannot be empty.")

    # Generate embeddings locally in batches
    embeddings = generate_embeddings(resume_chunks)

    # Generate unique IDs for resume chunks
    chunk_ids = [
        f"{file_hash}_{index}"
        for index in range(len(resume_chunks))
    ]

    # Prepare metadata for each chunk
    metadatas = []

    for index in range(len(resume_chunks)):

        metadata = {
            "file_hash": file_hash,
            "candidate_name": candidate_name,
            "chunk_index": index
        }

        if candidate_metadata:
            metadata.update(candidate_metadata)

        metadatas.append(metadata)

    # Store documents, embeddings and metadata
    resume_collection.add(
        ids=chunk_ids,
        documents=resume_chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "message": "Resume successfully stored.",
        "candidate_name": candidate_name,
        "total_chunks": len(resume_chunks),
        "file_hash": file_hash
    }

def store_job_description(
    job_id: str,
    job_title: str,
    requirements: list[str],
    jd_metadata: dict | None = None
) -> dict:

    if not requirements:
        raise ValueError("Job requirements cannot be empty.")

    embeddings = generate_embeddings(requirements)

    ids = [
        f"{job_id}_{index}"
        for index in range(len(requirements))
    ]

    metadatas = []

    for index, requirement in enumerate(requirements):
        metadata = {
            "job_id": job_id,
            "job_title": job_title,
            "requirement_index": index,
            "source_type": "job_description"
        }

        if jd_metadata:
            metadata.update(jd_metadata)

        metadatas.append(metadata)

    jd_collection.upsert(
        ids=ids,
        documents=requirements,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "job_id": job_id,
        "total_requirements": len(requirements)
    }



def search_resume_chunks(
    query: str,
    top_k: int = 5
) -> dict:
    """
    Search relevant resume chunks using semantic similarity.
    """

    query_embedding = generate_embeddings([query])[0]

    results = resume_collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, resume_collection.count())
    )

    return results


# ============================================================
# RESUME CACHE RETRIEVAL
# ============================================================

def get_cached_resume(file_hash: str) -> dict | None:
    """
    Retrieve an already processed resume using its SHA-256 hash.

    Returns the candidate profile, candidate ID and existing
    vector metadata without generating new embeddings.
    """

    result = resume_collection.get(
        where={"file_hash": file_hash},
        include=["metadatas"]
    )

    if not result["ids"]:
        return None

    metadatas = result.get("metadatas") or []

    if not metadatas:
        return None

    metadata = metadatas[0]

    profile_json = metadata.get("candidate_profile_json")

    if not profile_json:
        return {
            "candidate_id": metadata.get("candidate_id"),
            "candidate_name": metadata.get("candidate_name"),
            "candidate_profile": None,
            "file_hash": file_hash,
            "cached": True,
            "metadata": metadata
        }

    candidate_profile = json.loads(profile_json)

    return {
        "candidate_id": metadata.get("candidate_id"),
        "candidate_name": metadata.get("candidate_name"),
        "candidate_profile": candidate_profile,
        "file_hash": file_hash,
        "cached": True,
        "metadata": metadata
    }


# ============================================================
# UPDATE EXISTING RESUME METADATA
# ============================================================

def update_resume_metadata(
    file_hash: str,
    extra_metadata: dict
) -> bool:
    """
    Update metadata of existing resume chunks.

    This does not regenerate or modify existing embeddings.
    """

    result = resume_collection.get(
        where={"file_hash": file_hash},
        include=["metadatas"]
    )

    ids = result.get("ids", [])
    metadatas = result.get("metadatas", [])

    if not ids:
        return False

    updated_metadatas = []

    for metadata in metadatas:

        updated_metadata = metadata.copy()

        updated_metadata.update(extra_metadata)

        updated_metadatas.append(
            updated_metadata
        )

    resume_collection.update(
        ids=ids,
        metadatas=updated_metadatas
    )

    return True

