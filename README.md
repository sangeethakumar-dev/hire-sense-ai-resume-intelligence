# HireSense AI
### AI-Powered Resume Intelligence & Candidate Evaluation System

HireSense AI is an AI-powered recruitment intelligence platform that automates resume screening and candidate evaluation using Generative AI, semantic search, and intelligent matching algorithms.

The platform analyses job descriptions, extracts structured information from candidate resumes, evaluates candidate-job compatibility, identifies skill gaps, ranks candidates, and generates individual recruitment reports through an interactive recruiter dashboard.

## 🎯 Business Problem

Recruiters often spend significant time manually reviewing resumes, extracting candidate information, and comparing qualifications against job requirements.

Traditional resume screening can be repetitive, time-consuming, and inconsistent.

HireSense AI aims to streamline this process through automated document extraction, AI-powered analysis, semantic matching, and structured candidate evaluation.

## 💡 Proposed Solution

HireSense AI follows a modular, agent-based architecture in which specialized components handle different stages of the recruitment workflow.

### Core Components

| Component | Responsibility |
|---|---|
| Resume Parsing Agent | Extracts candidate information, education, technical skills, projects, and work experience from PDF resumes. |
| Job Description Analysis Agent | Analyses job descriptions and extracts job titles, required skills, preferred skills, qualifications, and experience criteria. |
| Candidate Matching Engine | Evaluates candidate profiles against job requirements using keyword and semantic matching. |
| Skill Gap Analysis | Identifies matched skills, missing required skills, and matched preferred skills. |
| Candidate Ranking | Calculates candidate rankings based on matching scores. |
| Candidate Report Generation | Produces structured candidate evaluation reports for recruiter review. |

## ⚙️ System Workflow

1. Upload a job description.
2. Upload multiple candidate resumes in PDF format.
3. Extract text and structured information from resumes.
4. Analyse the job description using Google Gemini.
5. Generate semantic embeddings using Sentence Transformers.
6. Store and retrieve resume vectors using ChromaDB.
7. Compare candidate profiles against job requirements.
8. Calculate matching scores and evaluate education eligibility.
9. Identify matched skills and skill gaps.
10. Rank candidates and generate individual evaluation reports.
11. View results through the HireSense AI recruiter dashboard.

## ✨ Key Features

### 1. AI-Powered Resume Parsing
- Extracts candidate names, contact details, education, work experience, technical skills, and projects.
- Converts unstructured resume content into structured candidate profiles.
- Supports PDF resume uploads.

### 2. Intelligent Job Description Analysis
- Uses Google Gemini to analyse job descriptions.
- Extracts required and preferred skills.
- Identifies educational qualifications and experience criteria.
- Extracts explicitly stated graduation-year eligibility requirements.

### 3. Semantic Resume Matching
- Generates text embeddings using Sentence Transformers.
- Uses ChromaDB for persistent vector storage and retrieval.
- Combines keyword matching and semantic similarity to evaluate candidate-job compatibility.

### 4. Candidate Scoring and Ranking
- Calculates overall candidate matching scores.
- Evaluates required and preferred skill matches.
- Calculates experience matching scores.
- Evaluates education eligibility against job requirements.
- Ranks candidates based on their matching scores.

### 5. Resume Caching and Reuse
- Identifies previously processed resumes using file hashing.
- Reuses cached candidate profiles and stored resume vectors.
- Avoids unnecessary resume parsing and embedding generation for previously processed resumes.
- Supports evaluating existing candidates against new job descriptions.

### 6. Skill Gap Analysis
- Highlights matched required skills.
- Identifies missing required skills.
- Displays matched preferred skills.
- Presents candidate technical skills through compact visual skill indicators.

### 7. Recruiter Dashboard and Reports
- Interactive Streamlit dashboard.
- Candidate ranking table.
- Individual candidate reports.
- Matching score breakdown.
- Education and work experience details.
- Downloadable candidate evaluation reports.
- Processing error reporting.

