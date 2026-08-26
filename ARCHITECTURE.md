# CramWise Architecture

> **Document Status:** Verified from actual source code. Last updated: 2026-08-25.
> Every claim below is backed by reading the actual files. Nothing is assumed.

---

## 1. Project Overview

CramWise is an AI-powered academic preparation platform. Its goal is to help students prepare for university exams by:

1. Parsing uploaded **Syllabi** PDFs to extract courses, units, and topics.
2. Parsing uploaded **PYQ (Previous Year Question)** PDFs via OCR + LLM to extract structured questions.
3. Running **M3–M5 analytics** (LLM-driven question-to-syllabus mapping, importance scoring, dependency analysis, study priority ranking) entirely as offline scripts.
4. Providing **M6.5 topic explanations** at runtime: given a selected topic, retrieving grounded context from Cognee (student's notes) and relevant PYQs, then calling Groq to generate a natural-language teaching explanation.
5. Providing **M6.3 personalized study recommendations** using Groq to select topics within a student's available time.
6. Offering a **React + Vite frontend** with dashboard, subjects, analytics, study plan, PYQ explorer, upload, and chat pages — most of which currently display hardcoded mock data.

The system distinguishes between:
- **Offline pipeline** (scripts in `backend/scripts/`): M1–M5 processing that runs separately, producing JSON files.
- **Online API** (FastAPI in `backend/app/`): upload endpoints + M6.x runtime services — **only partially exposed as HTTP endpoints**.

---

## 2. Tech Stack

### Frontend
| Technology | Version / Detail |
|------------|-----------------|
| React | 18.3.1 |
| Vite | 6.0.5 |
| lucide-react | 0.468.0 (icons) |
| Vanilla CSS | `src/styles.css` |
| No router | Single-page app — page switching via `useState` |
| No state manager | All state is local `useState` in `App` |

### Backend
| Technology | Version / Detail |
|------------|-----------------|
| Python | 3.x |
| FastAPI | 0.141.1 |
| Uvicorn | 0.52.4 |
| Pydantic | 2.13.4 |
| python-dotenv | 1.2.3 |
| python-multipart | 0.0.32 (file uploads) |
| SQLAlchemy | 2.0.52 (ORM — defined but **not used by active routers**) |

### AI / LLM
| Technology | Detail |
|------------|--------|
| Groq | API key: `GROQ_API_KEY` from `.env`; model: `openai/gpt-oss-120b` via `groq` Python SDK |
| Cognee | Version 1.5.1; used for vector + knowledge-graph storage and CHUNKS retrieval |
| LiteAPI / LiteLLM | `litellm==1.97.0` — listed in requirements, used by Cognee internally |
| Instructor | `instructor==1.15.1` — listed in requirements |

### Document Processing
| Technology | Detail |
|------------|--------|
| PyMuPDF (fitz) | PDF text extraction (Syllabus), PDF-to-image (PYQ OCR pipeline) |
| Pillow | Image resizing before OCR |
| Ollama | Local OCR model: `maternion/LightOnOCR-2:1b` at `http://localhost:11434` |
| TextCleaner | Custom class in `app/extraction/text_cleaner.py` |

### Storage
| Technology | Detail |
|------------|--------|
| LanceDB | Vector store for Cognee (`cognee.lancedb`); path from `.env` |
| FastEmbed / BAAI/bge-large-en-v1.5 | Embedding model used by Cognee |
| PostgreSQL | Defined in `db/database.py` and `db/models.py`; **not connected to any active API router** |
| File system | Uploads stored under `backend/uploads/`; temp data under `backend/uploads/temp/` |

---

## 3. Directory Structure

```
CramWise_vaishi/
├── backend/
│   ├── .env                          # All secrets and configuration
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                   # FastAPI app; registers upload + notes routers
│   │   ├── clients/
│   │   │   └── groq_client.py        # Groq API wrapper (generate + generate_json)
│   │   ├── db/
│   │   │   ├── database.py           # SQLAlchemy engine + session (PostgreSQL)
│   │   │   └── models.py             # Subject, Unit, Topic, TextBook, ReferenceBook ORM models
│   │   ├── extraction/
│   │   │   ├── ocr_client.py         # Calls Ollama OCR model on page images
│   │   │   ├── ocr_prompt.py         # OCR system prompt text
│   │   │   ├── pdf_to_images.py      # fitz: PDF → JPEG images per page
│   │   │   └── text_cleaner.py       # Cleans raw OCR output
│   │   ├── parsers/
│   │   │   ├── metadata_extractor.py # Regex-based exam metadata (subject, code, sem, marks)
│   │   │   ├── syllabus_parser.py    # fitz: PDF → courses, units, textbooks
│   │   │   ├── question_parser.py    # LLM-based question extraction from OCR text
│   │   │   ├── parser_client.py      # OpenAI-compatible LLM client wrapper
│   │   │   ├── parser_prompt.py      # Question parser prompt
│   │   │   ├── paper_grouper.py      # Groups PDF pages into individual exam papers
│   │   │   ├── exam_type_classifier.py # MIDTERM / ENDTERM classifier
│   │   │   ├── syllabus_topic_prompt.py # Prompt for LLM syllabus structuring
│   │   │   └── syllabus_topic_service.py  ← actually in services/
│   │   ├── prompts/
│   │   │   ├── m6_5_topic_explanation_prompt.py  # M6.5 system prompt + user prompt builder
│   │   │   └── question_analysis_prompt.py       # M3 question analysis prompt
│   │   ├── routers/
│   │   │   ├── upload.py             # POST /upload/syllabus, POST /upload/pyq
│   │   │   └── notes.py              # POST /api/notes/upload
│   │   ├── schemas/
│   │   │   ├── notes.py              # NotesDocumentResponse, NotesUploadResponse
│   │   │   ├── m6_5_topic_explanation.py # M65TopicExplanation, ExampleSection (Pydantic)
│   │   │   ├── llm_analysis.py       # QuestionAnalysis
│   │   │   ├── recommendation.py     # RecommendationRequest, PersonalizedRecommendation
│   │   │   ├── final_study_plan.py   # FinalStudyPlan schema
│   │   │   ├── paper.py              # Paper schema
│   │   │   ├── question.py           # Question schema
│   │   │   └── syllabus_retrieval.py # Syllabus retrieval schema
│   │   ├── services/
│   │   │   ├── upload_service.py     # Simple file-save helper
│   │   │   ├── cognee_service.py     # Cognee remember() / recall() wrapper
│   │   │   ├── paper_storage.py      # Saves parsed paper JSON
│   │   │   ├── paper_text_builder.py # Assembles OCR pages into full paper text
│   │   │   ├── paper_question_parser.py # Orchestrates text builder + question parser
│   │   │   ├── question_enricher.py  # Adds topic/subtopic to raw questions
│   │   │   ├── question_enrichment_service.py
│   │   │   ├── syllabus_topic_service.py # LLM structuring of raw syllabus units
│   │   │   ├── syllabus_index_builder.py # Builds flat syllabus index JSON
│   │   │   ├── syllabus_matcher.py   # (empty file)
│   │   │   ├── database_loader.py    # PostgreSQL bulk loader
│   │   │   ├── embedding_service.py  # Embedding generation
│   │   │   ├── confidence_service.py # Confidence scoring for topic assignments
│   │   │   ├── confidence_policy_service.py
│   │   │   ├── academic_analytics/   # M5 analytics modules
│   │   │   │   ├── m5_marks_frequency_analyzer.py
│   │   │   │   ├── m5_importance_analyzer.py
│   │   │   │   ├── m5_dependency_analyzer.py
│   │   │   │   ├── m5_priority_analyzer.py   # M5.6: topological study-order sort
│   │   │   │   ├── m5_topic_aggregator.py
│   │   │   │   └── m5_result_loader.py
│   │   │   ├── llm_analysis/         # M3 question-to-syllabus analysis
│   │   │   │   ├── input_service.py
│   │   │   │   ├── question_analysis_service.py
│   │   │   │   └── syllabus_catalog_service.py
│   │   │   ├── m6_5/                 # M6.5 runtime topic explanation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── topic_explanation_service.py # Main M6.5 orchestrator
│   │   │   │   └── pyq_retrieval_service.py     # Reads enriched PYQ JSON files
│   │   │   └── recommendations/      # M6.3 study recommendations
│   │   │       ├── personalized_recommendation_service.py
│   │   │       ├── final_study_plan_service.py
│   │   │       ├── recommendation_input_service.py
│   │   │       └── topic_selector.py
│   │   ├── utils/                    # Empty directory
│   │   └── validators/
│   │       ├── question_output_validator.py
│   │       └── syllabus/
│   │           └── syllabus_structure_validator.py
│   ├── data/
│   │   └── cognee/                   # LanceDB vector store data directory
│   ├── uploads/
│   │   ├── syllabus/                 # Saved syllabus PDFs
│   │   ├── pyqs/                     # Saved PYQ PDFs
│   │   ├── notes/                    # Saved notes (organized by course_code/NOTES_id/)
│   │   └── temp/                     # OCR cache, parsed JSON, metadata, enriched PYQs
│   └── scripts/                      # Offline batch scripts (M1–M5 pipeline)
│       ├── parse_all_papers.py
│       ├── build_syllabus_index.py
│       ├── analyze_confidence_signals.py
│       ├── test_*.py
│       └── (m6_5/, rag/, llm_analysis/, recommendations/, academic_analytics/)
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                # port: 5173, no proxy configured
│   └── src/
│       ├── main.jsx                  # ENTIRE app in one file (2644 lines)
│       └── styles.css
└── docs/
    └── architecture.md               # Old draft (partially outdated)
```

---

## 4. Backend Architecture

### What is actually running vs. what exists as scripts

```
┌────────────────────────────────────────────────────┐
│            ONLINE  (FastAPI — actually running)     │
│                                                     │
│  POST /upload/syllabus  →  saves file to disk       │
│  POST /upload/pyq       →  saves file to disk       │
│  POST /api/notes/upload →  saves + creates metadata │
│  GET  /                 →  health check             │
│  GET  /health           →  health check             │
└─────────────────────────────┬──────────────────────┘
                              │
                              ▼
          All further processing is OFFLINE
          (run manually via scripts/ or test files)

┌────────────────────────────────────────────────────┐
│              OFFLINE PIPELINE (scripts/)            │
│                                                     │
│  M1: PDF → images → Ollama OCR → cleaned text      │
│  M2: metadata extraction, paper grouping,           │
│      syllabus parsing, LLM topic structuring        │
│  M3: question → syllabus mapping via Groq           │
│  M4: question enrichment + confidence scoring       │
│  M5: importance/dependency/priority analytics       │
│  M6.3: personalized recommendation (Groq)          │
│  M6.5: topic explanation (Cognee + Groq)           │
│                                                     │
│  OUTPUT: JSON files in uploads/temp/enriched/       │
│           and uploads/temp/parsed/                   │
└────────────────────────────────────────────────────┘
```

### Active FastAPI request flow (upload only)

```
React Frontend (port 5173)
        │
        │  multipart/form-data
        ▼
FastAPI (port 8000)
        │
        ├── POST /upload/syllabus
        │       └── UploadService.save_file()
        │               └── writes to uploads/syllabus/<filename>
        │
        ├── POST /upload/pyq
        │       └── UploadService.save_file()
        │               └── writes to uploads/pyqs/<filename>
        │
        └── POST /api/notes/upload
                └── normalize subject, validate PDFs
                └── UploadService.save_file() per file
                └── writes metadata.json per file
                └── returns NotesUploadResponse
```

### M6.5 service flow (offline / invoked from scripts)

```
topic_id, topic, subtopic, course_code, unit
        │
        ▼
M65TopicExplanationService.generate_explanation()
        │
        ├── Step 1: CogneeService.search()
        │       └── cognee.recall(query, dataset=cramwise_<CODE>,
        │                         query_type=CHUNKS, top_k=5,
        │                         auto_route=False, only_context=True)
        │               └── Returns list of text chunks from student's notes
        │
        ├── Step 2: M65PyqRetrievalService.retrieve()
        │       └── Reads JSON files from uploads/temp/enriched/*.json
        │       └── Filters by course_code + unit
        │       └── Ranks by keyword overlap with topic/subtopic
        │       └── Returns top-k enriched PYQ dicts
        │
        ├── Step 3: build_m65_user_prompt()
        │       └── Combines topic + notes chunks + PYQ text into prompt
        │
        └── Step 4: GroqClient.generate()
                └── model: openai/gpt-oss-120b
                └── Returns natural-language markdown explanation
```

---

## 5. API Endpoints

> **These are the ONLY endpoints that currently exist in the FastAPI application.**

| Method | Endpoint | Purpose | Request | Response | Frontend Connection |
|--------|----------|---------|---------|----------|--------------------|
| GET | `/` | Welcome / root | — | `{"message": "Welcome to CramWise!"}` | ✅ Used by `checkBackendConnection()` |
| GET | `/health` | Health check | — | `{"status": "healthy"}` | ❌ Not called from frontend |
| POST | `/upload/syllabus` | Save syllabus PDF | `multipart/form-data`: `file` (UploadFile) | `{"filename": str, "status": str}` | ❌ Upload UI exists but **does not call this** |
| POST | `/upload/pyq` | Save PYQ PDF | `multipart/form-data`: `file` (UploadFile) | `{"filename": str, "status": str}` | ❌ Upload UI exists but **does not call this** |
| POST | `/api/notes/upload` | Save notes PDF(s) | `multipart/form-data`: `files[]`, `subject` (str), `course_code` (str, optional) | `NotesUploadResponse` (JSON) | ❌ Upload UI exists but **does not call this** |

### What does NOT exist as an HTTP endpoint (yet)

| Functionality | Service / Code | Status |
|---------------|---------------|--------|
| Syllabus parsing + LLM topic structuring | `SyllabusParser`, `SyllabusTopic­Service` | Script only |
| PYQ OCR + parsing pipeline | `PDFToImages`, `OCRClient`, `QuestionParser` | Script only |
| M3 question analysis (topic mapping) | `QuestionAnalysisService` | Script only |
| M5 analytics (importance, priority, study order) | `M5Priority­Analyzer` etc. | Script only |
| M6.3 personalized recommendations | `M6Personalized­RecommendationService` | Script only |
| M6.5 topic explanation | `M65Topic­ExplanationService` | Script only — **no HTTP endpoint exists** |
| Cognee ingestion | `CogneeService.add_content()` | Script only |
| Chat / AI interaction | (not implemented) | Missing entirely |
| Subject listing | (not implemented) | Missing entirely |
| Analytics data | (not implemented) | Missing entirely |
| Study plan | (not implemented) | Missing entirely |
| PYQ explorer data | (not implemented) | Missing entirely |

---

## 6. Document Processing Pipeline

### 6.1 Syllabus Pipeline (Offline)

```
User uploads syllabus PDF
        │
        ▼
POST /upload/syllabus  →  saves to uploads/syllabus/<filename>
        │
        ▼  (manual script execution)
SyllabusParser.parse(pdf_path)
    │   ├── fitz.open() → extract text lines
    │   ├── split_into_courses()    # detects "Course Code" boundaries
    │   ├── extract_course_info()   # course_name, code, category, credits, semester
    │   ├── extract_units()         # UNIT-I … UNIT-V with hours + raw content
    │   └── extract_text_books() / extract_reference_books()
        │
        ▼
SyllabusTopicService.structure_unit(unit_content)
    └── calls LLM (via ParserClient / Groq) with syllabus_topic_prompt
    └── returns hierarchical topic + subtopic JSON
        │
        ▼
SyllabusIndexBuilder.build()
    └── creates flat index with topic_id, topic, subtopic, unit, course_code
    └── saves to JSON file (used by M3 + M6.3)
        │
        ▼
DatabaseLoader (optional)
    └── inserts Subject, Unit, Topic into PostgreSQL
```

### 6.2 PYQ Pipeline (Offline)

```
User uploads PYQ PDF
        │
        ▼
POST /upload/pyq  →  saves to uploads/pyqs/<filename>
        │
        ▼  (manual script execution)
PDFToImages.convert()
    └── fitz renders each page as JPEG (150 DPI, 1024×1024 max)
    └── saves to uploads/temp/images/<document>/page_N.jpg
        │
        ▼
OCRClient.get_cleaned_page(image_path)
    └── calls Ollama (maternion/LightOnOCR-2:1b at localhost:11434)
    └── TextCleaner.clean(raw_text)
    └── caches to uploads/temp/ocr/ and uploads/temp/cleaned/
        │
        ▼
MetadataExtractor.extract_page_identity()
    └── regex: exam_type (MIDTERM/ENDTERM), subject, subject_code, semester
        │
        ▼
PaperGrouper
    └── groups pages into individual exam papers
        │
        ▼
PaperTextBuilder
    └── assembles full paper text from cleaned pages
        │
        ▼
QuestionParser.get_questions(paper_id, paper_text)
    └── calls ParserClient (openai/gpt-oss-120b via Groq endpoint)
    └── uses QUESTION_PARSER_PROMPT
    └── returns list of question dicts
    └── validates with QuestionValidator
    └── caches to uploads/temp/parsed/<document>/<paper_id>_questions.json
        │
        ▼
QuestionEnricher  (M3 + M4)
    └── QuestionAnalysisService maps each question → topic_id via Groq
    └── enriched questions saved to uploads/temp/enriched/*.json
```

---

## 7. AI Architecture

### 7.1 Groq

| Property | Value |
|----------|-------|
| SDK | `groq` Python package (v0.37.1) |
| API key source | `GROQ_API_KEY` environment variable (loaded via `python-dotenv`) |
| Model | `openai/gpt-oss-120b` (set in `.env` as `LLM_MODEL`) |
| Client class | `app/clients/groq_client.py → GroqClient` |
| `generate()` | Plain text generation: `chat.completions.create()` |
| `generate_json()` | Structured output: `response_format = {"type": "json_schema", "json_schema": {..., "strict": True}}` |
| Retries | `max_retries=2`, `retry_delay=2.0s` by default |
| Token limit | `max_completion_tokens=6000` default; M6.5 uses 3500 |

**Who calls Groq:**
- `SyllabusTopicService` — structures raw unit content into topics/subtopics
- `QuestionParser` (via `ParserClient`) — extracts questions from OCR text
- `QuestionAnalysisService` (M3) — maps questions to syllabus topics
- `M65TopicExplanationService` (M6.5) — generates topic explanation
- `M6PersonalizedRecommendationService` (M6.3) — selects study topics

### 7.2 Cognee

| Property | Value |
|----------|-------|
| Version | 1.5.1 |
| Config | `.env`: `LLM_PROVIDER=groq`, `EMBEDDING_PROVIDER=fastembed`, `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5`, `VECTOR_DB_PROVIDER=lancedb` |
| Data directory | `C:/Users/vaish/CramWise_vaishi/backend/data/cognee` (from `.env`) |
| Dataset naming | `cramwise_<COURSE_CODE>` e.g. `cramwise_BCS306` |
| Ingestion | `cognee.remember(data, dataset_name, run_in_background=False)` |
| Retrieval | `cognee.recall(query_text, query_type=SearchType.CHUNKS, datasets=[...], top_k=5, auto_route=False, only_context=True)` |

**CramWise deliberately uses `SearchType.CHUNKS` instead of `GRAPH_COMPLETION_COT`** to prevent Cognee from triggering additional LLM reasoning (which would hit Groq TPM limits).

**Is Cognee grounding actually working?**
The code in `CogneeService` and `M65TopicExplanationService` correctly calls `cognee.remember()` (for ingestion) and `cognee.recall()` (for retrieval). **However:** there is no HTTP endpoint that calls `cognee.remember()` — ingestion is also script-only. If no notes have been ingested yet, M6.5 will receive an empty context list and the prompt will say `"No relevant student-note context was retrieved from Cognee."`. Groq will still generate a response, but without grounding.

### 7.3 M6.5 Topic Explanation

```
Input:  topic_id, topic, subtopic, course_code, unit
   │
   ├── Cognee CHUNKS retrieval  (student notes → relevant text chunks)
   ├── PYQ keyword-match retrieval  (enriched JSON files → top-k PYQs)
   ├── Prompt construction  (build_m65_user_prompt)
   │
   └── Groq generate()  →  markdown teaching response
```

The system prompt (`M65_SYSTEM_PROMPT`) instructs Groq to: teach the topic from scratch, ground the explanation in the retrieved notes, apply every relevant PYQ specifically, use markdown, and NOT return JSON.

---

## 8. Frontend Architecture

### 8.1 Overview

| Property | Value |
|----------|-------|
| Entry point | `frontend/index.html` → `src/main.jsx` |
| Framework | React 18 SPA, single file (2644 lines) |
| Routing | None (React Router not installed). Navigation via `useState(page)` |
| State | All local `useState` inside `App()`. No Redux, no Zustand, no Context. |
| API base URL | `const API_BASE_URL = "http://127.0.0.1:8000"` (hardcoded, line 38) |
| Backend check | `checkBackendConnection()` calls `GET /` on mount; shows status dot in UI |
| Theme | Light/dark toggle via `dark` class on root `<div>` |
| Icons | lucide-react |

### 8.2 Pages

| Page key | Component | Description |
|----------|-----------|-------------|
| `dashboard` | `Dashboard` | Overview: subjects grid, priority topics, preparation ring, frequent PYQs |
| `subjects` | `Subjects` | Single subject view: progress, unit heatmap, topic cards list |
| `analytics` | `Analytics` | Bar charts for priority distribution, PYQ frequency, unit importance |
| `plan` | `StudyPlan` | Timeline of recommended study sessions with start buttons |
| `pyqs` | `PYQs` | PYQ explorer: search/filter UI + list of questions |
| `upload` | `UploadContent` | Three upload cards: Syllabus, PYQ, Notes — file picker only |
| `chat` | `Chat` | Chat interface with backend connection comment placeholder |

### 8.3 Components

| Component | Purpose |
|-----------|---------|
| `NavItem` | Sidebar navigation button |
| `Stat` | Stat card (icon, label, value, note) |
| `SubjectCard` | Subject overview card with progress bar |
| `TopicRow` | Topic row in priority list |
| `PYQCard` | PYQ question card |
| `MiniMetric` | Small label+value pair |
| `Ring` | Circular progress ring |
| `UnitBar` | Unit progress bar |
| `Bar` | Analytics vertical bar |
| `UnitImportance` | Unit importance card |
| `PlanItem` | Study plan timeline item |
| `UploadCard` | Upload dropzone + file picker |
| `TopicDrawer` | Slide-in drawer showing topic details |

### 8.4 Mock / Hardcoded Data

The following data is **hardcoded** at the top of `main.jsx`:

```js
const subjects = [
  { code: "BCS 306", name: "Compiler Design", progress: 68, pyqs: 32, topics: 17, high: 5 },
  { code: "BCS 302", name: "Wireless Networks", progress: 42, ... },
  { code: "BCS 304", name: "Cloud Computing", progress: 81, ... },
];

const topics = [
  { name: "Bottom-Up Parsing", unit: "Unit 2", priority: "HIGH", pyqs: 8, marks: 35, progress: 0 },
  ...
];

const repeated = [
  { question: "Describe the design goals...", count: 5, marks: 10, unit: 1 },
  ...
];
```

All pages render this hardcoded data. No page fetches real data from the backend except the single `GET /` health check.

---

## 9. Frontend ↔ Backend Connection Map

| Frontend Feature | React Component | API Endpoint | Backend Function | Status |
|------------------|-----------------|--------------|------------------|--------|
| Backend health indicator | `App` → `checkBackendConnection()` | `GET /` | `root()` in main.py | ✅ **Connected** |
| Syllabus upload | `UploadCard` (title="Syllabus") | `POST /upload/syllabus` | `upload_syllabus()` | ❌ **File picker only — no fetch call** |
| PYQ upload | `UploadCard` (title="Previous Year Questions") | `POST /upload/pyq` | `upload_pyq()` | ❌ **File picker only — no fetch call** |
| Notes upload | `UploadCard` (title="Notes") | `POST /api/notes/upload` | `upload_notes()` | ❌ **File picker only — no fetch call** |
| Dashboard subjects | `Dashboard` → `SubjectCard` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Dashboard stats | `Dashboard` → `Stat` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Priority topics | `Dashboard` → `TopicRow` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Frequent PYQs | `Dashboard` → `PYQCard` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Subject overview | `Subjects` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Analytics charts | `Analytics` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Study plan | `StudyPlan` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| PYQ explorer | `PYQs` | None (needed) | None (needed) | ❌ **Hardcoded mock** |
| Topic drawer explanation | `TopicDrawer` | None (needed → M6.5) | `M65TopicExplanationService` | ❌ **Static placeholder text** |
| Chat (CramWise Ask) | `Chat` → `send()` | None (no endpoint exists) | None (not implemented) | ❌ **Sends to itself, returns static message** |

---

## 10. Missing Connections

### 10.1 Upload buttons (Quick wins — endpoints already exist)

| Frontend Feature | Backend Endpoint | What's Missing |
|-----------------|-----------------|----------------|
| Syllabus upload button | `POST /upload/syllabus` | `fetch()` call in `UploadCard` for the Syllabus card |
| PYQ upload button | `POST /upload/pyq` | `fetch()` call in `UploadCard` for the PYQ card |
| Notes upload button | `POST /api/notes/upload` | `fetch()` call in `UploadCard` for the Notes card; also needs `subject` + `course_code` form fields |

### 10.2 Data endpoints (Need to be created)

| Frontend Feature | Endpoint (to create) | Backend Logic Available |
|-----------------|---------------------|-------------------------|
| Subjects list | `GET /api/subjects` | M5 JSON output files; PostgreSQL |
| Subject detail | `GET /api/subjects/{code}` | M5 JSON files |
| Topics for subject | `GET /api/subjects/{code}/topics` | M5 priority analytics JSON |
| Analytics data | `GET /api/analytics/{code}` | M5 marks/frequency/importance analytics |
| Study plan | `GET /api/study-plan` | M6.3 `PersonalizedRecommendationService` |
| PYQ list | `GET /api/pyqs` | Enriched PYQ JSON files in `uploads/temp/enriched/` |
| Topic explanation (M6.5) | `POST /api/explain` | `M65TopicExplanationService` |
| Chat / general question | `POST /api/chat` | Not implemented |

### 10.3 Architectural issues to fix before connecting

| Issue | Detail | Severity |
|-------|--------|----------|
| **No CORS middleware** | FastAPI has no `CORSMiddleware`. React (port 5173) calling FastAPI (port 8000) will be blocked by the browser. | 🔴 Critical — must fix first |
| **No proxy in Vite** | `vite.config.js` has no `server.proxy`. All frontend calls hit `http://127.0.0.1:8000` directly. CORS error will block everything. | 🔴 Critical |
| **API_BASE_URL hardcoded** | `const API_BASE_URL = "http://127.0.0.1:8000"` hardcoded in `main.jsx`. No `.env` support. Acceptable for development; needs a Vite env variable for production. | 🟡 Medium |
| **Upload buttons not wired** | All three `UploadCard` upload buttons are disabled when no file is selected and call nothing when clicked. | 🟡 Medium |
| **No loading/error state for uploads** | `UploadCard` has no `loading` or `error` state. | 🟡 Medium |
| **M6.5 has no HTTP endpoint** | `M65TopicExplanationService.generate_explanation()` exists but there is no router that exposes it. | 🟡 Medium |
| **Chat has no backend** | The `Chat.send()` function has a placeholder comment instead of a real `fetch()` call. No `/api/chat` endpoint exists. | 🟡 Medium |
| **Cognee ingestion not automated** | Notes are saved to disk but never ingested into Cognee on upload. M6.5 grounding will fail without ingestion. | 🟡 Medium |
| **PostgreSQL defined but unused** | `db/database.py` and `db/models.py` exist, but no active router uses them. | 🟢 Low — decide whether to use DB or JSON files |
| **All analytics/subjects data is mock** | Frontend displays made-up data. No API to return real M5 output. | 🟡 Medium |
| **Single-file frontend** | 2644-line `main.jsx` will be hard to maintain. Not blocking, but worth noting. | 🟢 Low |

---

## 11. Recommended Fix Order (Before Connecting)

These are the steps you should take **in order**, before connecting any frontend feature:

1. **Add CORS middleware to FastAPI** — without this, nothing will work from the browser.

2. **Wire the three upload buttons** to their existing endpoints (`/upload/syllabus`, `/upload/pyq`, `/api/notes/upload`) — these are the quickest wins.

3. **Add Notes ingestion to Cognee after upload** — when `POST /api/notes/upload` succeeds, call `CogneeService.add_content()` so M6.5 grounding actually works.

4. **Create `POST /api/explain`** — expose `M65TopicExplanationService.generate_explanation()` as an HTTP endpoint so the Topic Drawer can call it.

5. **Create `GET /api/subjects`** and related data endpoints — serve M5 analytics JSON through the API so the dashboard/analytics/study-plan pages show real data.

6. **Wire the Chat page** — create `POST /api/chat` that can either call M6.5 (for topic explanations) or return appropriate responses.

7. **Replace all hardcoded mock data** in the frontend with real API calls.

8. **(Optional) Add Vite proxy** — configure `vite.config.js` to proxy `/api` to `http://127.0.0.1:8000` instead of using a hardcoded base URL. This also makes CORS less critical during development.
