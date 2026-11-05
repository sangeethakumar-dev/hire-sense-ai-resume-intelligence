
from backend.services.resume_processor import process_resume


def test_resume_processor():

    resume_path = "data/resumes/my_resume.pdf"

    result = process_resume(resume_path)

    print("\n========== RESUME PROCESSING RESULT ==========")

    print("Status:", result["status"])
    print("Message:", result["message"])

    if result["status"] == "success":
        print("Candidate ID:", result["candidate_id"])
        print("Candidate Name:", result["candidate_name"])
        print("Total Chunks:", result["total_chunks"])

    print("===============================================")


if __name__ == "__main__":
    test_resume_processor()
