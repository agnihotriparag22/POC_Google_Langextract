"""Pydantic Models and Schemas"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types"""
    STORY = "story"
    MEETING = "meeting"
    RESEARCH = "research"
    TECHNICAL = "technical"
    LEGAL = "legal"
    GENERAL = "general"


class ExtractionItem(BaseModel):
    """Single extraction item"""
    extraction_class: str
    extraction_text: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint"""
    job_id: str
    document_type: DocumentType
    confidence: float
    summary: str
    extraction_count: int
    extractions: List[ExtractionItem]
    pdf_url: str
    jsonl_url: str


class ClassificationResult(BaseModel):
    """Document classification result"""
    document_type: DocumentType
    confidence: float
    reasoning: str


class ExtractionTemplate(BaseModel):
    """Template for document extraction"""
    prompt_description: str
    examples: List[Any]
    extraction_classes: List[str]
    report_sections: List[str]
