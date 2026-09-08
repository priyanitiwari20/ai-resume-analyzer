"""
app.py
--------------------------------------------------------------------------------
AI Resume Analyzer
AI-Powered Resume Analysis & Job Matching

Main entrypoint, page routing, and modern SaaS design system.
To run:
    streamlit run app.py
--------------------------------------------------------------------------------
"""

import streamlit as st
from utils.helpers import ensure_sample_pdf_exists
from database.database import init_db

# 1. Global Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Comprehensive Modern SaaS Design System
st.markdown("""
<style>
    /* 1. Global Typography & Base Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0f172a;
        -webkit-font-smoothing: antialiased;
    }

    /* 2. Main Container Padding & Clean Background */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px;
    }

    /* 3. Metric Scorecards with SaaS Card Styling */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #64748b !important;
        margin-bottom: 4px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.2 !important;
    }

    /* 4. Primary & Secondary Button Styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 9px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #334155 !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: #94a3b8 !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* 5. Custom Card Classes */
    .saas-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }

    .saas-card-accent {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #4f46e5;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        height: 100%;
    }

    .saas-step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 22px 18px;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        height: 100%;
        transition: all 0.2s ease;
    }

    .saas-step-card:hover {
        border-color: #c7d2fe;
        transform: translateY(-3px);
        box-shadow: 0 6px 16px -2px rgba(79, 70, 229, 0.08);
    }

    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: #eef2ff;
        color: #4f46e5;
        font-weight: 700;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }

    /* 6. Expanders Styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
    }

    [data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 10px;
    }

    /* 7. Modern Sidebar Header */
    [data-testid="stSidebarHeader"] {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Initialize SQLite Database & Sample Artifacts
try:
    init_db()
    ensure_sample_pdf_exists()
except Exception as init_err:
    st.sidebar.warning(f"Initialization notice: {init_err}")

# 4. Modern Multi-Page Navigation Definition
pages = [
    st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True),
    st.Page("pages/analyze.py", title="Analyze Resume", icon="🔍"),
    st.Page("pages/history.py", title="History", icon="📜"),
    st.Page("pages/about.py", title="About", icon="ℹ️")
]

# Run the active page
navigation = st.navigation(pages)
navigation.run()
