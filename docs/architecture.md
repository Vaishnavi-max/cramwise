# CramWise Architecture & Pipeline Documentation

## 1. Project Overview
CramWise is an AI-powered academic knowledge platform designed to help students prepare for exams. It analyzes university syllabi and previous year question papers (PYQs) using Retrieval-Augmented Generation (RAG), semantic search, and Large Language Models (LLMs). By mapping questions to syllabus units and identifying important topics, it provides structured insights for effective studying.

## 2. High-Level Architecture
The project follows a modular, pipeline-driven architecture consisting of the following key layers:

### A. API Layer (FastAPI)
The entry point for the application. It handles incoming requests for file uploads (Syllabi and PYQs).
- **Core file:** `backend/app/main.py`
- **Routers:** `backend/app/routers/upload.py`

### B. Storage & Database Layer
Uses PostgreSQL (via SQLAlchemy) to store structured academic data such as Subjects, Units, Topics, Books, and Questions.
- **Core files:** `backend/app/db/database.py`, `backend/app/db/models.py`

### C. Extraction & Parsing Layer (The Pipeline)
This is where the core logic resides. It converts unstructured PDFs (Syllabi & PYQs) into structured JSON data.
- **Extraction:** PyMuPDF (`fitz`) and OCR are used to extract raw text from uploaded files.
- **Parsing (LLM-driven):** The raw text is passed to an LLM via `ParserClient` (using OpenAI-compatible endpoints) which structures the raw text into distinct entities like units, topics, and individual questions safely using specific prompts.

### D. RAG & Search Layer
Implements various retrieval mechanisms to establish connections between past questions and syllabus topics.
- **Keywords/Services:** FAISS/Chroma for vector stores, Sentence Transformers for embeddings, BM25 for keyword search, Cross-Encoder for re-ranking, and Hybrid Retrieval.

---

## 3. Data Pipelines

### Pipeline 1: Syllabus Processing
1. **Upload:** User uploads a syllabus PDF (`/upload/syllabus`).
2. **Text Extraction:** `pdf_to_images.py` / `SyllabusParser` extracts text from the PDF pages.
3. **Course Splitting:** Identifies different courses, subjects, units, and textbooks.
4. **LLM Structuring:** `SyllabusTopicService` invokes the LLM (`SyllabusTopicPrompt`) to accurately map out raw text into specific, hierarchical topic structures (Topics and Sub-topics).
5. **Database Storage:** Saves structured Subjects, Units, and Topics into PostgreSQL.

### Pipeline 2: PYQ (Previous Year Question) Processing
1. **Upload:** User uploads PYQ PDFs (`/upload/pyq`).
2. **OCR / Text Building:** `PaperTextBuilder` integrates pages and uses OCR to extract text from papers.
3. **Question Parsing:** `QuestionParser` reads the paper content and uses LLM (`QuestionParserPrompt`) to extract individual questions, question numbers, marks, etc.
4. **Validation:** `QuestionValidator` ensures the extracted json conforms to expected data structures.
5. **Enrichment & Mapping:** Questions are evaluated and mapped to syllabus units using embedding services and semantic search.

---

## 4. Directory & File Breakdown

### `backend/app`
- **`main.py`**: Initializes the FastAPI application and mounts routers.
- **`routers/`**: Contains API endpoints (e.g., `upload.py` for `/upload/syllabus` and `/upload/pyq`).

### `backend/app/db`
- **`database.py`**: SQLAlchemy database connection and session management.
- **`models.py`**: Defines the ORM schemas (`Subject`, `Unit`, `Topic`, `TextBook`, `ReferenceBook`).

### `backend/app/extraction`
Handles initial raw text and image extraction.
- **`ocr_client.py` & `ocr_prompt.py`**: Interfaces with OCR services to turn images of exams into text.
- **`pdf_to_images.py`**: Converts PDF pages into images for OCR.
- **`text_cleaner.py`**: Cleans extracted text to improve LLM parsing quality.

### `backend/app/parsers`
Contains logic for structuring extracted text using LLMs.
- **`syllabus_parser.py`**: Splits syllabus PDFs into courses, units, and textbook lists.
- **`question_parser.py`**: Sends OCR text of exam papers to the LLM to meticulously extract individual questions.
- **`parser_client.py`**: A unified client wrapper over the LLM (`openai/gpt-oss-120b`).
- **`metadata_extractor.py`**: Extracts context about exams (course code, semester, year).
- **`exam_type_classifier.py`**: Classifies if the exam is Midterm, Endterm, etc.

### `backend/app/services`
Core business logic and integration of the pipeline steps.
- **`paper_question_parser.py`**: Orchestrates `PaperTextBuilder` and `QuestionParser` for a complete paper.
- **`syllabus_topic_service.py`**: Iterates over syllabus units and uses LLMs to structure them contextually.
- **`embedding_service.py` & `chroma_service.py`**: Generates and manages vector embeddings for semantic search.
- **`bm25_service.py` & `hybrid_retrieval_service.py`**: Implements keyword matching and combines it with vector search to reliably match questions to syllabus topics.
- **`confidence_service.py`**: Evaluates the model's confidence when predicting bindings between questions and syllabus topics.
- **`question_enricher.py`**: Enriches fundamental questions with more data like Bloom's taxonomy mapping or CO mapping.

### `backend/app/validators`
- **`question_output_validator.py`**: Validates the output format from the LLM to ensure structural integrity and correct types before database insertion.

### `backend/scripts`
Standalone scripts used for running batch jobs, initializations, and tests.
- **`parse_all_papers.py`**: Bulk processes PYQs, iterating over a batch of papers and saving structured results.
- **`build_syllabus_index.py` & `build_chroma_syllabus.py`**: Indexing scripts to populate FAISS/Chroma to set up semantic search environments.
- **`test_*.py`**: Assorted test scripts validating different nodes in the pipeline (OCR, BM25, cross-encoder, grouping, text_builder).

## 5. Conclusion
CramWise represents a highly robust data funnel: normalizing vastly different unstructured source materials—textual syllabi and image-heavy exam papers—into highly structured schema stored in PostgreSQL, and intelligently interlinking them utilizing FAISS, Semantic Similarity, and RAG.
