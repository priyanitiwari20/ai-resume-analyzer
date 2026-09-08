"""
skill_extractor.py
--------------------------------------------------------------------------------
Skill Extraction Service.
Matches skills from a structured JSON taxonomy against unstructured resume
and job description texts using regex word boundaries.

Beginner-Friendly Explanation:
Instead of just checking 'if skill in text' (which causes bugs like matching 'C'
inside 'Cat' or 'Java' inside 'JavaScript'), we use regular expressions with
word boundaries (\b) and escape special characters like 'C++' or 'Node.js'.
--------------------------------------------------------------------------------
"""

import json
import os
import re
from typing import Dict, List, Set, Optional

# Default path to skills.json in data/
DEFAULT_SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")

# Normalization dictionary to consolidate skill variations to standard names
SKILL_ALIASES = {
    "react.js": "React",
    "reactjs": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "html5": "HTML",
    "html": "HTML",
    "css3": "CSS",
    "css": "CSS",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "genai": "Generative AI",
    "generative ai": "Generative AI"
}


def load_skills_taxonomy(filepath: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Loads the skills dictionary grouped by category from data/skills.json.
    """
    path = filepath or DEFAULT_SKILLS_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback minimal dictionary if file is missing
        return {
            "Programming": ["Python", "Java", "C++", "JavaScript", "SQL", "C"],
            "Web Development": ["HTML", "CSS", "React", "Node.js", "Django", "Flask"],
            "Data & AI": ["Machine Learning", "Deep Learning", "Pandas", "NumPy", "Scikit-learn"],
            "Database": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"],
            "Cloud & DevOps": ["AWS", "Azure", "Docker", "Git", "GitHub"],
            "Tools & Platforms": ["VS Code", "Jupyter", "Postman"],
            "Soft Skills": ["Communication", "Problem Solving", "Teamwork", "Leadership"]
        }


def build_skill_regex(skill: str) -> re.Pattern:
    """
    Constructs a robust regex pattern for a given skill.
    Handles tricky characters like '+', '#', '.', and single letter languages like 'C' and 'R'.
    """
    skill_clean = skill.strip()

    # Special handling for single-letter programming languages
    if skill_clean.upper() in ["C", "R"]:
        # Match 'C' or 'R' when preceded/followed by whitespace, punctuation, or common qualifiers
        # e.g., "C programming", "C / C++", "Language: C", but NOT "Cat", "Car", etc.
        return re.compile(rf"(?:(?<=\s)|(?<=^)|(?<=[,\/;|]))\b{re.escape(skill_clean)}\b(?=(?:[\s,.;\/|]|$))", re.IGNORECASE)

    # For C++ or C#
    if "++" in skill_clean or "#" in skill_clean:
        escaped = re.escape(skill_clean)
        return re.compile(rf"(?:(?<=\s)|(?<=^)|(?<=[,\/;|])){escaped}(?=(?:[\s,.;\/|]|$))", re.IGNORECASE)

    # Standard word-boundary regex for multi-word or standard tokens
    escaped = re.escape(skill_clean)
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def extract_skills_from_text(
    text: str,
    skills_taxonomy: Optional[Dict[str, List[str]]] = None
) -> Dict[str, List[str]]:
    """
    Extracts all detected skills from the provided text, grouped by category.

    Parameters:
        text: Raw or cleaned text (resume or job description)
        skills_taxonomy: Optional custom taxonomy dictionary

    Returns:
        Dictionary mapping category names to lists of detected skills.
        Example: {"Programming": ["Python", "SQL"], "Cloud & DevOps": ["Docker"]}
    """
    if not text:
        return {}

    taxonomy = skills_taxonomy or load_skills_taxonomy()
    extracted_by_category: Dict[str, List[str]] = {}

    for category, skill_list in taxonomy.items():
        found_in_category: Set[str] = set()

        for raw_skill in skill_list:
            pattern = build_skill_regex(raw_skill)
            if pattern.search(text):
                # Standardize skill name if alias exists
                norm_name = SKILL_ALIASES.get(raw_skill.lower(), raw_skill)
                found_in_category.add(norm_name)

        if found_in_category:
            extracted_by_category[category] = sorted(list(found_in_category))

    return extracted_by_category


def flatten_skills(categorized_skills: Dict[str, List[str]]) -> List[str]:
    """
    Flattens a categorized skills dictionary into a single sorted list of unique skills.
    """
    all_skills: Set[str] = set()
    for skills in categorized_skills.values():
        all_skills.update(skills)
    return sorted(list(all_skills))


def get_technical_and_soft_skills(
    categorized_skills: Dict[str, List[str]]
) -> Tuple_Soft_Tech:
    """
    Splits detected skills into two convenient lists:
    1. technical_skills (Programming, Web, Data/AI, Cloud, Database, Tools)
    2. soft_skills (Soft Skills category)
    """
    soft = categorized_skills.get("Soft Skills", [])
    tech: Set[str] = set()
    for cat, skills in categorized_skills.items():
        if cat != "Soft Skills":
            tech.update(skills)

    return sorted(list(tech)), sorted(list(soft))


# Type alias for tuple return
Tuple_Soft_Tech = tuple[List[str], List[str]]
