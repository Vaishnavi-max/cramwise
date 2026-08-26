# CramWise — Implementation Log

> This document records every completed implementation step.  
> Each step follows: DISCUSS → APPROVE → IMPLEMENT → TEST → DOCUMENT.  
> No step is claimed as complete unless it was actually tested.

---

## Step 0 — Fix QuestionParser Duplicate Imports

### Problem

[question_parser.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/parsers/question_parser.py) had **duplicate import blocks**:
- Lines 1–6: First set of imports (`Path`, `json`, `logging`, `ParserClient`, `QUESTION_PARSER_PROMPT`)
- Lines 7–19: Identical second set of the same imports, plus the corrected `QuestionOutputValidator` import

This was leftover from a partial patch. Every import statement appeared twice, making the file confusing and suggesting it might still be broken.

### Decision

Remove the duplicate import block (lines 1–6). Keep only the clean second block (lines 7–19) which includes all necessary imports with proper comments.

### Files Read

| File | Purpose |
|------|---------|
| [question_parser.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/parsers/question_parser.py) | The file being fixed — verified exact current state |
| [question_output_validator.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/validators/question_output_validator.py) | Verified class name `QuestionOutputValidator` and `validate(questions, exam_type)` signature |
| [parser_client.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/parsers/parser_client.py) | Verified `ParserClient` class and `parse(text, prompt)` method |
| [parser_prompt.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/parsers/parser_prompt.py) | Verified `QUESTION_PARSER_PROMPT` exists and uses `"part"` field in output schema |

### Files Changed

