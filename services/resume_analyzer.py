"""
resume_analyzer.py
--------------------------------------------------------------------------------
Resume Structure, Section Parsing, and ATS-Style Scoring Engine.

Beginner-Friendly Explanation:
Real ATS (Applicant Tracking Systems) parse resumes looking for standard sections,
contact information, relevant skills, action verbs, and clear formatting.
This module inspects the resume structure and calculates an explainable
"Estimated ATS-Style Score" (0-100) with detailed component breakdowns.
--------------------------------------------------------------------------------
"""

import re
from typing import Dict, List, Any, Optional
from services.skill_extractor import extract_skills_from_text, flatten_skills, get_technical_and_soft_skills


# Common action verbs that strengthen resume bullet points
ACTION_VERBS = [
    "architected", "built", "created", "designed", "developed", "engineered",
    "implemented", "spearheaded", "optimized", "streamlined", "accelerated",
    "automated", "deployed", "orchestrated", "refactored", "resolved",
    "led", "managed", "supervised", "mentored", "collaborated", "negotiated",
    "analyzed", "forecasted", "modeled", "measured", "evaluated", "launched",
    "reduced", "increased", "maximized", "saved", "achieved", "delivered"
]

# Standard section header regex patterns
SECTION_PATTERNS = {
    "education": re.compile(r"\b(education|academic background|academics|qualifications|degrees?)\b", re.IGNORECASE),
    "experience": re.compile(r"\b(experience|work experience|employment history|work history|professional experience|internships?)\b", re.IGNORECASE),
    "projects": re.compile(r"\b(projects|key projects|academic projects|personal projects|technical projects)\b", re.IGNORECASE),
    "skills": re.compile(r"\b(skills|technical skills|core competencies|technologies|tools & technologies)\b", re.IGNORECASE),
    "certifications": re.compile(r"\b(certifications?|licenses|certificates|credentials|courses)\b", re.IGNORECASE),
    "summary": re.compile(r"\b(summary|professional summary|profile|about me|objective)\b", re.IGNORECASE)
}


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts email addresses, phone numbers, and professional social profiles
    (LinkedIn, GitHub, Portfolios) from resume text.
    """
    info = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "score_contribution": 0
    }

    if not text:
        return info

    # Email pattern
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", text)
    if email_match:
        info["email"] = email_match.group(0)

    # Phone number pattern (various formats: (123) 456-7890, 123-456-7890, +1 123 456 7890, etc.)
    phone_match = re.search(
        r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})",
        text
    )
    if phone_match:
        info["phone"] = phone_match.group(0).strip()

    # LinkedIn profile
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group(0)

    # GitHub profile
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        info["github"] = github_match.group(0)

    # Calculate contact completeness score (out of 15)
    score = 0
    if info["email"]:
        score += 6
    if info["phone"]:
        score += 5
    if info["linkedin"] or info["github"]:
        score += 4

    info["score_contribution"] = min(score, 15)
    return info


def detect_sections(text: str) -> Dict[str, bool]:
    """
    Checks for the presence of essential resume sections.
    """
    found_sections = {}
    for section_name, pattern in SECTION_PATTERNS.items():
        found_sections[section_name] = bool(pattern.search(text))
    return found_sections


def extract_education_details(text: str) -> List[str]:
    """
    Detects degrees, diplomas, universities, and graduation years.
    """
    education_items = []
    if not text:
        return education_items

    # Degree patterns
    degree_patterns = [
        r"\b(?:bachelor'?s?|b\.?s\.?|b\.?tech|b\.?e\.?|b\.?a\.?)\b(?:\s+(?:of|in)\s+[A-Za-z\s]+)?",
        r"\b(?:master'?s?|m\.?s\.?|m\.?tech|m\.?e\.?|m\.?b\.?a\.?)\b(?:\s+(?:of|in)\s+[A-Za-z\s]+)?",
        r"\b(?:ph\.?d\.?|doctorate)\b(?:\s+(?:of|in)\s+[A-Za-z\s]+)?",
        r"\b(?:associate'?s?)\b(?:\s+(?:of|in)\s+[A-Za-z\s]+)?"
    ]

    for pat in degree_patterns:
        matches = re.finditer(pat, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.group(0).strip().title()
            if cleaned not in education_items and len(cleaned) < 50:
                education_items.append(cleaned)

    # Also detect graduation years like 2018 - 2022 or Graduated 2023
    year_matches = re.findall(r"\b(20[0-2][0-9]|19[8-9][0-9])\b", text)
    if year_matches and not education_items:
        education_items.append(f"Graduation/Timeline Years Detected: {', '.join(sorted(set(year_matches))[-2:])}")

    return education_items[:4]


def extract_experience_details(text: str) -> Dict[str, Any]:
    """
    Extracts experience metrics such as detected job titles, years of experience,
    and action verb count.
    """
    details = {
        "job_titles_detected": [],
        "action_verbs_found": [],
        "quantifiable_metrics_count": 0,
        "estimated_years": 0
    }

    if not text:
        return details

    # Common role keywords
    common_roles = [
        "Software Engineer", "Software Developer", "Full Stack Developer",
        "Frontend Developer", "Backend Developer", "Data Scientist",
        "Data Analyst", "Machine Learning Engineer", "DevOps Engineer",
        "Cloud Architect", "Project Manager", "Product Manager",
        "Quality Assurance", "QA Engineer", "Intern", "Research Assistant"
    ]

    for role in common_roles:
        if re.search(rf"\b{re.escape(role)}\b", text, re.IGNORECASE):
            details["job_titles_detected"].append(role)

    # Detect action verbs
    words = text.lower().split()
    found_verbs = set()
    for verb in ACTION_VERBS:
        if verb in words:
            found_verbs.add(verb.capitalize())
    details["action_verbs_found"] = sorted(list(found_verbs))

    # Detect quantifiable metrics (percentages, dollar amounts, numbers with + or k)
    metrics_matches = re.findall(r"(\b\d+%\b|\$\d+(?:,\d+)*(?:\.\d+)?|\b\d+\+\s*(?:users|clients|projects|team|members|latency|queries)\b)", text, re.IGNORECASE)
    details["quantifiable_metrics_count"] = len(metrics_matches)

    # Estimate years of experience from year ranges (e.g., 2021 - 2024 or 2020 - Present)
    ranges = re.findall(r"\b(20[0-2][0-9])\s*(?:-|to|–)\s*(20[0-2][0-9]|present)\b", text, re.IGNORECASE)
    total_years = 0
    for start, end in ranges:
        start_yr = int(start)
        end_yr = 2026 if end.lower() == "present" else int(end)
        diff = max(0, end_yr - start_yr)
        total_years += diff

    details["estimated_years"] = min(total_years, 25)
    return details


def calculate_estimated_ats_score(
    text: str,
    contact_info: Dict[str, Any],
    sections: Dict[str, bool],
    skill_count: int,
    action_verb_count: int,
    metrics_count: int
) -> Dict[str, Any]:
    """
    Calculates an explainable Estimated ATS-Style Score (0-100).

    Breakdown:
    1. Section Completeness (Max 30 pts)
       - Experience section (8 pts)
       - Education section (8 pts)
       - Skills section (8 pts)
       - Projects / Certifications / Summary (6 pts)
    2. Contact Information (Max 15 pts)
       - Email (6 pts), Phone (5 pts), Social Profile (4 pts)
    3. Action Verbs & Quantifiable Impact (Max 20 pts)
       - Strong action verbs (up to 12 pts)
       - Quantified metrics like % or $ (up to 8 pts)
    4. Skill Richness & Density (Max 20 pts)
       - 10+ skills found gives full points (2 pts per skill)
    5. Formatting & Length Suitability (Max 15 pts)
       - Word count between 300 and 1000 words (15 pts), scaled if too short or long
    """
    breakdown = {}

    # 1. Section Completeness (30 pts)
    sec_pts = 0
    if sections.get("experience"):
        sec_pts += 8
    if sections.get("education"):
        sec_pts += 8
    if sections.get("skills"):
        sec_pts += 8
    if sections.get("projects") or sections.get("certifications") or sections.get("summary"):
        sec_pts += 6
    breakdown["section_completeness"] = min(sec_pts, 30)

    # 2. Contact Info (15 pts)
    breakdown["contact_information"] = contact_info.get("score_contribution", 0)

    # 3. Action Verbs & Impact (20 pts)
    verb_pts = min(action_verb_count * 2, 12)
    metric_pts = min(metrics_count * 4, 8)
    breakdown["action_verbs_and_impact"] = verb_pts + metric_pts

    # 4. Skill Richness (20 pts)
    breakdown["skill_richness"] = min(skill_count * 2, 20)

    # 5. Formatting & Length (15 pts)
    word_count = len(text.split())
    if 300 <= word_count <= 950:
        length_pts = 15
    elif 150 <= word_count < 300:
        length_pts = 9
    elif 950 < word_count <= 1400:
        length_pts = 10
    else:
        length_pts = 5
    breakdown["formatting_and_length"] = length_pts

    # Total score calculation (bounded strictly between 0 and 100)
    total_ats_score = sum(breakdown.values())
    total_ats_score = max(0, min(round(total_ats_score, 1), 100))

    return {
        "score": total_ats_score,
        "breakdown": breakdown,
        "word_count": word_count
    }


def analyze_resume_full(text: str) -> Dict[str, Any]:
    """
    Performs complete comprehensive analysis of the resume text.
    """
    # 1. Extract contact information
    contact = extract_contact_info(text)

    # 2. Detect resume sections
    sections = detect_sections(text)

    # 3. Extract categorized skills
    categorized_skills = extract_skills_from_text(text)
    all_skills = flatten_skills(categorized_skills)
    tech_skills, soft_skills = get_technical_and_soft_skills(categorized_skills)

    # 4. Extract education & experience details
    education = extract_education_details(text)
    experience = extract_experience_details(text)

    # 5. Calculate ATS-style score
    ats_data = calculate_estimated_ats_score(
        text=text,
        contact_info=contact,
        sections=sections,
        skill_count=len(all_skills),
        action_verb_count=len(experience["action_verbs_found"]),
        metrics_count=experience["quantifiable_metrics_count"]
    )

    return {
        "text": text,
        "ats_score": ats_data["score"],
        "ats_breakdown": ats_data["breakdown"],
        "word_count": ats_data["word_count"],
        "contact_info": contact,
        "sections": sections,
        "all_skills": all_skills,
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "categorized_skills": categorized_skills,
        "education": education,
        "experience": experience
    }
