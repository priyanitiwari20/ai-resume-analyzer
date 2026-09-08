"""
ai_analyzer.py
--------------------------------------------------------------------------------
AI Analysis Service with Dual-Mode Operation.
Supports Google Gemini and OpenAI LLMs for advanced generative insights.
Includes automatic, graceful fallback to a local rule-based analysis if no
API key is provided or if network/API errors occur.

Security Note:
API keys are read exclusively from environment variables or UI session input.
Keys are never logged or hardcoded.
--------------------------------------------------------------------------------
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Explicitly locate and load .env from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)
else:
    load_dotenv(override=True)


def get_configured_api_key(custom_key: Optional[str] = None) -> Tuple_Key_Provider:
    """
    Retrieves the available API key and identifies the provider (Gemini or OpenAI).
    Checks custom_key first (e.g. entered via UI), then environment variables.
    Reloads .env dynamically so on-the-fly edits take effect immediately.
    """
    if custom_key and custom_key.strip():
        # Auto-detect OpenAI vs Gemini
        if custom_key.strip().startswith("sk-"):
            return custom_key.strip(), "openai"
        return custom_key.strip(), "gemini"

    # Reload from .env in case user updated keys while server is running
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH, override=True)

    # 1. Check Streamlit Cloud Secrets (if running on Streamlit Community Cloud)
    gemini_key = ""
    openai_key = ""
    preferred_provider = "gemini"
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            gemini_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
            openai_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
            preferred_provider = str(st.secrets.get("LLM_PROVIDER", "gemini")).lower()
    except Exception:
        pass

    # 2. Fall back to environment variables (.env)
    if not gemini_key:
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not openai_key:
        openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if preferred_provider == "gemini" and os.environ.get("LLM_PROVIDER"):
        preferred_provider = os.environ.get("LLM_PROVIDER", "gemini").lower()

    if preferred_provider == "openai" and openai_key:
        return openai_key, "openai"
    elif gemini_key:
        return gemini_key, "gemini"
    elif openai_key:
        return openai_key, "openai"

    return "", "none"


Tuple_Key_Provider = tuple[str, str]


def _clean_json_markdown(text: str) -> str:
    """Strips markdown code fences (```json ... ```) if wrapped by the LLM."""
    clean = text.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    return clean.strip()


def call_gemini_api(api_key: str, prompt: str) -> Optional[Tuple[Dict[str, Any], str]]:
    """
    Calls Google Gemini REST API using the lightweight requests library.
    Employs a resilient multi-model cascade to gracefully handle traffic spikes or deprecations.
    Returns (parsed_json_dict, model_name_used) on success, or None on failure.
    """
    # Priority cascade: highly responsive models with generous free tiers
    candidate_models = [
        "gemini-3.1-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-flash-latest"
    ]

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }

    for model in candidate_models:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    cleaned = _clean_json_markdown(raw_text)
                    return json.loads(cleaned), model
        except Exception:
            continue

    return None


def call_openai_api(api_key: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Calls OpenAI Chat Completions REST API.
    Target model: gpt-4o-mini
    """
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an expert career coach and ATS optimization specialist. Respond strictly in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                raw_text = choices[0].get("message", {}).get("content", "")
                cleaned = _clean_json_markdown(raw_text)
                return json.loads(cleaned)
        return None
    except Exception:
        return None


