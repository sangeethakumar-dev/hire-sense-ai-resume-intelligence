
from backend.services.jd_processor import process_job_description


def test_jd_processor():

    jd_path = "data/job_descriptions/vasiva_ai_intern.txt"

    result = process_job_description(jd_path)

    print("\n========== JOB DESCRIPTION RESULT ==========")

    print("Status:", result["status"])
    print("Job ID:", result["job_id"])
    print("Job Title:", result["job_title"])
    print("Total Requirements:", result["total_requirements"])

    print("\nExtracted Job Profile:")

    for key, value in result["job_profile"].items():
        print(f"{key}: {value}")

    print("============================================")


if __name__ == "__main__":
    test_jd_processor()
