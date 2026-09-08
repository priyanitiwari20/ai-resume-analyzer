"""
test_pipeline.py
--------------------------------------------------------------------------------
Automated test suite verifying core services:
- SQLite database CRUD operations
- PDF text extraction & error handling
- Skill taxonomy extraction & regex boundary logic
- ATS scoring and section parsing
- TF-IDF cosine similarity & job match scoring
- Local NLP fallback analysis
--------------------------------------------------------------------------------
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import init_db, save_analysis, get_all_analyses, delete_analysis, clear_all_analyses
from services.pdf_parser import extract_text_from_pdf, clean_extracted_text
from services.skill_extractor import extract_skills_from_text, flatten_skills
from services.resume_analyzer import analyze_resume_full, extract_contact_info, detect_sections
from services.job_matcher import match_resume_to_job, calculate_tfidf_similarity, compare_skills
from services.ai_analyzer import analyze_with_ai_or_fallback
from utils.helpers import ensure_sample_pdf_exists, ensure_sample_scanned_pdf_exists


def run_all_tests():
    print("==================================================")
    print("RUNNING AUTOMATED SYSTEM TESTS")
    print("==================================================")

    test_db_path = os.path.join(os.path.dirname(__file__), "test_temp.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # 1. Test Database
    print("[1/7] Testing Database Persistence (SQLite)...")
    init_db(test_db_path)
    rec_id = save_analysis(
        resume_filename="Test_Resume.pdf",
        job_title="Software Engineer",
        ats_score=85.0,
        match_score=78.5,
        matching_skills=["Python", "SQL"],
        missing_skills=["Docker"],
        additional_skills=["Git"],
        summary="Test Candidate Summary",
        db_path=test_db_path
    )
    assert rec_id > 0, "Failed to insert record into SQLite"
    records = get_all_analyses(test_db_path)
    assert len(records) == 1, f"Expected 1 record, got {len(records)}"
    assert records[0]["ats_score"] == 85.0, "Score mismatch in DB"
    assert "Python" in records[0]["matching_skills"], "Skills mismatch in DB"
    del_ok = delete_analysis(rec_id, test_db_path)
    assert del_ok is True, "Failed to delete record from SQLite"
    assert len(get_all_analyses(test_db_path)) == 0, "Record not deleted"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    print("  -> PASS: Database CRUD operations validated.")

    # 2. Test Normal Text PDF Extraction
    print("[2/7] Testing Normal Searchable PDF Text Extraction...")
    sample_pdf = ensure_sample_pdf_exists()
    assert os.path.exists(sample_pdf), "Failed to generate sample PDF"
    text, err, meta = extract_text_from_pdf(sample_pdf)
    assert not err, f"Unexpected error parsing sample PDF: {err}"
    assert len(text) > 50, "Extracted text too short"
    assert meta["page_count"] >= 1, "Page count must be >= 1"
    assert meta["extraction_method"] == "normal", f"Expected normal extraction, got {meta['extraction_method']}"
    assert meta["ocr_applied"] is False, "OCR should not be applied to standard text PDF"
    print(f"  -> Extracted {meta['word_count']} words via native PyMuPDF.")
    print("  -> PASS: Standard text PDF extraction validated.")

    # 3. Test Scanned / Image-Based PDF OCR Fallback
    print("[3/7] Testing Scanned / Image-Based PDF with Automatic OCR Fallback...")
    scanned_pdf = ensure_sample_scanned_pdf_exists()
    assert os.path.exists(scanned_pdf), "Failed to generate scanned image PDF"
    scanned_text, ocr_msg, scanned_meta = extract_text_from_pdf(scanned_pdf)
    assert len(scanned_text) > 50, f"OCR extracted text too short: '{scanned_text}'"
    assert scanned_meta["extraction_method"] == "ocr", f"Expected 'ocr' method, got {scanned_meta['extraction_method']}"
    assert scanned_meta["ocr_applied"] is True, "OCR should be marked as applied"
    assert scanned_meta["is_scanned"] is True, "Document should be detected as scanned"
    # Verify skills can be extracted from the OCR-extracted text
    ocr_skills = flatten_skills(extract_skills_from_text(scanned_text))
    assert len(ocr_skills) > 0, "Failed to extract skills from OCR text"
    print(f"  -> OCR Extracted {scanned_meta['word_count']} words: '{scanned_text[:80]}...'")
    print(f"  -> Detected skills from OCR: {ocr_skills[:5]}")
    print("  -> PASS: Scanned PDF automatic OCR fallback validated.")

    # Test error handling with empty input
    _, empty_err, _ = extract_text_from_pdf(b"")
    assert "empty" in empty_err.lower(), "Empty PDF error not caught properly"

    # Test corrupted PDF error handling
    _, corrupt_err, _ = extract_text_from_pdf(b"Not a real PDF header")
    assert "corrupted" in corrupt_err.lower() or "read pdf" in corrupt_err.lower(), "Corrupted PDF error not caught"

    # 4. Test Skill Extraction
    print("[4/7] Testing Skill Extraction & Regex Boundaries...")
    test_text = "Proficient in Python, SQL, Docker, React.js, and C programming. Experienced with Machine Learning."
    extracted = extract_skills_from_text(test_text)
    flat = flatten_skills(extracted)

    assert "Python" in flat, "Failed to detect Python"
    assert "SQL" in flat, "Failed to detect SQL"
    assert "Docker" in flat, "Failed to detect Docker"
    assert "React" in flat, "Failed to normalize React.js alias"
    assert "Machine Learning" in flat, "Failed to extract multi-word skill"
    print(f"  -> Extracted {len(flat)} skills: {flat}")
    print("  -> PASS: Skill extraction and regex boundary validated.")

    # 5. Test Resume Structure & ATS Scoring
    print("[5/7] Testing Resume Analyzer & ATS-Style Scoring...")
    resume_analysis = analyze_resume_full(text)
    assert 0 <= resume_analysis["ats_score"] <= 100, "ATS score out of bounds"
    assert resume_analysis["contact_info"]["email"] is not None, "Email not detected"
    assert resume_analysis["sections"]["education"] is True, "Education section not detected"
    assert resume_analysis["sections"]["experience"] is True, "Experience section not detected"
    print(f"  -> ATS Score: {resume_analysis['ats_score']}/100")
    print(f"  -> Contact Info: {resume_analysis['contact_info']['email']}")
    print("  -> PASS: Resume structure and ATS scoring validated.")

    # 6. Test Job Matching & TF-IDF
    print("[6/7] Testing Job Matching & TF-IDF Cosine Similarity...")
    job_txt_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_job.txt")
    with open(job_txt_path, "r", encoding="utf-8") as f:
        job_text = f.read()

    match_result = match_resume_to_job(resume_analysis, job_text)
    assert 0 <= match_result["match_score"] <= 100, "Job match score out of bounds"
    assert match_result["tfidf_similarity"] > 0, "TF-IDF similarity should be > 0"
    comp = match_result["skill_comparison"]
    print(f"  -> Job Match Score: {match_result['match_score']}%")
    print(f"  -> TF-IDF Cosine Similarity: {match_result['tfidf_similarity']}%")
    print(f"  -> Matching skills ({len(comp['matching_skills'])}): {comp['matching_skills']}")
    print(f"  -> Missing skills ({len(comp['missing_skills'])}): {comp['missing_skills']}")
    print("  -> PASS: Job matching and similarity calculations validated.")

    # 7. Test AI / Local NLP Fallback & Generative LLM
    print("[7/7] Testing AI Analyzer Dual-Mode & Local Fallback...")
    from services.ai_analyzer import generate_local_fallback_analysis, get_configured_api_key
    # Test local fallback engine explicitly
    local_result = generate_local_fallback_analysis(resume_analysis, match_result)
    assert "summary" in local_result, "Summary missing from local fallback"
    assert len(local_result["strengths"]) > 0, "Strengths missing in local fallback"
    assert len(local_result["weaknesses"]) > 0, "Weaknesses missing in local fallback"
    assert 5 <= len(local_result["interview_questions"]) <= 10, "Expected 5-10 interview questions in local fallback"
    print(f"  -> Local NLP Mode Verified: {local_result['provider_used']}")

    # Test Generative AI integration if key is present
    key, provider = get_configured_api_key()
    if key:
        print(f"  -> Configured LLM Key Detected: Provider = {provider.title()}")
        ai_result = analyze_with_ai_or_fallback(resume_analysis, match_result)
        assert "summary" in ai_result, "Summary missing from AI analysis"
        assert len(ai_result["strengths"]) > 0, "Strengths missing"
        assert len(ai_result["weaknesses"]) > 0, "Weaknesses missing"
        assert len(ai_result["interview_questions"]) >= 5, "Expected at least 5 interview questions"
        print(f"  -> Generative AI Engine Active: {ai_result['provider_used']}")
        print(f"  -> Summary: {ai_result['summary'][:90]}...")
    else:
        print("  -> No external API key found; system operating in 100% Local NLP mode.")
    print("  -> PASS: Dual-mode AI Analyzer and Local NLP validated.")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (7/7)")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
