from backend.agents.job_analyser import analyse_job_description

def test_job_analyser():
    #Read Job description from the text file
    jd_path = "data/job_descriptions/vasiva_ai_intern.txt"

    with open(jd_path,'r',encoding="utf-8") as file:
        jd_text = file.read()

    #Analyse the job description

    job_profile = analyse_job_description(jd_text)

    #Display Extracted Information

    print("\n=====================Job Analysis report=====================")
    print("Job title", job_profile.job_title)

    print("\n==================Required Skills======================")
    for skill in job_profile.preferred_skills:
        print("-",skill)

    print("\n====================Minimum Experience==========================")
    print(job_profile.minimum_experience)

    print("\n======================Education========================")
    for qualification in job_profile.education:
        print("-",qualification)

    print("\n=================Responsibilities====================")
    for responsibility in job_profile.responsibilities:
        print("-",responsibility)

    #Display COmplete JSON Output

    print("\n=====================JSON Output==========================")
    print(job_profile.model_dump_json(indent=4))


if __name__ == "__main__":
    test_job_analyser()