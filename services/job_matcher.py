"""
job_matcher.py
--------------------------------------------------------------------------------
Job Matching & NLP Similarity Service.
Computes skill overlap, TF-IDF cosine similarity, combined job match percentage,
and generates actionable resume improvement suggestions.

Beginner-Friendly Explanation:
1. Skill Overlap measures what percentage of the employer's required skills you have.
2. TF-IDF (Term Frequency-Inverse Document Frequency) measures how well the vocabulary,
   phrasing, and terminology between your resume and the job description align.
3. Combining them (60% Skill Overlap + 40% TF-IDF Similarity) produces an explainable,
   balanced Job Match Score.
--------------------------------------------------------------------------------
"""

from typing import Dict, List, Set, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.skill_extractor import extract_skills_from_text, flatten_skills


def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Calculates the TF-IDF cosine similarity between two texts.

    Parameters:
        text1: Resume text
        text2: Job description text

    Returns:
        Similarity percentage as a float between 0.0 and 100.0.
    """
    if not text1 or not text2:
        return 0.0

    try:
        # TfidfVectorizer with english stop-words and unigrams + bigrams
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        # Compute cosine similarity between vector 0 and vector 1
        sim_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim_score) * 100, 1)
    except Exception:
        # Fallback if vocabulary is empty or vectorizer encounters edge-case input
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        jaccard = len(words1 & words2) / len(words1 | words2)
        return round(float(jaccard) * 100, 1)


def compare_skills(
    resume_skills: List[str],
    job_skills: List[str]
) -> Dict[str, Any]:
    """
    Compares resume skills with job description skills to produce:
    - Matching Skills: Skills in both Resume and Job
    - Missing Skills: Skills required by Job but absent from Resume
    - Additional Skills: Skills on Resume not explicitly requested by Job
    - Skill Overlap Score (0-100)
    """
    resume_set: Set[str] = set(resume_skills)
    job_set: Set[str] = set(job_skills)

    matching = sorted(list(resume_set & job_set))
    missing = sorted(list(job_set - resume_set))
    additional = sorted(list(resume_set - job_set))

    if len(job_set) > 0:
        overlap_score = round((len(matching) / len(job_set)) * 100, 1)
    else:
        # If job description didn't specify any recognized skills
        overlap_score = 100.0 if len(resume_set) > 0 else 50.0

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "additional_skills": additional,
        "overlap_score": min(overlap_score, 100.0),
        "total_job_skills": len(job_set),
        "total_resume_skills": len(resume_set)
    }


def compute_job_match_score(
    skill_overlap_score: float,
    tfidf_similarity_score: float
) -> Dict[str, Any]:
    """
    Combines skill overlap and TF-IDF similarity into an overall job match score.

    Formula:
    Match Score = (0.60 * Skill Overlap) + (0.40 * TF-IDF Cosine Similarity)
    """
    weight_skills = 0.60
    weight_tfidf = 0.40

    overall = (weight_skills * skill_overlap_score) + (weight_tfidf * tfidf_similarity_score)
    overall_clamped = round(max(0.0, min(overall, 100.0)), 1)

    return {
        "match_score": overall_clamped,
        "skill_overlap_score": skill_overlap_score,
        "tfidf_similarity_score": tfidf_similarity_score,
        "weights": {
            "skill_overlap_weight": "60%",
            "tfidf_similarity_weight": "40%"
        },
        "formula_explanation": (
            "Overall Job Match Score is calculated by combining: "
            "1) Skill Overlap (60% weight) - the percentage of target job skills present on your resume, and "
            "2) TF-IDF Cosine Similarity (40% weight) - how closely your resume's terminology and phrasing match the job description."
        )
    }


def generate_improvement_suggestions(
    resume_analysis: Dict[str, Any],
    job_comparison: Dict[str, Any],
    job_text: str
) -> Dict[str, List[str]]:
    """
    Generates actionable, practical resume improvement suggestions.
    Guaranteed not to invent fake experiences or degrees.
    """
    missing_skills = job_comparison.get("missing_skills", [])
    sections = resume_analysis.get("sections", {})
    contact = resume_analysis.get("contact_info", {})
    experience = resume_analysis.get("experience", {})
    action_verbs = experience.get("action_verbs_found", [])
    metrics_count = experience.get("quantifiable_metrics_count", 0)

    suggestions = {
        "missing_keywords": missing_skills[:8],
        "skills_to_learn": [],
        "ats_optimization": [],
        "formatting_readability": [],
        "project_descriptions": [],
        "bullet_points": [],
        "action_verbs": []
    }

    # 1. Skills the candidate should learn
    if missing_skills:
        for s in missing_skills[:4]:
            suggestions["skills_to_learn"].append(
                f"**{s}**: High-priority gap for this role. Build a small hands-on project or complete an online module demonstrating basic proficiency."
            )
        if len(missing_skills) > 4:
            suggestions["skills_to_learn"].append(
                f"Secondary target competencies to explore: {', '.join(missing_skills[4:8])}."
            )
    else:
        suggestions["skills_to_learn"].append(
            "All core skills identified in the job description are already represented on your resume! Focus on highlighting advanced depth."
        )

    # 2. ATS Optimization Suggestions
    suggestions["ats_optimization"].extend([
        "Use standard section headers ('Technical Skills', 'Work Experience', 'Education', 'Projects') so ATS parsing algorithms categorize entries without errors.",
        "Ensure keywords from the job description are integrated naturally into the context of work accomplishments, not just dumped in a keyword list.",
        "Keep contact information in the document body. Avoid placing email or phone numbers inside header/footer bands where some ATS parsers ignore them."
    ])

    # 3. Resume Formatting & Readability Suggestions
    suggestions["formatting_readability"].extend([
        "Maintain clean single-column layout for your work history. Multi-column tables or floating text boxes can scramble the reading order in older ATS engines.",
        "Use standard, universally supported fonts (Calibri, Arial, Helvetica, Georgia) at 10-12pt size with clear line spacing.",
        "Aim for a concise length: 1 page for 0-4 years experience, or 2 pages for senior profiles. Avoid leaving awkward 2-line overflow onto a second page."
    ])

    # 4. Suggestions for Improving Project Descriptions
    if not sections.get("projects"):
        suggestions["project_descriptions"].append(
            "Add a dedicated 'Key Projects' section with 2-3 substantial technical projects showcasing practical engineering ability."
        )
    suggestions["project_descriptions"].extend([
        "Structure each project with: 1) Project Name & Role, 2) Tech Stack Used (e.g. Python, Docker, Redis), 3) The specific problem solved, and 4) A clickable link to the GitHub repository or live demo.",
        "State the scale or complexity: mention API request volumes, dataset sizes, latency improvements, or active user counts."
    ])

    # 5. Suggestions for Improving Experience Bullet Points (STAR / XYZ framework)
    if metrics_count < 2:
        suggestions["bullet_points"].append(
            "Quantify Your Impact: Recruiters look for measurable outcomes. Include numbers, percentages, time saved, or revenue metrics (e.g. 'Automated ETL pipeline cutting processing time by 45%')."
        )
    suggestions["bullet_points"].extend([
        "Adopt Google's XYZ Formula: 'Accomplished [X], as measured by [Y], by doing [Z]' to ensure every bullet communicates genuine business value.",
        "Avoid duty-based passive phrases like 'Responsible for maintaining servers' — transform into 'Maintained 99.9% uptime across 15 production Linux instances via automated health monitoring'."
    ])

    # 6. Stronger Action Verbs
    recommended_verbs = ["Architected", "Engineered", "Optimized", "Automated", "Spearheaded", "Refactored", "Deployed", "Streamlined", "Orchestrated"]
    missing_power_verbs = [v for v in recommended_verbs if v not in action_verbs]

    if len(action_verbs) < 5:
        suggestions["action_verbs"].append(
            f"Replace passive language with high-impact power verbs. Recommended verbs for your domain: {', '.join(missing_power_verbs[:6])}."
        )
    else:
        suggestions["action_verbs"].append(
            f"Strong action verbs detected: {', '.join(action_verbs[:5])}. To further elevate your bullets, consider incorporating: {', '.join(missing_power_verbs[:4])}."
        )

    return suggestions


def match_resume_to_job(
    resume_analysis: Dict[str, Any],
    job_text: str
) -> Dict[str, Any]:
    """
    Orchestrates the complete matching pipeline between a parsed resume and a job description.
    """
    resume_text = resume_analysis.get("text", "")
    resume_skills = resume_analysis.get("all_skills", [])

    # Extract skills from job description
    job_categorized_skills = extract_skills_from_text(job_text)
    job_skills = flatten_skills(job_categorized_skills)

    # Skill comparison
    skill_comparison = compare_skills(resume_skills, job_skills)

    # TF-IDF similarity
    tfidf_sim = calculate_tfidf_similarity(resume_text, job_text)

    # Overall Job Match score
    match_score_data = compute_job_match_score(
        skill_overlap_score=skill_comparison["overlap_score"],
        tfidf_similarity_score=tfidf_sim
    )

    # Improvement recommendations
    suggestions = generate_improvement_suggestions(
        resume_analysis=resume_analysis,
        job_comparison=skill_comparison,
        job_text=job_text
    )

    return {
        "job_text": job_text,
        "job_categorized_skills": job_categorized_skills,
        "job_skills": job_skills,
        "skill_comparison": skill_comparison,
        "tfidf_similarity": tfidf_sim,
        "match_score": match_score_data["match_score"],
        "match_breakdown": match_score_data,
        "suggestions": suggestions
    }
