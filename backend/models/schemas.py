from pydantic import BaseModel,Field

class WorkExperience(BaseModel):
    company: str | None = None
    job_title : str | None = None
    start_date : str |None = None
    end_date : str | None = None
    description : list[str] = Field(default_factory=list)

class Education(BaseModel):
    institution: str |None = None
    degree : str | None = None
    field_of_study : str |None = None
    graduation_year : str |None = None

class Project (BaseModel):
    project_name : str |None = None
    description : str|None = None
    technologies : str|None = None

class Certification(BaseModel):
    certification_name : str |None = None
    issuing_organization : str|None = None

class ResumeProfile(BaseModel):
    """Structured information extracted from a candidate's resume"""

    full_name : str|None = None
    email : str |None = None
    phone : str |None = None
    location : str |None = None
    professional_summary : str | None = None

    technical_skills : list[str] = Field(default_factory=list)
    soft_skills : list[str] = Field(default_factory=list)

    education : list[Education] = Field(default_factory=list)
    work_experience : list[WorkExperience] = Field(default_factory=list)
    projects : list[Project] = Field(default_factory=list)
    Certifications : list[Certification] = Field(default_factory=list)
    
class JobDescriptionProfile(BaseModel):
    job_title : str | None = None
    required_skills : list[str] = Field(default_factory=list)
    preferred_skills : list[str] = Field(default_factory=list)
    minimum_experience : str | None = None
    education : list[str] = Field(default_factory=list)
    responsibilities : list[str] = Field(default_factory=list)
    

