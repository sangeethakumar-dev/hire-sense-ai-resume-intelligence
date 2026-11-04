from backend.services.resume_extractor import extract_resume_text
from backend.agents.resume_parser import parse_resume

def test_resume_parser():
    resume_path = "data/resumes/my_resume.pdf"

    #Extract Raw Text from PDF

    resume_text = extract_resume_text(resume_path)

    print("\n================RAW RESUME EXTRAXTION=================")
    print(resume_text)

    # Parse Resume using Gemini
    candidate = parse_resume(resume_text)

    #Display Structured Candidate Information

    print("\n===================STRUCTURED CANDIDATE PROFILE=====================")

    print("\nCandidate Name : ",candidate.full_name)
    print("\nEmail : ",candidate.email)
    print("\nPhone : ",candidate.phone)
    print("\nLocation : ",candidate.location)

    print("\nProfessional Summary : ")
    print(candidate.professional_summary)

    print("\nTechnical Skills : ")
    print(candidate.technical_skills)

    print("\nSoft Skills : ")
    print(candidate.soft_skills)

    print("\neducation :")
    print(candidate.education)

    print("\nWork Experience : ")
    for experience in candidate.work_experience:
        print(experience.model_dump())

    print("\nProjects : ")
    for project in candidate.projects:
        print(project.model_dump())

    print("\nCertifications : ")
    for certificate in candidate.Certifications:
        print(certificate.model_dump())

    #Display Complete JSON Output

    print("\n====================Final JSON Output===========================")
    print(candidate.model_dump_json(indent=4))

if __name__ == "__main__":
    test_resume_parser()