### 8. API Reliability
- Implements retry handling for temporary Gemini API failures.
- Handles temporary service unavailability and rate-limit errors.
- Provides processing error information for failed candidate evaluations.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend / Dashboard | Streamlit |
| Generative AI | Google Gemini API |
| LLM Integration | LangChain, LangChain Google GenAI |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Database | ChromaDB |
| Document Processing | PyMuPDF |
| Data Validation | Pydantic |
| Data Processing | Pandas |
| Version Control | Git, GitHub |

## 🏗️ System Architecture

The application follows a modular architecture with specialized AI agents and backend services.

**High-level workflow:**

```text
                  Recruiter
                      |
                      v
              Streamlit Dashboard
                      |
             Resume + Job Description
                      |
          +-----------+-----------+
          |                       |
          v                       v
    Resume Parsing Agent    JD Analysis Agent
          |                       |
          v                       v
   Structured Candidate     Structured Job
       Profiles              Requirements
          |
          v
   Sentence Transformers
          |
          v
       ChromaDB
   (Persistent Vector Store)
          |
          v
   Candidate Matching Engine
          |
          v
    Skill Gap Analysis
          |
          v
     Candidate Ranking
          |
          v
   Candidate Report Generation
          |
          v
     Recruiter Dashboard
```

## 📁 Project Structure

```text
hire-sense-ai-resume-intelligence/
│
├── backend/
│   ├── agents/
│   │   ├── resume_parser.py
│   │   ├── job_analyser.py
│   │   └── candidate_matcher.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── services/
│       ├── resume_extractor.py
│       ├── resume_processor.py
│       ├── text_chunker.py
│       ├── vector_store.py
│       ├── jd_processor.py
│       ├── recruitment_pipeline.py
│       ├── candidate_ranking.py
│       └── candidate_report.py
│
├── data/
│   └── job_descriptions/
│
├── tests/
│
├── app.py
├── list_models.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- Google Gemini API key.

### 1. Clone the Repository

```bash
git clone https://github.com/sangeethakumar-dev/hire-sense-ai-resume-intelligence.git

cd hire-sense-ai-resume-intelligence
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure the required Gemini API key is configured using the environment variable expected by the application.

For local development, create a `.env` file using `.env.example` as a reference. Never commit API keys or other credentials.

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, normally at:

```text
http://localhost:8501
```

## 🧪 Testing

The project includes tests for important backend components, including:

- Candidate matching.
- Candidate ranking.
- Candidate report generation.
- Experience calculation.
- Skill normalization.
- Recruitment pipeline execution.

Run the test suite using:

```bash
pytest
```

## 🔒 Responsible AI

HireSense AI is designed as a recruitment decision-support system, not an autonomous hiring platform.

- Candidate matching scores are intended to assist recruiter evaluation.
- Extracted resume information may require manual verification.
- Education eligibility depends on the requirements extracted from the job description and the information available in the resume.
- Missing information should not automatically be interpreted as verified eligibility.
- Recruiters should independently review candidate qualifications and make final hiring decisions.

**Important:** Matching scores are algorithmic estimates, not guarantees of candidate suitability or hiring success.

## 📌 Project Status

**MVP Completed — November 2026**

The current MVP includes:

- Resume parsing and structured profile extraction.
- Job description analysis.
- Semantic and keyword-based candidate matching.
- ChromaDB-based resume vector storage and reuse.
- Candidate scoring and ranking.
- Education eligibility evaluation.
- Skill gap analysis.
- Individual candidate reports.
- Interactive Streamlit recruiter dashboard.

## 👩‍💻 Author

**Sangeetha S**

AI Engineer Intern | Generative AI | LLM Applications | AI Agents

GitHub: [sangeethakumar-dev](https://github.com/sangeethakumar-dev)

---

*HireSense AI — Making Recruitment Smarter Through Intelligent Automation.*
