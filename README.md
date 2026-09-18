# CramWise

> **An AI-powered academic intelligence platform for smarter exam preparation.**

CramWise transforms scattered academic resources such as **syllabi, previous-year question papers, notes, assignments, and books** into structured and searchable academic knowledge.

The goal is to build an intelligent system that can understand a student's academic ecosystem, identify important and repeated topics, answer questions using relevant study material, analyze exam patterns, and eventually provide personalized study recommendations.

## 🚀 Vision

```text
Academic Documents
        ↓
Document Intelligence
        ↓
Structured Academic Knowledge
        ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
Search      Analytics      Knowledge Graph
│              │              │
└──────────────┴───────┬──────┘
                       ↓
                    AI Tutor
                       ↓
              Personalized Learning
                       ↓
                    CramWise
```

CramWise is designed as a **modular and scalable system**, where individual components can be developed, tested, and improved independently and later integrated into the complete platform.

---

## 🧩 Core Components

### 1. Document Intelligence Engine

Converts raw academic documents into structured information.

```text
PDF
 ↓
PDF → Images
 ↓
OCR
 ↓
Text Cleaning
 ↓
Metadata Extraction
 ↓
Document Classification
 ↓
Structure Detection
 ↓
Question / Syllabus Parsing
 ↓
Validation
 ↓
Structured JSON
```

### 2. Academic Knowledge Repository

Stores structured academic information such as:

* Documents
* Subjects
* Syllabus units
* Topics
* Questions
* Course Outcomes
* Exam metadata

**Planned:** PostgreSQL

### 3. Embedding Service

Converts academic content into vector representations for semantic retrieval.

**Planned:** Sentence Transformers / FastEmbed + BGE models

### 4. Search Engine

Retrieves relevant questions, topics, notes, and other academic content using semantic and hybrid search.

**Planned:**

* Vector Search
* BM25
* Hybrid Retrieval
* Cross-Encoder Reranking

### 5. Analytics Engine

Analyzes historical examination data to identify:

* Repeated questions
* Important topics
* Unit-wise frequency
* Marks distribution
* Question trends

### 6. AI Tutor / RAG Engine

Uses retrieved academic context to generate grounded answers.

```text
Student Question
       ↓
Search
       ↓
Relevant Academic Content
       ↓
LLM
       ↓
Context-Aware Answer
```

### 7. Recommendation Engine

Combines academic analytics with student progress to provide personalized preparation recommendations.

### 8. Student Progress Engine

Tracks:

* Completed topics
* Completed units
* Quiz performance
* Revision history
* Bookmarks
* Study sessions

### 9. Frontend

Provides the student-facing interface for:

* Academic search
* AI tutoring
* PYQ exploration
* Analytics
* Syllabus tracking
* Study recommendations

---

## 🔄 Complete Data Flow

```text
                    Academic Documents
                           ↓
                Document Intelligence
                           ↓
                 Structured Documents
                           ↓
                Academic Knowledge Base
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       Embedding Service          Analytics Engine
              ↓                         ↓
         Vector Store             Academic Insights
              └────────────┬────────────┘
                           ↓
                     Search Engine
                           ↓
                       AI Tutor
                           ↓
                 Recommendation Engine
                           ↓
                  Student Progress
                           ↓
                    CramWise Frontend
```

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Pydantic

### Document Processing

* PDF processing
* OCR
* OCRmyPDF
* Ollama
* LLM-based extraction

### LLM

* Ollama
* Groq
* OpenAI-compatible APIs

### Embeddings

* Sentence Transformers / FastEmbed
* BAAI/bge-large-en-v1.5

### Database

* PostgreSQL

### Vector Search

* FAISS

### Frontend

* React

---

## 📦 Current Implementation

The current development focus is the **Academic Document Intelligence / Parsing Pipeline**.

### Implemented

* PDF to image conversion
* OCR extraction
* OCR cleaning
* Metadata extraction
* Syllabus parsing
* PYQ parsing
* Question validation
* Intermediate-result caching
* LLM-based question analysis
* Individual pipeline testing and debugging

### In Progress

* Reliable question extraction
* Question chunking
* Improved validation
* Marks normalization
* Course Outcome normalization
* Malformed LLM output handling
* Retry and error handling

### Planned

* Knowledge Repository
* Embedding Service
* Hybrid Search
* RAG Pipeline
* Analytics Engine
* Recommendation Engine
* Student Progress Engine
* Frontend Dashboard

---

## 📁 Project Structure

```text
CramWise/
│
├── backend/
│   ├── app/
│   │   ├── clients/
│   │   ├── extraction/
│   │   ├── parsers/
│   │   ├── prompts/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── validators/
│   │
│   ├── scripts/
│   └── uploads/
│
├── IMPLEMENTATION_LOG.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file locally using `.env.example`.

Example:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cramwise

GROQ_API_KEY=your_api_key

LLM_PROVIDER=groq
LLM_MODEL=your_model
LLM_API_KEY=your_api_key
LLM_ENDPOINT=https://api.groq.com/openai/v1

EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
EMBEDDING_DIMENSIONS=1024
```

**Never commit `.env` or API keys to the repository.**

---

## 🗺️ Roadmap

* [x] PDF processing
* [x] OCR pipeline
* [x] OCR cleaning
* [x] Metadata extraction
* [x] Initial syllabus parsing
* [x] Initial PYQ parsing
* [x] Validation layer
* [x] Processing cache
* [ ] Robust document intelligence engine
* [ ] Academic knowledge repository
* [ ] Embedding service
* [ ] Hybrid search
* [ ] Cross-encoder reranking
* [ ] RAG-based AI tutor
* [ ] PYQ analytics
* [ ] Recommendation engine
* [ ] Student progress tracking
* [ ] CramWise dashboard

---

## 🎯 Long-Term Goal

CramWise aims to evolve from a document-processing system into a complete **academic intelligence platform** that understands:

```text
What is in the syllabus?
        +
What has been asked before?
        +
What topics are important?
        +
What does the student already know?
        +
What should the student study next?
```

Ultimately:

> **CramWise turns scattered academic resources into an intelligent system that can search, analyze, teach, and personalize exam preparation.**
