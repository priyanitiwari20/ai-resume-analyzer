"""
dashboard.py
--------------------------------------------------------------------------------
AI Resume Analyzer
AI-Powered Resume Analysis & Job Matching

Landing & Dashboard Page.
Presents the 4-step workflow, aggregate analytics from past evaluations,
benchmark skill distribution, and immediate CTA to start a new analysis.
--------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from database.database import get_all_analyses
from utils.helpers import create_skill_radar_chart, get_score_color


def render_dashboard_page():
    # 1. Sleek SaaS Hero Banner
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid #312e81; padding: 2.2rem 2.4rem; border-radius: 14px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                <span style="background: rgba(99, 102, 241, 0.25); border: 1px solid #818cf8; color: #c7d2fe; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">Enterprise Intelligence</span>
            </div>
            <h1 style="color: #ffffff; margin-bottom: 0.4rem; font-size: 2.25rem; font-weight: 800; letter-spacing: -0.02em;">AI Resume Analyzer</h1>
            <p style="font-size: 1.15rem; color: #cbd5e1; font-weight: 400; margin-bottom: 1.5rem; max-width: 680px;">
                AI-Powered Resume Analysis & Job Matching. Evaluate your resume formatting, calculate job alignment, and eliminate skill gaps.
            </p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <span style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); padding: 5px 13px; border-radius: 20px; font-size: 0.84rem; color: #f1f5f9;">Estimated ATS Scoring</span>
                <span style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); padding: 5px 13px; border-radius: 20px; font-size: 0.84rem; color: #f1f5f9;">TF-IDF & Skill Gap Matching</span>
                <span style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); padding: 5px 13px; border-radius: 20px; font-size: 0.84rem; color: #f1f5f9;">OCR Scanned PDF Fallback</span>
                <span style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); padding: 5px 13px; border-radius: 20px; font-size: 0.84rem; color: #f1f5f9;">Local NLP + Optional AI</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 4-Step Interactive Workflow Cards
    st.markdown("### How It Works")
    st.caption("A structured, transparent pipeline from resume document upload to tailored interview preparation.")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("""
            <div class="saas-step-card">
                <div class="step-number">1</div>
                <h4 style="margin: 0 0 6px 0; font-size: 1rem; color: #0f172a;">Upload Resume</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.45;">
                    Upload any PDF resume. PyMuPDF extracts text, with automatic RapidOCR fallback for scanned images.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
            <div class="saas-step-card">
                <div class="step-number">2</div>
                <h4 style="margin: 0 0 6px 0; font-size: 1rem; color: #0f172a;">Add Job Description</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.45;">
                    Paste your target role requirements or upload a posting to extract required competencies and keywords.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with step3:
        st.markdown("""
            <div class="saas-step-card">
                <div class="step-number">3</div>
                <h4 style="margin: 0 0 6px 0; font-size: 1rem; color: #0f172a;">Analyze Alignment</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.45;">
                    Computes explainable ATS formatting score and job match percentage via TF-IDF cosine similarity.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with step4:
        st.markdown("""
            <div class="saas-step-card">
                <div class="step-number">4</div>
                <h4 style="margin: 0 0 6px 0; font-size: 1rem; color: #0f172a;">Improve & Prepare</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.45;">
                    Get actionable bullet rewrites (STAR method), power action verbs, and tailored interview prep questions.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Quick-Start CTA Banner
    col_cta_text, col_cta_btn = st.columns([3, 1])
    with col_cta_text:
        st.markdown("#### Ready to benchmark your resume?")
        st.caption("Upload your PDF resume or try our ready-to-test demo data in one click.")
    with col_cta_btn:
        st.markdown("<div style='margin-top: 6px;'>", unsafe_allow_html=True)
        if st.button("Start Analysis", type="primary", use_container_width=True):
            if hasattr(st, "switch_page"):
                st.switch_page("pages/analyze.py")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # 4. Aggregate Analytics & Historical Records
    analyses = get_all_analyses()

    st.subheader("System Performance & Analytics")
    if analyses:
        total_count = len(analyses)
        avg_ats = round(sum(a["ats_score"] for a in analyses) / total_count, 1)
        avg_match = round(sum(a["match_score"] for a in analyses) / total_count, 1)
        top_match = max(a["match_score"] for a in analyses)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Analyses", total_count)
        with m2:
            st.metric("Avg Estimated ATS Score", f"{avg_ats}/100")
        with m3:
            st.metric("Avg Job Match Score", f"{avg_match}%")
        with m4:
            st.metric("Highest Match Recorded", f"{top_match}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Recent Analysis History")
        recent_data = []
        for a in analyses[:5]:
            recent_data.append({
                "Date": a["timestamp"],
                "Resume Document": a["resume_filename"],
                "Target Role": a["job_title"][:38] + ("..." if len(a["job_title"]) > 38 else ""),
                "ATS Score": f"{a['ats_score']}/100",
                "Job Match": f"{a['match_score']}%",
                "Matched Skills": len(a["matching_skills"]),
                "Missing Skills": len(a["missing_skills"])
            })
        st.dataframe(pd.DataFrame(recent_data), use_container_width=True)

    else:
        st.info("No evaluations recorded yet in local database. Click 'Start Analysis' above to evaluate your first resume!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Core Methodology & Benchmark Radar Section
    st.subheader("Dual-Engine Evaluation Methodology")
    col_feat1, col_feat2 = st.columns([1, 1])

    with col_feat1:
        st.markdown("""
        Our system employs an **explainable, dual-engine scoring framework**:
        
        1. **Estimated ATS-Style Score (0–100)**:
           - Evaluates section completeness (Experience, Education, Skills, Projects), contact details placement, power action verbs, quantifiable achievements, and page length suitability.
        
        2. **Job Match Score (0–100%)**:
           - **60% Weight**: Direct skill overlap across 7 technical and soft skill taxonomies.
           - **40% Weight**: TF-IDF (Term Frequency-Inverse Document Frequency) unigram and bigram cosine similarity.
        
        3. **Dual-Stage PDF Extraction**:
           - Native PyMuPDF text parsing for searchable documents.
           - Automatic 200 DPI bitmap rendering and RapidOCR extraction for scanned or image-based resumes.
        """)

    with col_feat2:
        # Sample benchmark radar visualization
        sample_resume_cat = {
            "Programming": ["Python", "SQL", "JavaScript"],
            "Web Development": ["HTML", "CSS", "FastAPI"],
            "Data & AI": ["Pandas", "NumPy", "Scikit-learn", "Machine Learning"],
            "Database": ["PostgreSQL", "SQLite"],
            "Cloud & DevOps": ["Docker", "Git"],
            "Tools & Platforms": ["VS Code", "Postman"],
            "Soft Skills": ["Problem Solving", "Communication", "Agile"]
        }
        sample_job_cat = {
            "Programming": ["Python", "SQL", "JavaScript"],
            "Web Development": ["React", "FastAPI"],
            "Data & AI": ["Machine Learning", "NLP", "Scikit-learn", "PyTorch"],
            "Database": ["PostgreSQL", "Redis"],
            "Cloud & DevOps": ["Docker", "AWS", "Git", "CI/CD"],
            "Tools & Platforms": ["Postman"],
            "Soft Skills": ["Communication", "Agile", "Teamwork"]
        }
        radar_fig = create_skill_radar_chart(sample_resume_cat, sample_job_cat)
        st.plotly_chart(radar_fig, use_container_width=True)
        st.caption("Benchmark Visualization: Candidate Skill Profile vs. Target Role Competency Requirements")


if __name__ == "__main__":
    render_dashboard_page()
else:
    render_dashboard_page()
