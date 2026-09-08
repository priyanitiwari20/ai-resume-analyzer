# AI Resume Analyzer

> **AI-Powered Resume Analysis & Job Matching**  
> An explainable, production-ready SaaS application designed to audit resumes against technical job postings, detect critical skill gaps, calculate ATS parsing readiness, and generate targeted interview preparation questions.

Built with **Python 3.11+**, **Streamlit**, **PyMuPDF**, **RapidOCR**, **scikit-learn**, **Plotly**, and **SQLite**, featuring an optional **LLM API integration** (Google Gemini & OpenAI) and a 100% self-contained **local NLP fallback engine**.

---

## 📌 Problem Statement

In modern technical recruiting, resumes are typically pre-screened by automated Applicant Tracking Systems (ATS) and algorithmic filters before reaching an engineering hiring manager. Highly capable candidates are frequently eliminated due to:
1. **Non-standard formatting or flat scanned images** that traditional text extractors fail to parse.
2. **Taxonomy mismatch**, where industry-standard keywords and frameworks are missing or phrased differently from the job posting.
3. **Vague bullet points** that lack quantifiable metrics, scope indicators, or standard action verbs (e.g., Google XYZ or STAR framework).
4. **Lack of transparent, explainable feedback** showing exactly why an application scored low or what technical competencies need improvement.

**AI Resume Analyzer** solves this by delivering transparent, mathematical, and actionable evaluations with zero external infrastructure required.

---

## ✨ Key Features

### 1. Dual-Engine PDF Ingestion & Automatic OCR Fallback
- Extracts selectable digital text instantly using **PyMuPDF (`fitz`)**.
- If a scanned resume, flat bitmap, or image-only PDF is detected ($< 30$ selectable words), the application automatically renders high-DPI page images and recovers text via **RapidOCR (ONNX)** with zero external server dependencies.

### 2. Explainable Estimated ATS-Style Score (0–100)
- **Section Completeness (30%)**: Checks for standard headings (`Summary`, `Experience`, `Education`, `Skills`, `Projects`).
- **Contact Information (15%)**: Detects email, phone, and professional portfolio links (LinkedIn, GitHub).
- **Quantifiable Metrics & Power Verbs (20%)**: Audits impact metrics (percentages, numbers, dollar amounts) and strong action verbs.
- **Skill Breadth & Density (20%)**: Measures technical and domain skill richness.
- **Formatting Suitability (15%)**: Validates word count against optimal industry guidelines (350–950 words).

### 3. Intelligent Job Matching & Semantic Similarity
- **Job Match Score** is calculated using an explainable weighted formula:
  $$\text{Job Match Score} = (0.60 \times \text{Skill Overlap \%}) + (0.40 \times \text{TF-IDF Cosine Similarity \%})$$
- **Boundary-Aware Taxonomy Regex**: Scans for 100+ recognized technical and soft skills across 7 categories using boundary-enforced regex to eliminate substring collisions (e.g., distinguishing `C` from `Cat`, or `Java` from `JavaScript`).
- **TF-IDF Vectorization**: Computes high-dimensional cosine similarity across unigrams and bigrams using `scikit-learn`.

### 4. 3-Way Skill Gap Analysis
- **Matched Skills**: Competencies present on both the resume and the job posting.
- **Missing Skills**: Critical employer requirements absent from the resume.
- **Profile Skills**: Additional skills the candidate brings to the table.

### 5. Structured Improvement Recommendations
Renders directly on the results page across 7 distinct categories:
- Missing skills and target keywords
- Prioritized technical skills to learn
- ATS layout and header optimizations
- Readability and single-column formatting suggestions
- Project description enhancements
- Experience bullet rewrites using Google XYZ (`Accomplished [X] measured by [Y] by doing [Z]`)
- Domain-specific power action verbs

### 6. AI Insights & Interview Preparation
- **Executive Alignment Verdict**: Synthesized summary of profile fit against target requirements.
- **Side-by-Side Strengths & Weaknesses**: Immediate assessment of candidate advantages vs. gaps.
- **5–10 Tailored Interview Questions**: Behavioral and technical questions with expandable, actionable **💡 Answering Guidance & Tips**.

### 7. Dual-Mode Operation (Local NLP vs. Generative LLM)
- **Local Rule-Based NLP Mode**: Works 100% out of the box with zero internet connectivity or API keys required.
- **Generative AI Mode**: When an API key (Google Gemini or OpenAI) is provided, enriches evaluations with dynamic generative feedback.

