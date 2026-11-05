
# ============================================================
# HIRESENSE AI
# PART 1 OF 3
# Application Setup, Styling and File Uploads
# ============================================================

import os
import streamlit as st
import tempfile

from pathlib import Path


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

os.environ["CHROMA_DB_PATH"] = str(
    PROJECT_ROOT / "data" / "chroma_db_streamlit"
)

from backend.services.recruitment_pipeline import (
    run_recruitment_pipeline
)


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HireSense AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 3. SESSION STATE
# ============================================================

if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None

if "analysis_started" not in st.session_state:
    st.session_state.analysis_started = False


# ============================================================
# 4. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */

    .stApp {
        background: linear-gradient(
            135deg,
            #f8f9ff 0%,
            #ffffff 55%,
            #f4f0ff 100%
        );
        color: #17143f;
    }

    /* Main container */

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Header */

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Main title */

    .main-title {
        text-align: center;
        font-size: 46px;
        font-weight: 800;
        color: #21145c;
        margin-bottom: 4px;
    }

    .main-subtitle {
        text-align: center;
        font-size: 17px;
        color: #686487;
        margin-bottom: 32px;
    }

    /* Upload cards */

    .upload-card {
        background: #ffffff;
        border: 1px solid #e2d8fa;
        border-radius: 16px;
        padding: 20px;
        min-height: 105px;
        box-shadow: 0 4px 15px rgba(73, 44, 130, 0.06);
    }

    .upload-heading {
        font-size: 20px;
        font-weight: 700;
        color: #21145c;
        margin-bottom: 8px;
    }

    .upload-description {
        font-size: 14px;
        color: #77738f;
    }

    /* File uploader */

    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px solid #e2d8fa;
        border-radius: 12px;
        padding: 10px;
    }

    /* Primary Analyse button */

    div.stButton > button[kind="primary"],
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        background: linear-gradient(
            100deg,
            #7138d5,
            #4820a5
        );
        color: #ffffff !important;
        border: none;
        border-radius: 12px;
        min-height: 58px;
        font-size: 18px;
        font-weight: 750;
        letter-spacing: 0.3px;
        box-shadow: 0 5px 15px rgba(95, 47, 190, 0.22);
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover p,
    div.stButton > button[kind="primary"]:hover span {
        background: linear-gradient(
            100deg,
            #824ce8,
            #5927bd
        );
        color: #ffffff !important;
        box-shadow: 0 7px 20px rgba(95, 47, 190, 0.32);
        transform: translateY(-2px);
    }

    div.stButton > button[kind="primary"]:focus {
        color: #ffffff !important;
        border: 2px solid #a78bfa;
    }

    /* Report headings */

    .report-heading {
        color: #21145c;
        font-size: 29px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 18px;
    }

    /* General text */

    p {
        color: #494766;
    }

    /* Divider */

    hr {
        border-color: #e8e1f5;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #85819e;
        font-size: 12px;
        margin-top: 35px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. APPLICATION TITLE
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🎯 HireSense AI
    </div>

    <div class="main-subtitle">
        AI-Powered Resume Screening & Candidate Matching
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 6. FILE UPLOAD SECTION
# ============================================================

jd_column, resume_column = st.columns(2, gap="large")


# ------------------------------------------------------------
# JOB DESCRIPTION UPLOAD
# ------------------------------------------------------------

with jd_column:

    with st.container(border=True):

        st.markdown(
            "### 📄 Upload Job Description"
        )

        st.caption(
            "Supported formats: TXT, MD"
        )

        jd_file = st.file_uploader(
            "Choose Job Description",
            type=["txt", "md"],
            key="jd_upload"
        )


# ------------------------------------------------------------
# CANDIDATE RESUME UPLOAD
# ------------------------------------------------------------

with resume_column:

    with st.container(border=True):

        st.markdown(
            "### 👥 Upload Candidate Resumes"
        )

        st.caption(
            "Supported format: PDF (Multiple files)"
        )

        resume_files = st.file_uploader(
            "Choose Candidate Resumes",
            type=["pdf"],
            accept_multiple_files=True,
            key="resume_upload"
        )


# ============================================================
# 7. UPLOAD STATUS
# ============================================================

if jd_file is not None:

    st.success(
        f"Job Description uploaded: {jd_file.name}"
    )

if resume_files:

    st.success(
        f"{len(resume_files)} candidate resume(s) uploaded successfully."
    )


# ============================================================
# 8. ANALYSE CANDIDATES BUTTON
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

button_column1, button_column2, button_column3 = st.columns(
    [1, 2, 1]
)

with button_column2:

    analyse_button = st.button(
        "✨ Analyse Candidates",
        type="primary",
        use_container_width=True
    )


# ============================================================
# END OF PART 1
# PART 2 WILL CONTAIN BACKEND INTEGRATION
# ============================================================


# ============================================================
# HIRESENSE AI
# PART 2 OF 3
# Backend Integration and Recruitment Pipeline
# ============================================================


# ============================================================
# 9. BACKEND INTEGRATION
# ============================================================

if analyse_button:

    # Validate uploaded files

    if jd_file is None:

        st.warning(
            "Please upload a Job Description first."
        )

    elif not resume_files:

        st.warning(
            "Please upload at least one candidate resume."
        )

    else:

        # Clear previous results before new analysis

        st.session_state.pipeline_results = None

        st.session_state.analysis_started = False

        try:

            with st.spinner(
                "AI is analysing the job description and candidate resumes. "
                "Please wait..."
            ):

                # Create temporary directory

                with tempfile.TemporaryDirectory() as temp_dir:

                    temp_path = Path(temp_dir)

                    # ----------------------------------------
                    # Save Job Description
                    # ----------------------------------------

                    jd_extension = Path(jd_file.name).suffix.lower()

                    jd_path = (
                        temp_path / f"job_description{jd_extension}"
                    )

                    jd_path.write_bytes(
                        jd_file.getvalue()
                    )

                    # ----------------------------------------
                    # Save Candidate Resumes
                    # ----------------------------------------

                    resume_paths = []

                    for index, resume_file in enumerate(
                        resume_files,
                        start=1
                    ):

                        resume_name = Path(resume_file.name).name

                        resume_path = (
                            temp_path / f"{index}_{resume_name}"
                        )

                        resume_path.write_bytes(
                            resume_file.getvalue()
                        )

                        resume_paths.append(
                            str(resume_path)
                        )

                    # ----------------------------------------
                    # Run Recruitment Pipeline
                    # ----------------------------------------

                    results = run_recruitment_pipeline(
                        jd_file_path=str(jd_path),
                        resume_file_paths=resume_paths
                    )

                    # Save pipeline results

                    st.session_state.pipeline_results = results

                    st.session_state.analysis_started = True

            st.success(
                "Candidate analysis completed successfully!"
            )

        except Exception as error:

            st.session_state.pipeline_results = None

            st.session_state.analysis_started = False

            st.error(
                f"An error occurred during candidate analysis: {error}"
            )


# ============================================================
# 10. LOAD PIPELINE RESULTS
# ============================================================

results = st.session_state.pipeline_results


# ============================================================
# END OF PART 2
# PART 3 WILL CONTAIN THE RECRUITMENT REPORT
# ============================================================



# ============================================================
# HIRESENSE AI
# PART 3 OF 3
# Recruiter Dashboard and Candidate Reports
# ============================================================


# ============================================================
# 11. HELPER FUNCTIONS
# ============================================================

def display_skill_chips(skills, color="#e8f5e9", text_color="#187344"):

    if not skills:
        st.caption("None identified.")
        return

    # Remove duplicate skills
    skills = list(dict.fromkeys(skills))

    chips_html = "".join(
        f"""
        <span style="
            display:inline-block;
            background:{color};
            color:{text_color};
            padding:5px 11px;
            margin:3px 5px 3px 0;
            border-radius:20px;
            font-size:13px;
            font-weight:600;
            white-space:nowrap;
        ">{skill}</span>
        """
        for skill in skills
    )

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-wrap:wrap;
            align-items:center;
            gap:2px;
            line-height:1.8;
        ">
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def format_education(education_list):

    if not education_list:
        st.caption("No education information available.")
        return

    for index, education in enumerate(education_list, start=1):

        degree = education.get("degree") or "Not available"
        institution = education.get("institution") or "Not available"
        field = education.get("field_of_study") or "Not available"
        year = education.get("graduation_year") or "Not available"

        with st.expander(f"🎓 {degree}", expanded=(index == 1)):

            st.write(f"**Institution:** {institution}")
            st.write(f"**Specialization:** {field}")
            st.write(f"**Graduation Year:** {year}")


def format_work_experience(experience_list):

    if not experience_list:
        st.caption("No work experience information available.")
        return

    for index, experience in enumerate(experience_list, start=1):

        company = experience.get("company") or "Not available"
        title = experience.get("job_title") or "Not available"
        start = experience.get("start_date") or "Not available"
        end = experience.get("end_date") or "Not available"

        with st.expander(
            f"💼 {title} | {company}",
            expanded=(index == 1)
        ):

            st.write(f"**Duration:** {start} to {end}")

            descriptions = experience.get("description", [])

            if descriptions:

                st.write("**Responsibilities:**")

                for description in descriptions:
                    st.write(f"- {description}")


# ============================================================
# 12. DISPLAY RECRUITMENT REPORT
# ============================================================

if results:

    st.divider()

    st.markdown(
        '<div class="report-heading">📋 Recruitment Report</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Resumes",
            results.get("total_resumes_submitted", 0)
        )

    with col2:
        st.metric(
            "Candidates Evaluated",
            results.get("total_candidates_evaluated", 0)
        )

    with col3:
        st.metric(
            "Duplicates Reused",
            results.get("total_duplicates_reused", 0)
        )

    with col4:
        st.metric(
            "Processing Errors",
            results.get("total_processing_errors", 0)
        )

    st.markdown(
        f"**Job Title:** {results.get('job_title', 'Not available')}"
    )

    st.divider()

    # --------------------------------------------------------
    # CANDIDATE RANKINGS
    # --------------------------------------------------------

    st.subheader("🏆 Candidate Rankings")

    ranked_candidates = results.get("ranked_candidates", [])

    if ranked_candidates:

        candidate_rows = []

        for candidate in ranked_candidates:

            match_result = candidate.get("match_result", {})

            education_status = match_result.get("education_eligible")

            if education_status is True:
                eligibility = "Eligible"
            elif education_status is False:
                eligibility = "Not Eligible"
            else:
                eligibility = "Not Verified"

            candidate_rows.append({

                "Rank": candidate.get("rank"),

                "Candidate": candidate.get("candidate_name"),

                "Match Score": (
                    f"{match_result.get('overall_match_score', 0):.2f}%"
                ),

                "Required Skills": (
                    f"{match_result.get('required_skill_score', 0):.2f}%"
                ),

                "Preferred Skills": (
                    f"{match_result.get('preferred_skill_score', 0):.2f}%"
                ),

                "Education": eligibility

            })

        st.dataframe(
            candidate_rows,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ----------------------------------------------------
        # INDIVIDUAL CANDIDATE REPORT
        # ----------------------------------------------------

        st.subheader("👤 Individual Candidate Report")

        candidate_options = {

            (
                f"Rank {candidate.get('rank')} - "
                f"{candidate.get('candidate_name')}"
            ): candidate

            for candidate in ranked_candidates
        }

        selected_label = st.selectbox(
            "Select a candidate",
            options=list(candidate_options.keys())
        )

        selected_candidate = candidate_options[selected_label]

        profile = selected_candidate.get("profile", {})

        match_result = selected_candidate.get("match_result", {})

        candidate_id = selected_candidate.get("candidate_id")

        # ----------------------------------------------------
        # CANDIDATE OVERVIEW
        # ----------------------------------------------------

        st.markdown("### Candidate Overview")

        overview_col1, overview_col2 = st.columns(2)

        with overview_col1:

            st.write(
                f"**Name:** {profile.get('full_name') or 'Not available'}"
            )

            st.write(
                f"**Email:** {profile.get('email') or 'Not available'}"
            )

            st.write(
                f"**Phone:** {profile.get('phone') or 'Not available'}"
            )

        with overview_col2:

            st.write(
                f"**Location:** {profile.get('location') or 'Not available'}"
            )

            st.write(
                f"**Rank:** {selected_candidate.get('rank')}"
            )

            education_eligible = match_result.get("education_eligible")

            if education_eligible is True:
                st.success("Education: Eligible")

            elif education_eligible is False:
                st.error("Education: Not Eligible")

            else:
                st.warning("Education: Not Verified")

        # ----------------------------------------------------
        # OVERALL MATCH SCORE
        # ----------------------------------------------------

        overall_score = float(
            match_result.get("overall_match_score", 0) or 0
        )

        st.metric(
            "Overall Match Score",
            f"{overall_score:.2f}%"
        )

        st.progress(
            min(max(overall_score / 100, 0.0), 1.0)
        )

        # ----------------------------------------------------
        # MATCHING SCORE BREAKDOWN
        # ----------------------------------------------------

        st.markdown("### Matching Score Breakdown")

        score_col1, score_col2, score_col3 = st.columns(3)

        with score_col1:

            st.metric(
                "Keyword Match",
                f"{match_result.get('keyword_match_score', 0):.2f}%"
            )

        with score_col2:

            st.metric(
                "Semantic Match",
                f"{match_result.get('semantic_match_score', 0):.2f}%"
            )

        with score_col3:

            experience_score = match_result.get("experience_score")

            st.metric(
                "Experience Score",
                (
                    f"{experience_score:.2f}%"
                    if experience_score is not None
                    else "Not evaluated"
                )
            )

        # ----------------------------------------------------
        # COMPACT SKILLS ANALYSIS
        # ----------------------------------------------------

        st.markdown("### Skills Analysis")

        matched_skills = match_result.get("matched_skills", [])

        missing_skills = match_result.get(
            "missing_required_skills", []
        )

        preferred_skills = match_result.get(
            "matched_preferred_skills", []
        )

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:

            st.markdown(
                f"**✅ Matched Required Skills ({len(matched_skills)})**"
            )

            display_skill_chips(
                matched_skills,
                color="#dcfce7",
                text_color="#166534"
            )

        with skill_col2:

            st.markdown(
                f"**❌ Missing Required Skills ({len(missing_skills)})**"
            )

            display_skill_chips(
                missing_skills,
                color="#fee2e2",
                text_color="#991b1b"
            )

        st.markdown(
            f"**⭐ Matched Preferred Skills ({len(preferred_skills)})**"
        )

        display_skill_chips(
            preferred_skills,
            color="#ede9fe",
            text_color="#5b21b6"
        )

        # ----------------------------------------------------
        # OTHER CANDIDATE SKILLS
        # ----------------------------------------------------

        candidate_skills = profile.get("technical_skills", [])

        with st.expander(
            f"💡 Candidate Technical Skills ({len(candidate_skills)})"
        ):

            display_skill_chips(
                candidate_skills,
                color="#dbeafe",
                text_color="#1e40af"
            )

        # ----------------------------------------------------
        # MATCHING EVIDENCE
        # ----------------------------------------------------

        matching_evidence = match_result.get(
            "matching_evidence", []
        )

        if matching_evidence:

            with st.expander(
                f"🔎 Matching Evidence ({len(matching_evidence)})"
            ):

                for evidence in matching_evidence:
                    st.write(f"- {evidence}")

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        with st.expander("🎓 Education", expanded=False):

            format_education(
                profile.get("education", [])
            )

        # ----------------------------------------------------
        # WORK EXPERIENCE
        # ----------------------------------------------------

        with st.expander("💼 Work Experience", expanded=False):

            format_work_experience(
                profile.get("work_experience", [])
            )

        # ----------------------------------------------------
        # PROJECTS
        # ----------------------------------------------------

        projects = profile.get("projects", [])

        if projects:

            with st.expander(
                f"🚀 Projects ({len(projects)})",
                expanded=False
            ):

                for project in projects:

                    st.markdown(
                        f"**{project.get('project_name') or 'Project'}**"
                    )

                    st.write(
                        project.get("description")
                        or "No description available."
                    )

                    st.caption(
                        "Technologies: "
                        + (
                            project.get("technologies")
                            or "Not available"
                        )
                    )

        # ----------------------------------------------------
        # GENERATED CANDIDATE REPORT
        # ----------------------------------------------------

        candidate_report = next(

            (
                report

                for report in results.get("candidate_reports", [])

                if report.get("candidate_id") == candidate_id
            ),

            None
        )

        if candidate_report:

            with st.expander(
                "📑 Generated Candidate Report",
                expanded=False
            ):

                report_text = candidate_report.get("report_text", "")

                if report_text:

                    st.text_area(
                        "Evaluation Report",
                        value=report_text,
                        height=220,
                        disabled=True
                    )

                    st.download_button(
                        "⬇️ Download Candidate Report",
                        data=report_text,
                        file_name=f"candidate_report_{candidate_id}.txt",
                        mime="text/plain"
                    )

    else:

        st.warning(
            "No candidates were successfully evaluated."
        )

    # --------------------------------------------------------
    # PROCESSING ERRORS
    # --------------------------------------------------------

    processing_errors = results.get("processing_errors", [])

    if processing_errors:

        with st.expander("⚠️ Processing Errors"):

            for error in processing_errors:

                st.write(
                    f"**File:** {error.get('file_name', 'Unknown')}"
                )

                st.write(
                    f"**Error:** {error.get('error', 'Unknown error')}"
                )

    # --------------------------------------------------------
    # LEGACY SKIPPED RESUMES
    # --------------------------------------------------------

    skipped_resumes = results.get("skipped_resumes", [])

    if skipped_resumes:

        with st.expander("Previously Skipped Resumes"):

            for item in skipped_resumes:

                st.write(
                    f"{item.get('file_name')} - "
                    f"{item.get('reason')}"
                )


# ============================================================
# 13. FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        HireSense AI | Intelligent Resume Screening
        <br>
        Powered by Gemini, Sentence Transformers and ChromaDB
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# END OF PART 3
# HIRESENSE AI APPLICATION COMPLETE
# ============================================================
