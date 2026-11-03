from backend.services.resume_extractor import extract_resume_text

resume_path ="data/resumes/my_resume.pdf"

try :
    text = extract_resume_text(resume_path)

    print("Resume Extraction Successful!!!")
    print("Extracted Text : \n",)
    print(text)
except Exception as e:
    print(f'Extraction Failed : {e}')