### 8. SQLite Evaluation History & Data Export
- Automatically saves evaluations to a local SQLite database (`database/resume_analyzer.db`).
- Review past scores, compare metrics over time, inspect skill tags, or export history to CSV with a single click.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Primary programming language |
| **Web Interface** | Streamlit | Modern SaaS UI, reactive components, and navigation |
| **PDF Ingestion** | PyMuPDF (`fitz`) | Fast native text extraction and vector rendering |
| **OCR Engine** | RapidOCR / ONNX Runtime | Local OCR fallback for image-only/scanned resumes |
| **NLP & Similarity** | scikit-learn | TF-IDF unigram/bigram vectorization & cosine similarity |
| **Data Processing** | Pandas, NumPy | Relational tabular operations and data transformations |
| **Visualizations** | Plotly Graph Objects | Interactive gauges and 7-axis polar radar charts |
| **Database** | SQLite 3 | Embedded, zero-configuration local persistence |
| **Environment** | python-dotenv | Secure `.env` configuration |
| **Networking** | requests | Direct REST communication for optional Gemini / OpenAI APIs |

---

## 📐 How the Application Works

```
                       ┌─────────────────────────┐
                       │  Resume Upload (PDF)    │
                       └────────────┬────────────┘
                                    │
                         [ Native Text Present? ]
                             /             \
                      YES   /               \  NO (<30 words)
                           v                 v
                 ┌──────────────────┐  ┌──────────────────┐
                 │ PyMuPDF Extractor│  │ RapidOCR Engine  │
                 └─────────┬────────┘  └────────┬─────────┘
                           │                    │
                           └─────────┬──────────┘
                                     │ Sanitized Text
                                     v
                 ┌───────────────────────────────────────┐
                 │ Boundary-Aware Skill Taxonomy Matcher │
                 └───────────────────┬───────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌───────────────────────┐                           ┌─────────────────────┐
│ ATS Scoring Engine    │                           │ TF-IDF Job Matcher  │
│ - Section Check (30%) │                           │ - Skill Overlap 60% │
│ - Contact Info (15%)  │                           │ - Cosine Sim 40%    │
│ - Action/Metrics (20%)│                           └──────────┬──────────┘
│ - Skill Density (20%) │                                      │
│ - Length/Format (15%) │                                      │
└──────────┬────────────┘                                      │
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     │
                                     v
                   ┌───────────────────────────────────┐
                   │   Dual-Mode Insights Generator    │
                   │   - Local Rule-Based NLP (Default)│
                   │   - Optional Gemini / OpenAI API  │
                   └─────────────────┬─────────────────┘
                                     │
                                     v
                   ┌───────────────────────────────────┐
                   │    Streamlit SaaS Dashboard UI    │
                   │    & SQLite Persistence History   │
                   └───────────────────────────────────┘
```

---

## 📁 Project Structure

```text
ai-resume-analyzer/
├── app.py                     # Main application entry point & SaaS CSS design system
├── requirements.txt           # Production dependencies with version bounds
├── README.md                  # Comprehensive architecture & user guide
├── .env.example               # Template for optional LLM API credentials
├── .gitignore                 # Production ignore rules (caches, DB, env, secrets)
├── pages/                     # Streamlit application pages
│   ├── dashboard.py           # Landing view, 4-step workflow, and high-level KPIs
│   ├── analyze.py             # Dual-card input, scorecards, charts & recommendations
│   ├── history.py             # SQLite evaluations table, badges, and CSV export
│   └── about.py               # Technical specifications & architecture overview
├── services/                  # Business logic & algorithms
│   ├── pdf_parser.py          # PyMuPDF parser + RapidOCR fallback for scanned PDFs
│   ├── skill_extractor.py     # Regex boundary extractor across 7 skill domains
│   ├── resume_analyzer.py     # Section detection, contact info & ATS scoring
│   ├── job_matcher.py         # TF-IDF cosine similarity & weighted match scoring
│   └── ai_analyzer.py         # Dual-mode engine (Local NLP & Gemini/OpenAI API)
├── utils/                     # Data taxonomies & UI helpers
│   ├── helpers.py             # Plotly gauges, radar charts, pills & demo PDF generator
│   └── skills_data.py         # 100+ skill taxonomy dictionary
├── database/                  # Embedded persistence
│   └── database.py            # SQLite schema initialization and CRUD queries
├── data/                      # Sample datasets for instant evaluation
│   ├── skills.json            # Categorized skill taxonomy across 7 domains
│   ├── sample_resume.txt      # Source text for demo candidate profile
│   ├── sample_resume.pdf      # Searchable demo PDF resume
│   ├── sample_scanned_resume.pdf # Scanned bitmap PDF for testing OCR fallback
│   └── sample_job.txt         # Full-Stack AI Engineer sample job description
└── tests/                     # Automated test suite
    └── test_pipeline.py       # 7-step unit & integration test verifying all layers
```

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14.
- Git (optional, for cloning).

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment & API Key Setup (Optional)