def generate_local_fallback_analysis(
    resume_analysis: Dict[str, Any],
    job_match: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a rich, structured analysis using rule-based local NLP.
    Ensures the user gets high-quality insights even without any API key or internet access!
    """
    skills_matching = job_match.get("skill_comparison", {}).get("matching_skills", [])
    skills_missing = job_match.get("skill_comparison", {}).get("missing_skills", [])
    match_score = job_match.get("match_score", 0.0)
    ats_score = resume_analysis.get("ats_score", 0.0)
    education = resume_analysis.get("education", [])
    experience = resume_analysis.get("experience", {})
    job_titles = experience.get("job_titles_detected", [])
    action_verbs = experience.get("action_verbs_found", [])

    # Formulate executive summary
    title_str = job_titles[0] if job_titles else "Technical Professional"
    edu_str = education[0] if education else "Technical Background"
    summary = (
        f"Candidate presents a {title_str} profile with a foundation in {edu_str}. "
        f"Demonstrates practical hands-on experience with key tools including {', '.join(skills_matching[:4]) if skills_matching else 'core development tools'}. "
        f"The profile is well-positioned for roles requiring solid software development fundamentals."
    )

    # Determine job fit verdict
    if match_score >= 75:
        verdict = f"High Match ({match_score}%): Strong candidate alignment with core requirements."
    elif match_score >= 50:
        verdict = f"Moderate Match ({match_score}%): Candidate has relevant core skills but some key requirements need addressing."
    else:
        verdict = f"Developing Fit ({match_score}%): Candidate has foundational competencies, but needs further exposure to target job requirements."

    # Identify strengths
    strengths = []
    if skills_matching:
        strengths.append(f"Direct match on {len(skills_matching)} requested skills: {', '.join(skills_matching[:5])}.")
    if action_verbs:
        strengths.append(f"Demonstrates action-oriented experience with strong verbs: {', '.join(action_verbs[:4])}.")
    if ats_score >= 70:
        strengths.append(f"Clear structural layout with an estimated ATS score of {ats_score}/100.")
    if experience.get("quantifiable_metrics_count", 0) > 0:
        strengths.append("Incorporates measurable, quantifiable achievements into experience bullet points.")
    if not strengths:
        strengths.append("Clean resume layout and readable typography detected.")

    # Identify weaknesses / gaps
    weaknesses = []
    if skills_missing:
        weaknesses.append(f"Skill gap in target job requirements: missing {', '.join(skills_missing[:5])}.")
    if not resume_analysis.get("sections", {}).get("projects"):
        weaknesses.append("No dedicated technical projects section detected to demonstrate applied knowledge.")
    if experience.get("quantifiable_metrics_count", 0) == 0:
        weaknesses.append("Experience bullets lack measurable metrics (percentages, numbers, time savings).")
    if not weaknesses:
        weaknesses.append("Minor opportunities to tailor wording more closely to the target job description.")

    # Tailored suggestions
    suggestions = []
    if skills_missing:
        suggestions.append(f"If you have experience with {skills_missing[0]}, incorporate it into your technical skills and project descriptions.")
    suggestions.append("Structure each bullet point using the STAR method (Situation, Task, Action, Result).")
    suggestions.append("Highlight collaborative team contributions and version control practices.")

    # Suggested interview preparation questions with category and answering tips (5-7 tailored questions)
    questions = []

    # 1. Primary Matched Skill Deep Dive
    primary_skill = skills_matching[0] if skills_matching else "Python"
    questions.append({
        "question": f"Can you walk us through a production system or project where you implemented {primary_skill}? What architectural trade-offs did you make?",
        "category": "Technical Competency",
        "tip": f"Explain the core technical challenges, your design decisions, how you structured your {primary_skill} codebase, and how you validated performance."
    })

    # 2. Secondary Matched Skill or Data/Backend Architecture
    second_skill = skills_matching[1] if len(skills_matching) > 1 else "relational database design"
    questions.append({
        "question": f"How do you approach database schema design and query optimization when working with {second_skill}?",
        "category": "System Design & Databases",
        "tip": "Mention indexing strategies, query execution plans, normalization vs denormalization trade-offs, and how you handle concurrent read/write loads."
    })

    # 3. Target Skill Gap Ramp-Up
    if skills_missing:
        gap_skill = skills_missing[0]
        questions.append({
            "question": f"This role requires experience with {gap_skill}, which is not prominent on your resume. How would you quickly ramp up and achieve production proficiency?",
            "category": "Skill Gap & Learning Agility",
            "tip": f"Be honest about your current level, reference similar tools you know, explain your hands-on learning methodology, and cite past examples of rapid tech onboarding."
        })
    else:
        questions.append({
            "question": "How do you stay current with emerging software engineering technologies and decide when to adopt a new framework?",
            "category": "Continuous Learning",
            "tip": "Mention developer documentation, open-source benchmarking, proof-of-concept experimentation, and tech community involvement."
        })

    # 4. Secondary Skill Gap or DevOps/Testing
    if len(skills_missing) > 1:
        gap_skill_2 = skills_missing[1]
        questions.append({
            "question": f"Have you interacted with {gap_skill_2} or comparable tools in automated deployment or local development environments?",
            "category": "Tooling & Infrastructure",
            "tip": "Draw parallels to tools you've used, explain conceptual understanding, and express enthusiasm for mastering their cloud stack."
        })
    else:
        questions.append({
            "question": "What is your philosophy on automated testing (unit, integration, and CI/CD pipelines) in maintaining software reliability?",
            "category": "Software Quality & Testing",
            "tip": "Discuss the testing pyramid, mocking external services, automated regression suites, and test coverage thresholds."
        })

    # 5. Quantified Impact & Incident Resolution (STAR Framework)
    questions.append({
        "question": "Tell us about a time when an application you were working on failed in production or experienced severe performance degradation. How did you diagnose and resolve it?",
        "category": "Incident Resolution & Debugging",
        "tip": "Use the STAR method: clearly describe the Situation, Task, your diagnostic Action (logs, profiling, metrics), and the measurable Result."
    })

    # 6. Cross-functional Collaboration & Delivery
    questions.append({
        "question": "Describe a scenario where you had a technical disagreement with a team member or product requirement. How did you arrive at a constructive solution?",
        "category": "Behavioral & Teamwork",
        "tip": "Focus on data-driven reasoning, active listening, separating ego from technical decisions, and aligning with end-user requirements."
    })

    return {
        "summary": summary,
        "job_fit_verdict": verdict,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "personalized_suggestions": suggestions,
        "recommended_keywords": skills_missing[:6],
        "interview_questions": questions,
        "is_ai_generated": False,
        "provider_used": "Local Rule-Based NLP Engine"
    }


def analyze_with_ai_or_fallback(
    resume_analysis: Dict[str, Any],
    job_match: Dict[str, Any],
    custom_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for AI analysis.
    Attempts LLM API call if key is available; automatically defaults to local NLP fallback.
    """
    api_key, provider = get_configured_api_key(custom_api_key)

    if not api_key:
        return generate_local_fallback_analysis(resume_analysis, job_match)

    # Construct prompt for the LLM
    resume_text = resume_analysis.get("text", "")[:3500]  # Safe token window
    job_text = job_match.get("job_text", "")[:2500]

    prompt = f"""
You are an expert career coach and ATS optimization specialist.
Analyze this resume against the target job description.

RESUME TEXT:
{resume_text}

TARGET JOB DESCRIPTION:
{job_text}

Respond STRICTLY in valid JSON matching this exact JSON schema:
{{
    "summary": "2-3 sentence executive summary of candidate profile and fit",
    "job_fit_verdict": "Clear verdict string (e.g. High Match / Moderate Match / Developing Fit) with rationale",
    "strengths": ["3 to 5 specific candidate strengths relative to the target role"],
    "weaknesses": ["3 to 5 specific gaps or areas to improve"],
    "personalized_suggestions": ["3 to 4 actionable suggestions to enhance resume bullet points"],
    "recommended_keywords": ["Top 5 to 7 high-impact keywords from the job description to add"],
    "interview_questions": [
        {{
            "question": "5 to 8 specific interview questions based on candidate resume and target job",
            "category": "Category name (e.g. Technical Competency, Skill Gap, System Design, Behavioral)",
            "tip": "Actionable guidance and advice on how to structure a strong answer"
        }}
    ]
}}
"""

    ai_result = None
    model_name_used = None
    if provider == "gemini":
        gemini_res = call_gemini_api(api_key, prompt)
        if gemini_res:
            ai_result, model_name_used = gemini_res
    elif provider == "openai":
        ai_result = call_openai_api(api_key, prompt)
        model_name_used = "gpt-4o-mini"

    # If the API call succeeded and returned valid data
    if ai_result and isinstance(ai_result, dict) and "summary" in ai_result:
        ai_result["is_ai_generated"] = True
        ai_result["provider_used"] = f"LLM ({provider.title()} - {model_name_used})" if model_name_used else f"LLM ({provider.title()})"

        # Normalize interview questions in case model returned strings instead of dicts
        norm_questions = []
        for q in ai_result.get("interview_questions", []):
            if isinstance(q, dict):
                norm_questions.append({
                    "question": q.get("question", str(q)),
                    "category": q.get("category", "Technical Competency"),
                    "tip": q.get("tip", "Provide a concrete technical example using the STAR method.")
                })
            elif isinstance(q, str):
                norm_questions.append({
                    "question": q,
                    "category": "Technical Competency",
                    "tip": "Structure your answer around a specific project, technical trade-offs, and measurable outcomes."
                })
        ai_result["interview_questions"] = norm_questions or generate_local_fallback_analysis(resume_analysis, job_match)["interview_questions"]
        return ai_result

    fallback = generate_local_fallback_analysis(resume_analysis, job_match)
    fallback["provider_used"] = f"Local Fallback (API error on {provider.title()})"
    return fallback
