"""Document Classification Service"""
import os
import google.generativeai as genai
from app.core.config import settings
from app.core.schemas import DocumentType, ClassificationResult
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def classify_document(text: str) -> ClassificationResult:
    """
    Classify document type using Gemini
    
    Args:
        text: Document text content
    
    Returns:
        ClassificationResult with document type and confidence
    """
    
    # Use first 2000 characters for classification
    sample_text = text[:2000]
    
    prompt = f"""Analyze the following document excerpt and classify it into ONE of these categories:

1. STORY - Narrative fiction, novels, short stories, creative writing
2. MEETING - Meeting transcripts, minutes, discussion notes
3. RESEARCH - Research papers, academic articles, scientific studies
4. TECHNICAL - Technical documentation, API docs, user manuals, how-to guides
5. LEGAL - Legal documents, contracts, agreements, terms of service
6. GENERAL - Any other type of document

Document excerpt:
---
{sample_text}
---

Respond in this exact format:
CATEGORY: [one of: STORY, MEETING, RESEARCH, TECHNICAL, LEGAL, GENERAL]
CONFIDENCE: [0.0 to 1.0]
REASONING: [brief explanation]
"""
    
    try:
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
        response = model.generate_content(prompt)
        
        # Parse response
        lines = response.text.strip().split('\n')
        category = None
        confidence = 0.7
        reasoning = ""
        
        for line in lines:
            if line.startswith("CATEGORY:"):
                category_str = line.split(":", 1)[1].strip().upper()
                category = _map_category(category_str)
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    confidence = 0.7
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
        
        if not category:
            category = DocumentType.GENERAL
            reasoning = "Unable to determine specific category"
        
        return ClassificationResult(
            document_type=category,
            confidence=confidence,
            reasoning=reasoning
        )
        
    except Exception as e:
        print(f"Classification error: {e}")
        return ClassificationResult(
            document_type=DocumentType.GENERAL,
            confidence=0.5,
            reasoning=f"Classification failed, using fallback: {str(e)}"
        )


def _map_category(category_str: str) -> DocumentType:
    """Map string category to DocumentType enum"""
    mapping = {
        "STORY": DocumentType.STORY,
        "MEETING": DocumentType.MEETING,
        "RESEARCH": DocumentType.RESEARCH,
        "TECHNICAL": DocumentType.TECHNICAL,
        "LEGAL": DocumentType.LEGAL,
        "GENERAL": DocumentType.GENERAL
    }
    return mapping.get(category_str, DocumentType.GENERAL)
