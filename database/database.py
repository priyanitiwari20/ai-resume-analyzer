"""
database.py
--------------------------------------------------------------------------------
SQLite Database Layer for AI Resume Analyzer & Job Match System.
Provides simple, reliable, and clean CRUD operations to store and retrieve
past resume analyses.

Beginner-Friendly Note:
SQLite is a lightweight, file-based database built into Python's standard library.
No external database server (like PostgreSQL or MySQL) is required to run this!
--------------------------------------------------------------------------------
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Default path for the database file: stored inside the database/ directory
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "resume_analyzer.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Sets row_factory to sqlite3.Row so columns can be accessed by name like dictionaries.
    """
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initializes the SQLite database tables if they do not exist.
    Creates the 'analyses' table to store analysis results and metadata.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            resume_filename TEXT NOT NULL,
            job_title TEXT NOT NULL,
            ats_score REAL NOT NULL,
            match_score REAL NOT NULL,
            matching_skills TEXT,
            missing_skills TEXT,
            additional_skills TEXT,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(
    resume_filename: str,
    job_title: str,
    ats_score: float,
    match_score: float,
    matching_skills: List[str],
    missing_skills: List[str],
    additional_skills: List[str],
    summary: str = "",
    db_path: Optional[str] = None
) -> int:
    """
    Saves a new resume analysis record into the database.

    Parameters:
        resume_filename: Name of the uploaded resume PDF
        job_title: Target job title or short snippet of the job
        ats_score: Estimated ATS-style score (0-100)
        match_score: Overall Job Match percentage (0-100)
        matching_skills: List of skills matched between resume and job
        missing_skills: List of required skills missing from resume
        additional_skills: List of extra skills found on resume
        summary: Brief AI or heuristic summary of the fit
        db_path: Optional custom path to database file

    Returns:
        The newly inserted row ID (integer).
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serialize skill lists as JSON strings for clean storage
    matching_json = json.dumps(matching_skills)
    missing_json = json.dumps(missing_skills)
    additional_json = json.dumps(additional_skills)

    cursor.execute("""
        INSERT INTO analyses (
            timestamp,
            resume_filename,
            job_title,
            ats_score,
            match_score,
            matching_skills,
            missing_skills,
            additional_skills,
            summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        resume_filename or "Resume.pdf",
        job_title or "Target Job",
        round(float(ats_score), 1),
        round(float(match_score), 1),
        matching_json,
        missing_json,
        additional_json,
        summary or ""
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_all_analyses(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all past resume analyses sorted by most recent first.

    Returns:
        List of dictionaries representing each analysis record.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM analyses ORDER BY id DESC")
    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "resume_filename": row["resume_filename"],
            "job_title": row["job_title"],
            "ats_score": row["ats_score"],
            "match_score": row["match_score"],
            "matching_skills": json.loads(row["matching_skills"] or "[]"),
            "missing_skills": json.loads(row["missing_skills"] or "[]"),
            "additional_skills": json.loads(row["additional_skills"] or "[]"),
            "summary": row["summary"]
        })

    conn.close()
    return results


def get_analysis_by_id(analysis_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single analysis record by its ID.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "resume_filename": row["resume_filename"],
        "job_title": row["job_title"],
        "ats_score": row["ats_score"],
        "match_score": row["match_score"],
        "matching_skills": json.loads(row["matching_skills"] or "[]"),
        "missing_skills": json.loads(row["missing_skills"] or "[]"),
        "additional_skills": json.loads(row["additional_skills"] or "[]"),
        "summary": row["summary"]
    }


def delete_analysis(analysis_id: int, db_path: Optional[str] = None) -> bool:
    """
    Deletes a specific analysis record from the database by ID.

    Returns:
        True if a row was deleted, False otherwise.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def clear_all_analyses(db_path: Optional[str] = None) -> None:
    """
    Removes all records from the analyses table.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analyses")
    conn.commit()
    conn.close()
