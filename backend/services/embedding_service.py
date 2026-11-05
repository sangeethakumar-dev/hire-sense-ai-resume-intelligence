from sentence_transformers import SentenceTransformer
from typing import List

#Loading the embedding model

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)

def generate_embedding(text: str) -> List[float]:
    #Generate EMbedding for a single text

    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text")

    embedding = embedding_model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def generate_embeddings(texts: str)-> List[List[float]]:
    #Generate Embeddings for multiple text in a batch

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Input Contains Empty text")

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings.tolist()