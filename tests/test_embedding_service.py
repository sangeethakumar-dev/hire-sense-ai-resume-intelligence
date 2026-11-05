
from backend.services.embedding_service import (
    generate_embedding,
    generate_embeddings
)


def test_single_embedding():

    text = "Python developer with experience in FastAPI and Machine Learning."

    embedding = generate_embedding(text)

    print("Single embedding dimension:", len(embedding))
    print("First five values:", embedding[:5])

    assert len(embedding) == 384


def test_multiple_embeddings():

    texts = [
        "Python developer",
        "Machine Learning Engineer",
        "Generative AI Engineer"
    ]

    embeddings = generate_embeddings(texts)

    print("Number of embeddings:", len(embeddings))

    assert len(embeddings) == 3
    assert all(len(vector) == 384 for vector in embeddings)


if __name__ == "__main__":
    test_single_embedding()
    test_multiple_embeddings()
