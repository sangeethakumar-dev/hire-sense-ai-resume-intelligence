import pymupdf
from pathlib import Path

def extract_resume_text(file_path : str) -> str :
    resume_path = Path(file_path)

    #Check whether the file exixts

    if not resume_path.exists():
        raise FileNotFoundError(f"Resume File Not Found : {resume_path}")

    #Validate the file extension
    if resume_path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported File Format . Please upload a PDF Resume!!!")

    extracted_text = []

    try :
        #Opening the PDF Document
        with pymupdf.open(resume_path) as pdf_document:

            #Check whether the PDF Document contains pages
            if pdf_document.page_count ==0:
                raise ValueError ("The Uploaded PDF have no pages")

            #Extract Text from each page

            for page_number,page in enumerate(pdf_document,start=1):
                page_text = page.get_text("text")

                if page_text.strip():
                    extracted_text.append(page_text)

    except pymupdf.FileDataError as error:
        raise ValueError(
            "The Uploaded PDF is corrupted or invalid"
        ) from error

    #Combine text from all pages

    full_text = "\n".join(extracted_text)

    #Validate Extracted Content

    if not full_text.strip():
        raise ValueError (
            "No readable text found in the PDF"
            "The resume may be image based or scanned"
        )        

    #Return Extracted Resune Text
    return full_text

