"""
analyze.py
--------------------------------------------------------------------------------
AI Resume Analyzer
AI-Powered Resume Analysis & Job Matching

Analyze Resume Page with Modern SaaS UI/UX.
Handles PDF resume upload, OCR fallback, job matching, explainable scoring,
3-way skill gaps, improvement recommendations, and AI interview prep.
--------------------------------------------------------------------------------
"""

import streamlit as st
import os
import io
from services.pdf_parser import extract_text_from_pdf
from services.resume_analyzer import analyze_resume_full
from services.job_matcher import match_resume_to_job
from services.ai_analyzer import analyze_with_ai_or_fallback
from database.database import save_analysis
from utils.helpers import (
    create_gauge_chart,
    create_skill_radar_chart,
    render_skill_badges_html,
    ensure_sample_pdf_exists,
    ensure_sample_scanned_pdf_exists,
    render_extraction_badge_html
)


def render_analyze_page():
    # Page Header
    st.markdown("""
        <div style="margin-bottom: 1.6rem;">
            <h2 style="margin: 0 0 4px 0; font-size: 1.85rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">
                Analyze Resume & Match Job
            </h2>
            <p style="margin: 0; color: #64748b; font-size: 0.98rem;">
                Upload your resume, supply the target job description, and receive an instant, explainable alignment report.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar: Clean Configuration & Demo Quick-Loads
    with st.sidebar:
        st.markdown("### Configuration")
        st.markdown("""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <p style="margin: 0; font-size: 0.8rem; color: #475569; line-height: 1.4;">
                    <strong>Dual-Engine Mode:</strong> An API key is optional. The application runs locally using rule-based NLP and TF-IDF similarity.
                </p>
            </div>
        """, unsafe_allow_html=True)

        custom_api_key = st.text_input(
            "LLM API Key (Optional)",
            type="password",
            placeholder="Paste Gemini or OpenAI key...",
            help="Leave blank to use local rule-based NLP mode or your .env file."
        )

        st.divider()
        st.markdown("### Quick Test Datasets")
        st.caption("Load sample datasets to test the complete workflow instantly.")

        if st.button("Load Searchable PDF Resume", use_container_width=True):
            sample_txt_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_resume.txt")
            if os.path.exists(sample_txt_path):
                with open(sample_txt_path, "r", encoding="utf-8") as f:
                    st.session_state["resume_text_input"] = f.read()
                    st.session_state["resume_filename"] = "Alex_Rivera_Sample_Resume.pdf"
                    st.session_state["extraction_method"] = "normal"
                    st.session_state["is_scanned"] = False
                st.toast("Loaded searchable text resume!", icon="📄")

        if st.button("Load Scanned Image PDF Resume", use_container_width=True):
            scanned_pdf_path = ensure_sample_scanned_pdf_exists()
            with open(scanned_pdf_path, "rb") as f:
                scanned_bytes = f.read()
            with st.spinner("Processing scanned document with OCR Fallback Engine..."):
                extracted_txt, msg, meta = extract_text_from_pdf(scanned_bytes)
                st.session_state["resume_text_input"] = extracted_txt
                st.session_state["resume_filename"] = "Alex_Rivera_Scanned_Resume.pdf"
                st.session_state["extraction_method"] = meta.get("extraction_method", "ocr")
                st.session_state["is_scanned"] = True
                st.toast("Loaded scanned PDF via OCR Fallback!", icon="🔍")

        if st.button("Load Sample Job Description", use_container_width=True):
            sample_job_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_job.txt")
            if os.path.exists(sample_job_path):
                with open(sample_job_path, "r", encoding="utf-8") as f:
                    st.session_state["job_text_input"] = f.read()
                st.toast("Loaded sample job description!", icon="💼")

    # Layout: Two clean cards for inputs
    col1, col2 = st.columns(2)

    # Column 1: Resume Upload
    with col1:
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">1. Candidate Resume (PDF)</h3>
            </div>
        """, unsafe_allow_html=True)

        uploaded_pdf = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"],
            help="Upload your resume in standard or scanned PDF format. If no selectable text is found, RapidOCR will automatically trigger.",
            label_visibility="collapsed"
        )

        resume_text = st.session_state.get("resume_text_input", "")
        resume_filename = st.session_state.get("resume_filename", "Uploaded_Resume.pdf")
        pdf_metadata = {}

        if uploaded_pdf is not None:
            resume_filename = uploaded_pdf.name
            with st.spinner("Extracting text from PDF (with automatic OCR fallback)..."):
                extracted_txt, err, meta = extract_text_from_pdf(uploaded_pdf)
                pdf_metadata = meta
                method = meta.get("extraction_method", "normal")
                is_scanned = meta.get("is_scanned", False)
                st.session_state["extraction_method"] = method
                st.session_state["is_scanned"] = is_scanned

                if err:
                    if meta.get("ocr_applied"):
                        st.info(f"{err}")
                        resume_text = extracted_txt
                    elif meta.get("is_scanned"):
                        st.warning(err)
                        resume_text = extracted_txt
                    else:
                        st.error(f"{err}")
                        resume_text = ""
                else:
                    resume_text = extracted_txt

                st.session_state["resume_text_input"] = resume_text
                st.session_state["resume_filename"] = resume_filename

        # Resume Text Preview Expandable
        if resume_text:
            with st.expander("Preview Extracted Resume Text", expanded=False):
                ext_method = st.session_state.get("extraction_method", "normal")
                is_scan = st.session_state.get("is_scanned", False)
                st.markdown(render_extraction_badge_html(ext_method, is_scan), unsafe_allow_html=True)
                st.caption(f"Document: `{resume_filename}` | Characters: {len(resume_text)} | Words: {len(resume_text.split())}")
                st.text_area("Extracted Content", resume_text, height=160, disabled=True, label_visibility="collapsed")
        else:
            st.markdown("""
                <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; margin-top: 6px;">
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Upload a PDF resume or click a quick-load button in the sidebar.</p>
                </div>
            """, unsafe_allow_html=True)

    # Column 2: Target Job Description
    with col2:
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">2. Target Job Description</h3>
            </div>
        """, unsafe_allow_html=True)

        job_upload = st.file_uploader(
            "Upload Job Description (.txt or .pdf)",
            type=["txt", "pdf"],
            key="job_file_uploader",
            help="Optional: Upload job description file instead of pasting.",
            label_visibility="collapsed"
        )

        if job_upload is not None:
            if job_upload.name.endswith(".pdf"):
                extracted_job, j_err, _ = extract_text_from_pdf(job_upload)
                if not j_err:
                    st.session_state["job_text_input"] = extracted_job
            else:
                try:
                    job_str = job_upload.getvalue().decode("utf-8")
                    st.session_state["job_text_input"] = job_str
                except Exception:
                    pass

        default_job_val = st.session_state.get("job_text_input", "")
        job_description = st.text_area(
            "Paste Job Description Here",
            value=default_job_val,
            height=180,
            placeholder="Paste the target job description, requirements, and responsibilities here...",
            label_visibility="collapsed"
        )

        if job_description:
            st.caption(f"Job Description Length: {len(job_description.split())} words")

    st.markdown("<br>", unsafe_allow_html=True)

    # Big Prominent Primary Action Button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        analyze_clicked = st.button(
            "Analyze Resume & Match Job",
            type="primary",
            use_container_width=True
        )

    # Validation and Pipeline Execution
    if analyze_clicked:
        if not resume_text or len(resume_text.strip()) < 30:
            st.error("Please upload or provide a resume with readable text (at least 30 characters).")
            return

        if not job_description or len(job_description.strip()) < 30:
            st.error("Please enter a target job description (at least 30 characters).")
            return

        with st.spinner("Evaluating resume structure, matching competencies, and computing alignment scores..."):
            # 1. Full resume structure and ATS analysis
            resume_data = analyze_resume_full(resume_text)

            # 2. Job matching & TF-IDF similarity
            match_data = match_resume_to_job(resume_data, job_description)

            # 3. AI / Local Fallback Analysis
            ai_data = analyze_with_ai_or_fallback(resume_data, match_data, custom_api_key)

            # Extract short job title for storage
            job_lines = [l.strip() for l in job_description.split("\n") if l.strip()]
            job_title = job_lines[0][:50] if job_lines else "Target Job Position"

            # 4. Save analysis to SQLite database
            record_id = save_analysis(
                resume_filename=resume_filename,
                job_title=job_title,
                ats_score=resume_data["ats_score"],
                match_score=match_data["match_score"],
                matching_skills=match_data["skill_comparison"]["matching_skills"],
                missing_skills=match_data["skill_comparison"]["missing_skills"],
                additional_skills=match_data["skill_comparison"]["additional_skills"],
                summary=ai_data.get("summary", "")
            )

            # Store result in session state for UI persistence
            st.session_state["latest_results"] = {
                "record_id": record_id,
                "resume_data": resume_data,
                "match_data": match_data,
                "ai_data": ai_data,
                "job_title": job_title,
                "resume_filename": resume_filename,
                "extraction_method": st.session_state.get("extraction_method", "normal"),
                "is_scanned": st.session_state.get("is_scanned", False)
            }
            st.toast("Evaluation successfully completed and saved to history!", icon="✅")

    # Display Results Dashboard if available
    if "latest_results" in st.session_state:
        results = st.session_state["latest_results"]
        resume_data = results["resume_data"]
        match_data = results["match_data"]
        ai_data = results["ai_data"]
        skill_comp = match_data["skill_comparison"]

        st.divider()

        # Score Overview Section with Gauges & Engine Badge
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    <h3 style="margin:0 0 2px 0; font-size: 1.5rem; font-weight: 800; color:#0f172a;">Performance Dashboard</h3>
                    <p style="margin:0; color:#64748b; font-size:0.9rem;">High-level evaluation metrics, ATS estimate, and alignment scorecards.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        ext_method = results.get("extraction_method", "normal")
        is_scan = results.get("is_scanned", False)
        st.markdown(render_extraction_badge_html(ext_method, is_scan), unsafe_allow_html=True)

        # 4 Core KPI Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(
                label="Estimated ATS Score",
                value=f"{resume_data['ats_score']}/100",
                help="Heuristic evaluation based on formatting, structure, contact details, action verbs, and skill density."
            )
        with kpi2:
            st.metric(
                label="Job Match Score",
                value=f"{match_data['match_score']}%",
                help="Combined weighted score: 60% Skill Overlap + 40% TF-IDF Cosine Similarity."
            )
        with kpi3:
            st.metric(
                label="Matching Skills Found",
                value=len(skill_comp["matching_skills"]),
                delta=f"{round(skill_comp['overlap_score'])}% requirements covered",
                delta_color="normal"
            )
        with kpi4:
            st.metric(
                label="Missing Target Skills",
                value=len(skill_comp["missing_skills"]),
                delta=f"-{len(skill_comp['missing_skills'])} skill gaps" if skill_comp["missing_skills"] else "All matched",
                delta_color="inverse"
            )

        # Plotly Gauges
        gauge_col1, gauge_col2 = st.columns(2)
        with gauge_col1:
            fig_ats = create_gauge_chart(resume_data['ats_score'], "Estimated ATS Score", "Resume Formatting & Completeness")
            st.plotly_chart(fig_ats, use_container_width=True)
        with gauge_col2:
            fig_match = create_gauge_chart(match_data['match_score'], "Job Match Score", "Skill & Terminology Alignment")
            st.plotly_chart(fig_match, use_container_width=True)

        st.markdown("---")

        # 1. Skill Gap Analysis & Radar Breakdown
        st.markdown("### Skill Gap & Category Distribution")
        st.caption("Direct comparison between candidate competencies and target job requirements across 7 taxonomies.")

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"**Matching Skills ({len(skill_comp['matching_skills'])})**")
            st.caption("Competencies requested by employer that are present:")
            st.markdown(render_skill_badges_html(skill_comp["matching_skills"], "matching"), unsafe_allow_html=True)

        with sc2:
            st.markdown(f"**Missing Skills ({len(skill_comp['missing_skills'])})**")
            st.caption("Required competencies absent from your resume:")
            st.markdown(render_skill_badges_html(skill_comp["missing_skills"], "missing"), unsafe_allow_html=True)

        with sc3:
            st.markdown(f"**Additional Resume Skills ({len(skill_comp['additional_skills'])})**")
            st.caption("Extra technical proficiencies detected on your resume:")
            st.markdown(render_skill_badges_html(skill_comp["additional_skills"], "additional"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Skill Category Radar Breakdown")
        radar_fig = create_skill_radar_chart(
            resume_data["categorized_skills"],
            match_data["job_categorized_skills"]
        )
        st.plotly_chart(radar_fig, use_container_width=True)

        st.markdown("---")

        # 2. SECTION: Improvement Recommendations (Visibly rendered below radar chart)
        st.markdown("""
            <div style="margin-bottom: 12px;">
                <h3 style="margin: 0 0 2px 0; font-size: 1.45rem; font-weight: 800; color: #0f172a;">Improvement Recommendations</h3>
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Actionable, transparent guidance to optimize your resume for both ATS systems and human hiring managers.</p>
            </div>
        """, unsafe_allow_html=True)

        sug = match_data.get("suggestions", {})

        # Row A: Missing Skills & Skills Candidate Should Learn
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.markdown("""
                <div class="saas-card-accent">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Missing Skills & Target Keywords</h4>
                    <p style="margin:0 0 10px 0; font-size:0.85rem; color:#64748b;">High-impact keywords from the job description missing on your resume. Weave them in where true to your background:</p>
            """, unsafe_allow_html=True)
            if sug.get("missing_keywords"):
                st.markdown(render_skill_badges_html(sug["missing_keywords"], "missing"), unsafe_allow_html=True)
            else:
                st.success("No missing critical keywords detected!")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_rec2:
            st.markdown("""
                <div class="saas-card-accent">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Skills the Candidate Should Learn</h4>
                    <p style="margin:0 0 10px 0; font-size:0.85rem; color:#64748b;">Prioritized technical roadmap to eliminate your skill gap for this position:</p>
            """, unsafe_allow_html=True)
            if sug.get("skills_to_learn"):
                for item in sug["skills_to_learn"]:
                    st.markdown(f"- {item}")
            else:
                st.info("Your skill set is already well aligned with the stated requirements.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row B: ATS Optimization & Formatting/Readability
        col_rec3, col_rec4 = st.columns(2)
        with col_rec3:
            st.markdown("""
                <div class="saas-card">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">ATS Optimization Suggestions</h4>
            """, unsafe_allow_html=True)
            for item in sug.get("ats_optimization", []):
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_rec4:
            st.markdown("""
                <div class="saas-card">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Resume Formatting & Readability</h4>
            """, unsafe_allow_html=True)
            for item in sug.get("formatting_readability", []):
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row C: Project Descriptions & Experience Bullet Points
        col_rec5, col_rec6 = st.columns(2)
        with col_rec5:
            st.markdown("""
                <div class="saas-card">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Suggestions for Improving Project Descriptions</h4>
            """, unsafe_allow_html=True)
            for item in sug.get("project_descriptions", []):
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_rec6:
            st.markdown("""
                <div class="saas-card">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Experience Bullet Points (STAR & XYZ Formula)</h4>
            """, unsafe_allow_html=True)
            for item in sug.get("bullet_points", []):
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row D: Stronger Action Verbs
        st.markdown("""
            <div class="saas-card">
                <h4 style="margin:0 0 6px 0; font-size:1rem; color:#0f172a;">Stronger Action-Verb Suggestions</h4>
        """, unsafe_allow_html=True)
        for item in sug.get("action_verbs", []):
            st.markdown(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # 3. SECTION: AI Insights & Interview Prep (Visibly rendered below recommendations)
        st.markdown("""
            <div style="margin-bottom: 12px;">
                <h3 style="margin: 0 0 2px 0; font-size: 1.45rem; font-weight: 800; color: #0f172a;">AI Insights & Interview Prep</h3>
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Generative candidate profiling, tailored interview questions, and expert answering tips.</p>
            </div>
        """, unsafe_allow_html=True)

        provider = ai_data.get("provider_used", "Local Engine")
        if ai_data.get("is_ai_generated"):
            st.success(f"Powered by Generative AI: **{provider}**")
        else:
            st.info(f"**{provider}**: Running in local rule-based NLP mode. Add an API key in .env or the sidebar to enable generative AI insights.")

        # Candidate Summary & Overall Job-Fit Explanation
        st.markdown("#### Candidate Summary & Job-Fit Explanation")
        summary_text = ai_data.get("summary", "Candidate profile evaluated against target requirements.")
        st.write(summary_text)

        fit_verdict = ai_data.get("job_fit_verdict", "Evaluated fit.")
        st.info(f"**Target Role Alignment:** {fit_verdict}")

        # Strengths & Weaknesses in Side-by-Side Cards
        col_str, col_weak = st.columns(2)
        with col_str:
            st.markdown("""
                <div class="saas-card" style="border-left: 3px solid #10b981;">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#065f46;">Resume Strengths</h4>
            """, unsafe_allow_html=True)
            strengths_list = ai_data.get("strengths", [])
            if strengths_list:
                for s in strengths_list:
                    st.markdown(f"- {s}")
            else:
                st.write("- Solid foundational engineering profile detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_weak:
            st.markdown("""
                <div class="saas-card" style="border-left: 3px solid #f59e0b;">
                    <h4 style="margin:0 0 6px 0; font-size:1rem; color:#92400e;">Resume Weaknesses & Gaps</h4>
            """, unsafe_allow_html=True)
            weaknesses_list = ai_data.get("weaknesses", [])
            if weaknesses_list:
                for w in weaknesses_list:
                    st.markdown(f"- {w}")
            else:
                st.write("- Minor opportunities for closer keyword tailoring.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 5–10 Interview Questions with Short Guidance / Tips
        st.markdown("#### Tailored Interview Preparation Questions")
        st.caption("Custom technical and situational questions based on your resume qualifications and target job gaps:")

        questions_list = ai_data.get("interview_questions", [])
        if questions_list:
            for idx, q_item in enumerate(questions_list, 1):
                if isinstance(q_item, dict):
                    q_text = q_item.get("question", "Interview Question")
                    q_cat = q_item.get("category", "General Technical")
                    q_tip = q_item.get("tip", "Structure your answer using concrete examples and measurable results.")
                else:
                    q_text = str(q_item)
                    q_cat = "Technical Interview"
                    q_tip = "Structure your answer around a specific project, technical trade-offs, and measurable outcomes."

                with st.expander(f"Question #{idx} [{q_cat}]: {q_text[:75]}...", expanded=(idx <= 2)):
                    st.markdown(f"**Interview Question:**")
                    st.markdown(f"> *{q_text}*")
                    st.markdown(f"**Guidance & Tips for Answering:**")
                    st.markdown(f"{q_tip}")
        else:
            st.info("No interview questions generated.")

        st.markdown("---")

        # 4. Supplementary Expanders: Scoring Methodology & Raw Extracted Profile Details
        with st.expander("Scoring Methodology (Formulas & Component Weights)", expanded=False):
            st.markdown("""
            > [!NOTE]
            > **Educational Disclaimer**: This score is an explainable estimation designed to optimize your resume structure. It is not an official score from any commercial ATS vendor.
            """)
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("##### 1. Estimated ATS-Style Score (0–100)")
                ats_bd = resume_data["ats_breakdown"]
                st.markdown(f"""
                - **Section Completeness**: `{ats_bd.get('section_completeness', 0)} / 30 pts` (Experience, Education, Skills, Projects)
                - **Contact Details**: `{ats_bd.get('contact_information', 0)} / 15 pts` (Email, Phone, LinkedIn/GitHub)
                - **Action Verbs & Impact**: `{ats_bd.get('action_verbs_and_impact', 0)} / 20 pts` (Power verbs and quantified numbers)
                - **Skill Richness**: `{ats_bd.get('skill_richness', 0)} / 20 pts` (Density of recognized technical & soft skills)
                - **Formatting & Length**: `{ats_bd.get('formatting_and_length', 0)} / 15 pts` (Target word count: 350 - 950 words)
                - **Total Score**: **`{resume_data['ats_score']} / 100`**
                """)
            with col_s2:
                st.markdown("##### 2. Job Match Score (0–100%)")
                mb = match_data["match_breakdown"]
                st.markdown(f"""
                - **Skill Overlap Score**: `{mb['skill_overlap_score']}%`
                  *(Weight: 60% → Contributes `{round(0.60 * mb['skill_overlap_score'], 1)}%`)*
                - **TF-IDF Cosine Similarity**: `{mb['tfidf_similarity_score']}%`
                  *(Weight: 40% → Contributes `{round(0.40 * mb['tfidf_similarity_score'], 1)}%`)*
                - **Formula**: `(0.60 × Overlap) + (0.40 × TF-IDF Similarity)`
                - **Final Match Score**: **`{match_data['match_score']}%`**
                """)

        with st.expander("Extracted Resume Details & Parsed Structure", expanded=False):
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown("##### Contact Information")
                c_info = resume_data["contact_info"]
                st.write(f"- **Email**: {c_info['email'] or 'Not detected'}")
                st.write(f"- **Phone**: {c_info['phone'] or 'Not detected'}")
                st.write(f"- **LinkedIn**: {c_info['linkedin'] or 'Not detected'}")
                st.write(f"- **GitHub**: {c_info['github'] or 'Not detected'}")

                st.markdown("##### Education Detected")
                edu_list = resume_data.get("education", [])
                if edu_list:
                    for e in edu_list:
                        st.write(f"- {e}")
                else:
                    st.write("No standard degree patterns explicitly detected.")

            with p_col2:
                st.markdown("##### Experience Indicators")
                exp = resume_data["experience"]
                st.write(f"- **Estimated Experience**: ~{exp['estimated_years']} years detected")
                st.write(f"- **Roles Detected**: {', '.join(exp['job_titles_detected']) if exp['job_titles_detected'] else 'General Engineer'}")
                st.write(f"- **Quantified Metrics Found**: {exp['quantifiable_metrics_count']} metrics")
                st.write(f"- **Action Verbs Found**: {len(exp['action_verbs_found'])} distinct verbs")

                st.markdown("##### Resume Sections Status")
                for sec, status in resume_data["sections"].items():
                    icon = "Present" if status else "Missing"
                    st.write(f"- **{sec.capitalize()}**: {icon}")


if __name__ == "__main__":
    render_analyze_page()
else:
    render_analyze_page()
