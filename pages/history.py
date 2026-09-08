"""
history.py
--------------------------------------------------------------------------------
AI Resume Analyzer
AI-Powered Resume Analysis & Job Matching

Evaluation History Page with Modern SaaS UI/UX.
Displays past evaluations from the local SQLite database, allows viewing
stored metrics & skills, deleting specific records, or exporting data to CSV.
--------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from database.database import get_all_analyses, delete_analysis, clear_all_analyses
from utils.helpers import render_skill_badges_html, get_score_color


def render_history_page():
    # Page Header
    st.markdown("""
        <div style="margin-bottom: 1.6rem;">
            <h2 style="margin: 0 0 4px 0; font-size: 1.85rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">
                Evaluation History
            </h2>
            <p style="margin: 0; color: #64748b; font-size: 0.98rem;">
                Review, compare, and manage historical candidate evaluations stored in your local SQLite database.
            </p>
        </div>
    """, unsafe_allow_html=True)

    analyses = get_all_analyses()

    if not analyses:
        st.markdown("""
            <div class="saas-card" style="text-align: center; padding: 40px 20px;">
                <h4 style="margin: 0 0 8px 0; color: #0f172a;">No Saved Evaluations Found</h4>
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">
                    You haven't run any resume evaluations yet. Head over to the Analyze page to evaluate your first resume.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start First Analysis", type="primary"):
            if hasattr(st, "switch_page"):
                st.switch_page("pages/analyze.py")
        return

    # Top Action Bar
    top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
    with top_col1:
        st.markdown(f"Showing **{len(analyses)}** saved evaluation records.")

    with top_col2:
        # Prepare CSV export
        export_df = pd.DataFrame([{
            "ID": a["id"],
            "Timestamp": a["timestamp"],
            "Resume File": a["resume_filename"],
            "Job Title": a["job_title"],
            "ATS Score": a["ats_score"],
            "Match Score": a["match_score"],
            "Matched Skills Count": len(a["matching_skills"]),
            "Missing Skills Count": len(a["missing_skills"]),
            "Summary": a["summary"]
        } for a in analyses])
        csv_bytes = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export to CSV",
            data=csv_bytes,
            file_name="resume_match_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    with top_col3:
        if st.button("Clear All History", use_container_width=True):
            clear_all_analyses()
            st.toast("All history records cleared!", icon="🧹")
            st.rerun()

    st.divider()

    # Iterate through analyses and display in clean SaaS cards
    for item in analyses:
        item_id = item["id"]
        ats_col = get_score_color(item["ats_score"])
        match_col = get_score_color(item["match_score"])

        with st.expander(
            f"{item['timestamp']}  |  {item['resume_filename']}  |  {item['job_title'][:45]}",
            expanded=False
        ):
            c1, c2, c3, c4 = st.columns([1, 1, 2, 1])

            with c1:
                st.metric(
                    "Estimated ATS Score",
                    f"{item['ats_score']}/100"
                )
            with c2:
                st.metric(
                    "Job Match Score",
                    f"{item['match_score']}%"
                )
            with c3:
                st.markdown(f"**Target Role:** {item['job_title']}")
                if item.get("summary"):
                    st.caption(f"**Summary:** {item['summary'][:180]}...")
            with c4:
                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                if st.button("Delete", key=f"del_{item_id}", type="secondary", use_container_width=True):
                    delete_analysis(item_id)
                    st.toast(f"Deleted evaluation #{item_id}", icon="🗑️")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            sk_col1, sk_col2, sk_col3 = st.columns(3)
            with sk_col1:
                st.markdown(f"**Matching Skills ({len(item['matching_skills'])})**")
                st.markdown(render_skill_badges_html(item["matching_skills"], "matching"), unsafe_allow_html=True)
            with sk_col2:
                st.markdown(f"**Missing Skills ({len(item['missing_skills'])})**")
                st.markdown(render_skill_badges_html(item["missing_skills"], "missing"), unsafe_allow_html=True)
            with sk_col3:
                st.markdown(f"**Additional Skills ({len(item['additional_skills'])})**")
                st.markdown(render_skill_badges_html(item["additional_skills"], "additional"), unsafe_allow_html=True)


if __name__ == "__main__":
    render_history_page()
else:
    render_history_page()
