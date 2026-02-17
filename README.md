# Google Langextract POC

A FastAPI-based service that analyzes documents (PDF, DOCX, TXT) and extracts intelligent insights based on document type using Google Langextract.

## ✨ Latest Updates

- ✅ **Entity Deduplication** - No more duplicate entities! Each entity appears once with mention count
- ✅ **Executive Summary** - Get a high-level overview of your document instantly
- ✅ **Key Insights** - Quick bullet-point highlights of important information
- ✅ **Professional Reports** - Enhanced structure with organized categories
- ✅ **Smart Sorting** - Entities sorted by importance and mention frequency
- ✅ **Streamlit Frontend** - User-friendly web interface with PDF viewer

## Features

- Automatic document type classification (story, meeting, research, technical, legal)
- Context-aware extraction using langextract + Gemini
- Deduplicated entities with mention tracking
- Executive summaries for quick understanding
- Key insights highlighting important information
- Streamlit web interface with embedded PDF viewer
- Professional PDF reports with enhanced structure
- Structured JSONL data output
- RESTful API with async processing

## Quick Start

### Option 1: Backend Only

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
# Edit .env and add your GEMINI_API_KEY

# Run
uvicorn app.main:app --reload
```

### Option 3: Frontend Only

```bash
cd frontend

# Windows
streamlit run app.py
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Run the application:

## Using the Frontend

1. Open http://localhost:8501 in your browser
2. Upload a document (PDF, DOCX, or TXT)
3. Click "Analyze Document"
4. View the embedded PDF report
5. Explore extracted entities
6. Download PDF or JSONL data

## Using the API

### Upload and Analyze Document

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Download PDF Report

```bash
curl -X GET "http://localhost:8000/api/v1/report/{job_id}" \
  --output report.pdf
```

### Download JSONL Data

```bash
curl -X GET "http://localhost:8000/api/v1/data/{job_id}" \
  --output data.jsonl
```

## Supported Document Types

- Story/Narrative
- Meeting Transcript
- Research Paper
- Technical Documentation
- Legal Document
- General (fallback)
