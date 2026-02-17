"""Insight Extraction Service using langextract"""
import os
import langextract as lx
from collections import defaultdict
from app.core.config import settings
from app.core.schemas import DocumentType
from app.templates.extraction_templates import get_template

from dotenv import load_dotenv

load_dotenv()

# Configure Gemini for langextract
os.environ['GEMINI_API_KEY'] = settings.GEMINI_API_KEY


def extract_insights(text: str, doc_type: DocumentType):
    """
    Extract insights from document using langextract
    
    Args:
        text: Document text content
        doc_type: Classified document type
    
    Returns:
        langextract ExtractionResult with deduplicated extractions
    """
    
    # Get extraction template for document type
    template = get_template(doc_type)
    
    # Handle long documents by chunking
    if len(text) > 8000:
        text = _chunk_and_extract(text, template)
    
    # Run extraction
    result = lx.extract(
        text_or_documents=text,
        prompt_description=template.prompt_description,
        examples=template.examples,
        model_id=os.getenv("GEMINI_MODEL"),
    )
    
    # Deduplicate extractions
    result.extractions = _deduplicate_extractions(result.extractions)
    
    return result


def _deduplicate_extractions(extractions: list) -> list:
    """
    Deduplicate extractions by merging similar entities
    
    Groups by extraction_class and extraction_text (case-insensitive),
    merges attributes, and adds mention count
    """
    # Group by class and normalized text
    grouped = defaultdict(lambda: {
        'extraction': None,
        'count': 0,
        'all_attributes': []
    })
    
    for extraction in extractions:
        # Create key: class + normalized text
        key = (
            extraction.extraction_class,
            extraction.extraction_text.strip().lower()
        )
        
        if grouped[key]['extraction'] is None:
            grouped[key]['extraction'] = extraction
        
        grouped[key]['count'] += 1
        
        # Collect all attributes (ensure it's a dict)
        if extraction.attributes and isinstance(extraction.attributes, dict):
            grouped[key]['all_attributes'].append(extraction.attributes)
    
    # Build deduplicated list
    deduplicated = []
    
    for (cls, text), data in grouped.items():
        extraction = data['extraction']
        count = data['count']
        
        # Merge attributes
        merged_attrs = _merge_attributes(data['all_attributes'])
        
        # Add mention count if more than 1
        if count > 1:
            merged_attrs['mention_count'] = count
        
        # Update extraction - ensure attributes is always a dict
        extraction.attributes = merged_attrs if merged_attrs else {}
        deduplicated.append(extraction)
    
    return deduplicated


def _merge_attributes(all_attributes: list) -> dict:
    """
    Merge multiple attribute dictionaries intelligently
    
    - For duplicate keys, keep first non-empty value
    - Collect unique values for repeated keys
    """
    if not all_attributes:
        return {}
    
    merged = {}
    value_sets = defaultdict(set)
    
    for attrs in all_attributes:
        for key, value in attrs.items():
            if key not in merged:
                merged[key] = value
            
            # Track all unique values
            if value:
                value_sets[key].add(str(value))
    
    # If a key has multiple unique values, create a summary
    for key, values in value_sets.items():
        if len(values) > 1:
            merged[f"{key}_variations"] = ", ".join(sorted(values))
    
    return merged


def _chunk_and_extract(text: str, template):
    """
    Chunk long documents and extract from first significant chunk
    
    For 5-10 page documents, we focus on the first ~4000 chars
    which typically contains the most important information
    """
    # Take first 4000 characters with word boundary
    chunk_size = 4000
    if len(text) > chunk_size:
        # Find last space to avoid cutting words
        last_space = text[:chunk_size].rfind(' ')
        if last_space > chunk_size - 200:
            text = text[:last_space]
        else:
            text = text[:chunk_size]
    
    return text
