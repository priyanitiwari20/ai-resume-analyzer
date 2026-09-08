"""
helpers.py
--------------------------------------------------------------------------------
Utility Functions & Plotly Chart Helpers with Modern SaaS Styling.
Provides clean UI helpers, badge generators, Plotly visualizations, and
built-in PDF resume generators for seamless testing.
--------------------------------------------------------------------------------
"""

import os
import pymupdf as fitz  # PyMuPDF engine
import plotly.graph_objects as go
from typing import Dict, List, Any


def get_score_color(score: float) -> str:
    """
    Returns an intuitive HEX color code based on the score (0-100).
    """
    if score >= 75:
        return "#10B981"  # Emerald Green
    elif score >= 50:
        return "#F59E0B"  # Amber Orange
    else:
        return "#EF4444"  # Rose Red


def create_gauge_chart(score: float, title: str, subtitle: str = "") -> go.Figure:
    """
    Creates an interactive, ultra-modern SaaS Plotly Gauge indicator.
    """
    color = get_score_color(score)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<span style='font-size:1.05rem; font-weight:600; color:#0f172a;'>{title}</span>"
                    f"<br><span style='font-size:0.75rem; font-weight:400; color:#64748b;'>{subtitle}</span>",
            'font': {'family': 'Inter, system-ui, sans-serif'}
        },
        number={
            'suffix': "%" if "Match" in title else "/100",
            'font': {'size': 34, 'family': 'Inter, system-ui, sans-serif', 'color': color}
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1", 'tickfont': {'size': 10, 'color': '#94a3b8'}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': "#f1f5f9",
            'borderwidth': 1,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.06)"},
                {'range': [50, 75], 'color': "rgba(245, 158, 11, 0.06)"},
                {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.06)"}
            ]
        }
    ))

    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif")
    )
    return fig


def create_skill_radar_chart(
    resume_categorized: Dict[str, List[str]],
    job_categorized: Dict[str, List[str]]
) -> go.Figure:
    """
    Creates an ultra-clean radar chart comparing Candidate Skills vs Job Requirements
    across skill categories with modern SaaS styling.
    """
    categories = [
        "Programming", "Web Development", "Data & AI",
        "Database", "Cloud & DevOps", "Tools & Platforms", "Soft Skills"
    ]

    resume_counts = [len(resume_categorized.get(cat, [])) for cat in categories]
    job_counts = [len(job_categorized.get(cat, [])) for cat in categories]

    # Close the radar loop
    radar_categories = categories + [categories[0]]
    r_resume = resume_counts + [resume_counts[0]]
    r_job = job_counts + [job_counts[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=r_resume,
        theta=radar_categories,
        fill='toself',
        name='Resume Profile',
        line=dict(color='#4f46e5', width=2.5),
        fillcolor='rgba(79, 70, 229, 0.18)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=r_job,
        theta=radar_categories,
        fill='toself',
        name='Target Job Requirements',
        line=dict(color='#10b981', width=2.5),
        fillcolor='rgba(16, 185, 129, 0.14)'
    ))

    max_count = max(max(resume_counts + job_counts + [3]), 5)

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(248, 250, 252, 0.8)",
            radialaxis=dict(
                visible=True,
                range=[0, max_count],
                tickfont=dict(size=10, color='#64748b'),
                gridcolor='#e2e8f0',
                linecolor='#cbd5e1'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, family='Inter, sans-serif', color='#1e293b', weight='bold'),
                gridcolor='#e2e8f0',
                linecolor='#cbd5e1'
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#334155')
        ),
        height=350,
        margin=dict(l=45, r=45, t=35, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif")
    )
    return fig


