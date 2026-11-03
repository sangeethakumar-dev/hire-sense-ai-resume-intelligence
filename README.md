# HireSense AI
### Multi-Agent Resume Intelligence & Candidate Evaluation System

HireSense AI is an AI-powered recruitment intelligence platform designed to automate resume screening and candidate evaluation using specialized AI agents.

The system extracts structured candidate information from resumes, analyses job descriptions, evaluates candidate-job compatibility, identifies skill gaps, and generates evidence-based candidate evaluation reports.

## 🎯 Business Problem

Recruiters spend considerable time manually reviewing resumes, extracting candidate information, and comparing candidate qualifications against job requirements.

This process can be repetitive, time-consuming, and inconsistent.

HireSense AI aims to streamline recruitment workflows through intelligent document processing, multi-agent orchestration, and automated candidate evaluation.

## 💡 Proposed Solution

HireSense AI introduces a multi-agent architecture where each specialized agent performs a specific recruitment task.

### Core AI Agents

| Agent | Responsibility |
|---|---|
| Resume Parsing Agent | Extracts candidate details, education, skills, and experience from resumes. |
| Job Description Analysis Agent | Identifies required skills, qualifications, and experience from job descriptions. |
| Candidate Matching Agent | Evaluates candidate profiles against job requirements and calculates matching scores. |
| Skill Gap Analysis Agent | Identifies missing skills and areas requiring improvement. |
| Candidate Evaluation Agent | Generates structured, evidence-based candidate evaluation reports. |

## ⚙️ System Workflow

1. Upload candidate resumes.
2. Provide the target job description.
3. Extract structured information from resumes.
4. Analyse job requirements.
5. Compare candidate profiles against job requirements.
6. Identify matching strengths and skill gaps.
7. Generate candidate evaluation reports for recruiter review.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| AI / LLM | Google Gemini API |
| Document Processing | PyMuPDF |
| Data Validation | Pydantic |
| Data Processing | Pandas |
| Frontend | Streamlit |
| Version Control | Git & GitHub |

## ✨ Key Features

- Automated resume information extraction.
- Structured candidate profile generation.
- Job description analysis.
- Candidate-job matching and scoring.
- Skill gap identification.
- Evidence-based candidate evaluation.
- Interactive recruiter dashboard.
- Downloadable evaluation reports.

## 🏗️ Architecture

The application follows a modular multi-agent architecture coordinated by a central workflow controller.

Each agent performs a clearly defined task, combining LLM-powered extraction and analysis with deterministic validation and scoring logic.

## 🔒 Responsible AI

HireSense AI is designed as a recruitment decision-support system, not an autonomous hiring platform.

- Candidate evaluations are based on job-related qualifications.
- Matching scores use transparent evaluation criteria.
- Recommendations are supported by extracted evidence.
- Sensitive personal attributes are excluded from candidate ranking.
- Recruiters retain final hiring decisions.

## 🚀 Project Status

**Development in Progress**

The initial MVP focuses on resume parsing, job description analysis, candidate matching, skill gap analysis, and candidate evaluation.

## 👩‍💻 Author

**Sangeetha S**

AI Engineer Intern | Generative AI | LLM Applications | AI Agents

---

*HireSense AI — Making Recruitment Smarter Through Intelligent Automation.*