| File | What Changed |
|------|-------------|
| [question_parser.py](file:///c:/Users/vaish/CramWise_vaishi/backend/app/parsers/question_parser.py) | Removed duplicate import block (lines 1–6); improved comments on all imports and on the `part` → `sub_question` normalization block |

### Files Created

| File | Purpose |
|------|---------|
| [IMPLEMENTATION_LOG.md](file:///c:/Users/vaish/CramWise_vaishi/IMPLEMENTATION_LOG.md) | This implementation log (required by development process) |

### Implementation

1. Removed the duplicate import block at the top of the file (6 lines)
2. Kept the clean import block with:
   - `ParserClient` — Groq LLM communication
   - `QUESTION_PARSER_PROMPT` — LLM prompt template
   - `QuestionOutputValidator` — structural validation
3. Added descriptive comments on each import explaining what it does and why
4. Improved the comment on the `part` → `sub_question` normalization to explain the architectural reason: the LLM prompt outputs `"part"` but downstream consumers expect `"sub_question"`
5. **No logic was changed** — all behavior is identical

### Architecture After Step

No architectural change. The data flow remains:

```
Paper OCR text
    ↓
QuestionParser.get_questions()
    ↓ (cache check)
ParserClient.parse() → Groq LLM
    ↓
Cache to uploads/temp/parsed/{doc}/{paper_id}_questions.json
    ↓
QuestionOutputValidator.validate()
    ↓
Normalize "part" → "sub_question"
    ↓
Return cleaned question list
```

### Dependencies

No dependencies added or removed.

### Verification

```bash
# Test 1: QuestionParser imports cleanly
python -c "from app.parsers.question_parser import QuestionParser; print('QuestionParser import OK')"
# Result: QuestionParser import OK ✅

# Test 2: QuestionOutputValidator imports cleanly  
python -c "from app.validators.question_output_validator import QuestionOutputValidator; print('QuestionOutputValidator import OK')"
# Result: QuestionOutputValidator import OK ✅
```

### Result

Both imports succeed with exit code 0. The file is clean with no duplicate imports.

### Known Limitations

- The `QuestionOutputValidator` has hardcoded exam structure expectations (MIDTERM: Q1-Q3, ENDTERM: Q1-Q9) — this will be addressed in Step 5
- The `"part"` vs `"sub_question"` naming inconsistency exists across the pipeline — this is a known schema issue to be addressed in Step 5
- The `ParserClient` uses `print()` statements instead of `logging` — not in scope for Step 0

---

## Step 1 — Complete Syllabus Ingestion Pipeline

### Problem

The live syllabus upload flow stopped after OCR and raw course/unit extraction. Creating `syllabus_raw.json`, structuring topics, validating that structure, and producing `syllabus_index.json` still required separate manual scripts.

### Decision

Keep JSON as the primary storage format and connect the existing OCRmyPDF, parsing, topic-structuring, validation, and indexing services in `SyllabusPipelineService`. Reuse `OCRmyPDFClient` rather than maintaining a duplicate OCRmyPDF subprocess implementation. Background processing is intentionally deferred to the separately approved Step 12.

### Files Read

| File | Purpose |
|------|---------|
| `backend/app/routers/upload.py` | Confirmed the existing syllabus upload response expects a list of courses. |
| `backend/app/services/syllabus_pipeline_service.py` | Identified the incomplete two-stage pipeline and duplicated OCR command. |
| `backend/app/extraction/ocrmypdf_client.py` | Verified cache-aware OCRmyPDF + Tesseract support. |
| `backend/app/parsers/syllabus_parser.py` | Verified raw course/unit extraction contract. |
| `backend/app/services/syllabus_topic_service.py` | Verified per-unit topic structuring and checkpoint behavior. |
| `backend/app/validators/syllabus/syllabus_structure_validator.py` | Verified structural validation contract. |
| `backend/app/services/syllabus_index_builder.py` | Verified flat index creation and JSON persistence. |
| `backend/scripts/test_syllabus_topic_all.py` | Verified the previous manual topic-structuring flow. |
| `backend/scripts/build_syllabus_index.py` | Verified the previous manual index-building flow. |

### Files Changed

| File | What Changed |
|------|-------------|
| `backend/app/services/syllabus_pipeline_service.py` | Orchestrates every syllabus stage, writes JSON artifacts, validates before indexing, and reuses the shared OCR client. |
| `IMPLEMENTATION_LOG.md` | Records the approved implementation and verification. |

### Files Created

None.

### Implementation

1. Replaced the duplicated inline OCRmyPDF subprocess code with `OCRmyPDFClient`.
2. Store new OCR outputs in `uploads/temp/ocr_pdfs/<name>_ocr.pdf`.
3. Retain compatibility with the previous `uploads/syllabus/<name>_ocr.pdf` cache location, so existing OCR results are reused instead of rerunning Tesseract.
4. Persist raw parser output to `uploads/temp/syllabus/syllabus_raw.json` before topic structuring begins.
5. Run `SyllabusTopicService` to create `syllabus_structure.json` while preserving its existing unit-level checkpoints.
6. Validate the hierarchy and stop the pipeline before index creation if it is invalid.
7. Build and persist `uploads/temp/syllabus/syllabus_index.json` only from validated structure data.
8. Preserve the existing upload endpoint's list response, avoiding an unapproved API-contract change.

### Architecture After Step

```text
POST /upload/syllabus
    ↓
Save original PDF
    ↓
Reuse cached OCR PDF or OCRmyPDF + Tesseract
    ↓
PyMuPDF extraction + Groq raw course/unit parsing
    ↓
syllabus_raw.json
    ↓
Groq topic structuring (checkpointed per unit)
    ↓
syllabus_structure.json
    ↓
SyllabusStructureValidator
    ↓
SyllabusIndexBuilder
    ↓
syllabus_index.json
```

### Dependencies

No dependencies were added or removed.

### Verification

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& '..\.venv\Scripts\python.exe' -m py_compile app\services\syllabus_pipeline_service.py
& '..\.venv\Scripts\python.exe' -c "<isolated pipeline orchestration assertions with stub OCR, parser, and topic services>"
git diff --check
```

The isolated orchestration test asserted all three JSON outputs, the generated index ID (`TST101_U1_T01_S01`), and legacy OCR-cache reuse. It made no Groq request and did not OCR a user PDF.

### Result

The complete syllabus ingestion pipeline now runs from the existing upload flow and produces the JSON artifacts used by later pipeline stages.

### Known Limitations

- The upload request still waits for OCR and LLM processing. This is intentionally deferred to Step 12, where processing status and background execution will be designed and approved.
- JSON filenames are currently global (`syllabus_raw.json`, `syllabus_structure.json`, and `syllabus_index.json`), so processing a different syllabus replaces the current active syllabus dataset. Multi-syllabus storage needs a separate approved data-model decision.
