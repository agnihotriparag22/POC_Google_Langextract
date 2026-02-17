"""Document Analysis API Routes"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.schemas import AnalyzeResponse, ExtractionItem
from app.services.document_parser import parse_document
from app.services.classifier import classify_document
from app.services.extractor import extract_insights
from app.services.report_generator import generate_pdf_report
from app.utils.file_handler import save_upload_file, cleanup_old_files

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze uploaded document and extract intelligent insights
    
    - Accepts PDF, DOCX, TXT files
    - Returns structured analysis with PDF report and JSONL data
    """
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = await save_upload_file(file, job_id)
        
        # Parse document
        text = parse_document(file_path, file_ext)
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Document appears to be empty or too short"
            )
        
        # Classify document type
        classification = classify_document(text)
        
        # Extract insights
        extraction_result = extract_insights(text, classification.document_type)
        
        # Generate PDF report
        report_path = generate_pdf_report(
            extractions=extraction_result.extractions,
            doc_type=classification.document_type,
            job_id=job_id,
            filename=file.filename,
            classification=classification,
            document_text=text[:1000]  # First 1000 chars for context
        )
        
        # Save JSONL data
        jsonl_path = os.path.join(settings.REPORT_DIR, job_id, "data.jsonl")
        import langextract as lx
        lx.io.save_annotated_documents(
            [extraction_result],
            output_name="data.jsonl",
            output_dir=os.path.join(settings.REPORT_DIR, job_id)
        )
        
        # Generate summary
        summary = _generate_summary(extraction_result.extractions, classification.document_type)
        
        # Cleanup old files
        await cleanup_old_files()
        
        return AnalyzeResponse(
            job_id=job_id,
            document_type=classification.document_type,
            confidence=classification.confidence,
            summary=summary,
            extraction_count=len(extraction_result.extractions),
            extractions=[
                ExtractionItem(
                    extraction_class=e.extraction_class,
                    extraction_text=e.extraction_text,
                    attributes=e.attributes or {}
                )
                for e in extraction_result.extractions
            ],
            pdf_url=f"/api/v1/report/{job_id}",
            jsonl_url=f"/api/v1/data/{job_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Analysis failed: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to console
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/report/{job_id}")
async def get_report(job_id: str):
    """Download PDF report for a job"""
    report_path = os.path.join(settings.REPORT_DIR, job_id, "report.pdf")
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=f"analysis_{job_id}.pdf"
    )


@router.get("/data/{job_id}")
async def get_data(job_id: str):
    """Download JSONL data for a job"""
    data_path = os.path.join(settings.REPORT_DIR, job_id, "data.jsonl")
    
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found")
    
    return FileResponse(
        data_path,
        media_type="application/jsonl",
        filename=f"data_{job_id}.jsonl"
    )


def _generate_summary(extractions: list, doc_type: str) -> str:
    """Generate a brief summary from extractions"""
    if not extractions:
        return "No significant insights extracted from the document."
    
    count_by_class = {}
    for e in extractions:
        count_by_class[e.extraction_class] = count_by_class.get(e.extraction_class, 0) + 1
    
    summary_parts = [f"Analyzed as {doc_type.upper()} document."]
    summary_parts.append(f"Extracted {len(extractions)} entities:")
    
    for cls, count in count_by_class.items():
        summary_parts.append(f"• {count} {cls}(s)")
    
    return " ".join(summary_parts)