> **Important:** An API key is completely optional! The application is fully functional out of the box using built-in local NLP and TF-IDF similarity algorithms.

If you wish to enable advanced generative AI analysis (custom candidate summaries and generative interview questions):

1. Copy the `.env.example` file to create your `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and insert your API key:
   ```env
   # Option 1: Google Gemini API (Recommended free tier: https://aistudio.google.com/)
   GEMINI_API_KEY=your_actual_gemini_key_here

   # Option 2: OpenAI API
   OPENAI_API_KEY=your_actual_openai_key_here

   # Preferred provider ("gemini" or "openai")
   LLM_PROVIDER=gemini
   ```
*(You can also input your API key directly inside the application's sidebar during any session without saving it to disk.)*

---

## ▶️ Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

The application will launch in your default web browser at:
```text
http://localhost:8501
```

### Recommended Evaluation Flow:
1. Navigate to **Analyze Resume** in the left navigation sidebar.
2. Click **"Load Demo Resume"** to populate the sample PDF (or upload your own PDF).
3. Click **"Load Sample Job Description"** to populate a technical job description.
4. Click **"Run Analysis"**.
5. Review the **4 Scorecards**, **Dual Gauges**, **Skill Breakdown Pills**, **Category Radar Chart**, **Improvement Recommendations**, and **AI Interview Prep**.
6. Switch to **History** to view your saved evaluations and download a CSV report.

---

## 🧪 Automated Testing

Verify all components (SQLite, PyMuPDF, RapidOCR fallback, Regex boundary matching, ATS scoring, TF-IDF cosine similarity, and Local NLP) with the test suite:

```bash
python tests/test_pipeline.py
```

Expected output:
```text
==================================================
RUNNING AUTOMATED SYSTEM TESTS
==================================================
[1/7] Testing Database Persistence (SQLite)...
  -> PASS: Database CRUD operations validated.
[2/7] Testing Normal Searchable PDF Text Extraction...
  -> Extracted 322 words via native PyMuPDF.
  -> PASS: Standard text PDF extraction validated.
[3/7] Testing Scanned / Image-Based PDF with Automatic OCR Fallback...
  -> OCR Extracted 207 words from bitmap image.
  -> PASS: Scanned PDF automatic OCR fallback validated.
[4/7] Testing Skill Extraction & Regex Boundaries...
  -> PASS: Skill extraction and regex boundary validated.
[5/7] Testing Resume Analyzer & ATS-Style Scoring...
  -> ATS Score: 87/100
  -> PASS: Resume structure and ATS scoring validated.
[6/7] Testing Job Matching & TF-IDF Cosine Similarity...
  -> Job Match Score: 60.7% | TF-IDF Cosine Similarity: 23.9%
  -> PASS: Job matching and similarity calculations validated.
[7/7] Testing AI Analyzer Dual-Mode & Local Fallback...
  -> Mode: Local Rule-Based NLP Engine
  -> PASS: Local NLP fallback works seamlessly with 5-10 interview questions.
==================================================
ALL TESTS PASSED SUCCESSFULLY! (7/7)
==================================================
```

---

## 🔮 Future Enhancements

- [ ] Multi-document batch analysis (rank 10 candidate resumes against a single job description).
- [ ] Exportable PDF evaluation report containing full charts and recommendations.
- [ ] Direct `.docx` (Microsoft Word) resume ingestion.
- [ ] Self-hosted local LLM integration via Ollama (`llama3`, `mistral`, `deepseek`).

---

## 📄 License

This project is licensed under the **MIT License** — free for educational, personal, and commercial portfolio use.
