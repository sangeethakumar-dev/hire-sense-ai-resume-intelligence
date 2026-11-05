
from backend.services.resume_extractor import extract_resume_text
from backend.services.text_chunker import chunk_text


def test_text_chunker():

    resume_path = "data/resumes/my_resume.pdf"

    resume_text = extract_resume_text(resume_path)

    chunks = chunk_text(resume_text)

    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {index} ---")
        print(chunk)

    assert len(chunks) > 0


if __name__ == "__main__":
    test_text_chunker()
