"""
about.py
--------------------------------------------------------------------------------
About Page for AI Resume Analyzer.
Provides architecture breakdown, scoring formulas, tech stack,
and portfolio documentation in a polished SaaS design system.
--------------------------------------------------------------------------------
"""

import streamlit as st


def render_about_page():
    # Header
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <div style="display: inline-block; padding: 4px 12px; background: #eef2ff; color: #4f46e5; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                System Architecture & Specifications
            </div>
            <h1 style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-bottom: 0.4rem; letter-spacing: -0.02em;">
                About AI Resume Analyzer
            </h1>
            <p style="font-size: 1.05rem; color: #64748b; margin: 0; line-height: 1.5;">
                A production-grade, explainable resume evaluation engine engineered with Python, Streamlit, PyMuPDF, RapidOCR, scikit-learn, and SQLite.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.8, 1.2], gap="large")

    with col1:
        # Mission Card
        st.markdown("""
            <div class="saas-card-accent" style="margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#4f46e5;"></span>
                    Engineering Mission & Purpose
                </h3>
                <p style="color: #475569; line-height: 1.6; font-size: 0.95rem; margin-bottom: 0.75rem;">
                    Modern technical hiring relies heavily on automated Applicant Tracking Systems (ATS) and recruitment algorithms. Qualified candidates are frequently filtered out due to non-standard resume formats, missing industry-standard taxonomy keywords, or vague impact metrics.
                </p>
                <p style="color: #475569; line-height: 1.6; font-size: 0.95rem; margin-bottom: 0;">
                    <b>AI Resume Analyzer</b> was built to eliminate the hiring "black box" by offering <b>100% transparent, explainable, and actionable evaluations</b>:
                </p>
                <ul style="color: #475569; line-height: 1.6; font-size: 0.92rem; padding-left: 1.25rem; margin-top: 0.5rem; margin-bottom: 0;">
                    <li><b>ATS Parsing Score:</b> Audits structural sections, contact essentials, quantifiable metrics, and readability.</li>
                    <li><b>Job Match Index:</b> Measures exact semantic and technical taxonomy alignment against target job descriptions.</li>
                    <li><b>Skill Gap Analysis:</b> Identifies missing hard technologies, tools, and methodologies required by employers.</li>
                    <li><b>Interview Preparation:</b> Generates customized behavioral and technical interview questions with high-impact answering strategies.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        # Pipeline Architecture Card
        st.markdown("""
            <div class="saas-card" style="margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 1rem;">
                    System Architecture & Pipeline
                </h3>
                
                <div style="display: flex; flex-direction: column; gap: 14px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: #eef2ff; color: #4f46e5; font-weight: 700; font-size: 0.8rem; border-radius: 6px; padding: 4px 8px; min-width: 28px; text-align: center;">1</div>
                        <div>
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">Dual-Engine PDF Ingestion (PyMuPDF + RapidOCR Fallback)</div>
                            <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">Extracts selectable text via PyMuPDF. If a scanned document or flat image is detected, it automatically renders high-DPI page bitmaps and performs OCR text recovery.</div>
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: #eef2ff; color: #4f46e5; font-weight: 700; font-size: 0.8rem; border-radius: 6px; padding: 4px 8px; min-width: 28px; text-align: center;">2</div>
                        <div>
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">Boundary-Aware Skill Taxonomy Engine</div>
                            <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">Extracts 100+ technical and soft skills across 7 specialized domains using word-boundary regular expressions to prevent substring collisions (e.g., distinguishing 'Go' or 'C' from natural language).</div>
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: #eef2ff; color: #4f46e5; font-weight: 700; font-size: 0.8rem; border-radius: 6px; padding: 4px 8px; min-width: 28px; text-align: center;">3</div>
                        <div>
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">Vector NLP & Semantic Cosine Similarity (scikit-learn)</div>
                            <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">Converts cleaned resume text and job specifications into TF-IDF unigram/bigram vectors to compute cosine alignment across technical phrasing.</div>
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: #eef2ff; color: #4f46e5; font-weight: 700; font-size: 0.8rem; border-radius: 6px; padding: 4px 8px; min-width: 28px; text-align: center;">4</div>
                        <div>
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">Explainable Composite Scoring Formula</div>
                            <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">
                                <b>Job Match Score</b> = 60% Skill Overlap + 40% TF-IDF Cosine Similarity.<br>
                                <b>ATS Score</b> = Sections (30%) + Contact (15%) + Action & Metrics (20%) + Density (20%) + Length (15%).
                            </div>
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: #eef2ff; color: #4f46e5; font-weight: 700; font-size: 0.8rem; border-radius: 6px; padding: 4px 8px; min-width: 28px; text-align: center;">5</div>
                        <div>
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">Dual-Mode AI Engine (Local NLP + LLM API)</div>
                            <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">Operates seamlessly offline using rule-based NLP algorithms. When an LLM API key is configured, it enriches output with generative interview scenarios and bullet rewrites.</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Tech Stack Card
        st.markdown("""
            <div class="saas-card" style="margin-bottom: 1.5rem;">
                <h4 style="margin-top: 0; font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem;">
                    Technology Stack
                </h4>
                
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.88rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">Core Language</span>
                        <span style="font-weight: 600; color: #0f172a;">Python 3.11+</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">Web Framework</span>
                        <span style="font-weight: 600; color: #0f172a;">Streamlit</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">PDF Engine</span>
                        <span style="font-weight: 600; color: #0f172a;">PyMuPDF (fitz)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">OCR Engine</span>
                        <span style="font-weight: 600; color: #0f172a;">RapidOCR / ONNX</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">NLP & ML</span>
                        <span style="font-weight: 600; color: #0f172a;">scikit-learn (TF-IDF)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">Data Processing</span>
                        <span style="font-weight: 600; color: #0f172a;">Pandas & NumPy</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">Interactive Charts</span>
                        <span style="font-weight: 600; color: #0f172a;">Plotly Graph Objects</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="color: #64748b;">Persistence</span>
                        <span style="font-weight: 600; color: #0f172a;">SQLite 3</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 2px;">
                        <span style="color: #64748b;">Optional AI</span>
                        <span style="font-weight: 600; color: #0f172a;">Google Gemini / OpenAI</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Portfolio Credentials Card
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #dbeafe; border-radius: 12px; padding: 18px; margin-bottom: 1.5rem;">
                <h4 style="margin-top: 0; font-size: 1rem; font-weight: 700; color: #1e40af; margin-bottom: 0.5rem;">
                    Portfolio Credentials
                </h4>
                <p style="font-size: 0.86rem; color: #1e3a8a; line-height: 1.5; margin-bottom: 0;">
                    Engineered to showcase production-level software craftsmanship: modular service layers, strict regex tokenization, resilient error boundaries, dual-engine fallback, and clean visual design.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Pedagogical Disclaimer
        st.markdown("""
            <div style="background: #fffbeb; border: 1px solid #fef3c7; border-radius: 12px; padding: 16px;">
                <h5 style="margin-top: 0; font-size: 0.88rem; font-weight: 700; color: #92400e; margin-bottom: 0.4rem;">
                    Educational Disclaimer
                </h5>
                <p style="font-size: 0.8rem; color: #78350f; line-height: 1.4; margin-bottom: 0;">
                    The "Estimated ATS Score" is an algorithmic estimation based on established recruiting conventions. It is not affiliated with, licensed by, or representative of proprietary ATS vendors (e.g. Workday, Greenhouse, Taleo).
                </p>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_about_page()
else:
    render_about_page()