def render_skill_badges_html(skills: List[str], badge_type: str = "matching") -> str:
    """
    Renders styled modern HTML pill badges for skills.
    badge_type: 'matching' (emerald), 'missing' (rose), or 'additional' (indigo)
    """
    if not skills:
        return "<p style='color: #94a3b8; font-style: italic; font-size: 0.85rem; margin: 4px 0;'>No skills detected in this category.</p>"

    styles = {
        "matching": "background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;",
        "missing": "background-color: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;",
        "additional": "background-color: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe;"
    }
    style = styles.get(badge_type, styles["matching"])

    dot_colors = {
        "matching": "#10b981",
        "missing": "#ef4444",
        "additional": "#6366f1"
    }
    dot_color = dot_colors.get(badge_type, "#10b981")

    badges = []
    for skill in skills:
        badges.append(
            f"<span style='display:inline-flex; align-items:center; gap:5px; padding: 4px 10px; margin: 3px; "
            f"border-radius: 20px; font-size: 0.82rem; font-weight: 600; {style}'>"
            f"<span style='width:6px; height:6px; border-radius:50%; background-color:{dot_color}; display:inline-block;'></span>"
            f"{skill}</span>"
        )

    return f"<div style='display: flex; flex-wrap: wrap; gap: 4px; align-items: center;'>{''.join(badges)}</div>"


def render_extraction_badge_html(method: str, is_scanned: bool = False) -> str:
    """
    Renders a modern, minimalist badge indicating whether the resume text
    was extracted via native PyMuPDF or via the RapidOCR fallback engine.
    """
    if method == "ocr" or is_scanned:
        return (
            "<div style='margin-bottom:14px;'>"
            "<span style='display:inline-flex; align-items:center; gap:8px; background-color:#faf5ff; "
            "color:#6b21a8; border:1px solid #e9d5ff; padding:6px 14px; border-radius:8px; font-size:0.83rem; font-weight:600; box-shadow: 0 1px 2px rgba(0,0,0,0.03);'>"
            "<span style='width:8px; height:8px; border-radius:50%; background-color:#9333ea; display:inline-block;'></span>"
            "Engine Mode: OCR Fallback Engine (Scanned Document Detected)"
            "</span></div>"
        )
    elif method == "normal":
        return (
            "<div style='margin-bottom:14px;'>"
            "<span style='display:inline-flex; align-items:center; gap:8px; background-color:#f0fdf4; "
            "color:#15803d; border:1px solid #bbf7d0; padding:6px 14px; border-radius:8px; font-size:0.83rem; font-weight:600; box-shadow: 0 1px 2px rgba(0,0,0,0.03);'>"
            "<span style='width:8px; height:8px; border-radius:50%; background-color:#22c55e; display:inline-block;'></span>"
            "Engine Mode: Native Text Engine (Searchable Text PDF)"
            "</span></div>"
        )
    return ""


def ensure_sample_pdf_exists() -> str:
    """
    Generates a valid demo PDF resume file (data/sample_resume.pdf) using PyMuPDF
    if it does not already exist.
    """
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_resume.pdf")
    txt_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_resume.txt")

    if os.path.exists(pdf_path):
        return pdf_path

    # Read sample text
    content = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

    if not content:
        content = "Alex Rivera\nSoftware Engineer\nPython, SQL, Docker, Machine Learning"

    # Create PDF with PyMuPDF
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Standard Letter size

    # Write text cleanly to page
    rect = fitz.Rect(50, 50, 562, 742)
    page.insert_textbox(rect, content, fontsize=9.5, fontname="helv", align=fitz.TEXT_ALIGN_LEFT)

    doc.save(pdf_path)
    doc.close()
    return pdf_path


def ensure_sample_scanned_pdf_exists() -> str:
    """
    Generates a valid image-only/scanned PDF resume file (data/sample_scanned_resume.pdf)
    where pages contain rendered bitmap images with ZERO selectable text.
    Used for testing and demonstrating the automatic OCR fallback engine.
    """
    scanned_pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_scanned_resume.pdf")
    if os.path.exists(scanned_pdf_path):
        return scanned_pdf_path

    # First ensure the standard sample exists so we can render its visual representation
    sample_text_pdf = ensure_sample_pdf_exists()

    doc_text = fitz.open(sample_text_pdf)
    pix = doc_text[0].get_pixmap(dpi=150)
    img_bytes = pix.tobytes("jpeg", jpg_quality=85)
    doc_text.close()

    # Create a brand new PDF with only the bitmap image (no text layer)
    doc_scanned = fitz.open()
    page = doc_scanned.new_page(width=pix.width * 72 / 150, height=pix.height * 72 / 150)
    page.insert_image(page.rect, stream=img_bytes)
    doc_scanned.save(scanned_pdf_path)
    doc_scanned.close()

    return scanned_pdf_path
