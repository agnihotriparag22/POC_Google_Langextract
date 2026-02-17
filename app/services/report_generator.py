"""PDF Report Generation Service"""
import os
from datetime import datetime
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

from app.core.config import settings
from app.core.schemas import DocumentType, ClassificationResult


def generate_pdf_report(
    extractions: list,
    doc_type: DocumentType,
    job_id: str,
    filename: str,
    classification: ClassificationResult,
    document_text: str = ""
) -> str:
    """
    Generate professional PDF report
    
    Args:
        extractions: List of extraction items
        doc_type: Document type
        job_id: Unique job identifier
        filename: Original filename
        classification: Classification result
        document_text: Sample of document text for context
    
    Returns:
        Path to generated PDF
    """
    
    try:
        # Create job directory
        job_dir = os.path.join(settings.REPORT_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        report_path = os.path.join(job_dir, "report.pdf")
        
        # Create PDF
        doc = SimpleDocTemplate(
            report_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Title
        story.append(Paragraph("Langextract POC - Analysis Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata table
        metadata = [
            ['Document', filename],
            ['Type', doc_type.value.upper()],
            ['Confidence', f"{classification.confidence:.1%}"],
            ['Analyzed', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Job ID', job_id]
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        executive_summary = _generate_executive_summary(extractions, doc_type, classification, document_text)
        
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        for para in executive_summary:
            story.append(Paragraph(para, summary_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Extraction summary
        story.append(Paragraph("Extraction Summary", heading_style))
        
        # Group by extraction class
        grouped = {}
        for e in extractions:
            if e.extraction_class not in grouped:
                grouped[e.extraction_class] = []
            grouped[e.extraction_class].append(e)
        
        summary_data = [['Category', 'Count']]
        for cls, items in grouped.items():
            summary_data.append([cls.replace('_', ' ').title(), str(len(items))])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Key Insights Section
        story.append(Paragraph("Key Insights", heading_style))
        key_insights = _generate_key_insights(grouped, doc_type)
        
        for insight in key_insights:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
            story.append(Spacer(1, 0.08*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed Entities Section
        story.append(Paragraph("Detailed Entities & Findings", heading_style))
        
        # Sort categories by importance
        category_order = _get_category_order(doc_type)
        sorted_categories = sorted(
            grouped.items(),
            key=lambda x: category_order.get(x[0], 999)
        )
        
        for cls, items in sorted_categories:
            # Category header
            cat_style = ParagraphStyle(
                'Category',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#16a085'),
                spaceAfter=10,
                spaceBefore=15
            )
            story.append(Paragraph(cls.replace('_', ' ').title(), cat_style))
            
            # Sort items by mention count (if available)
            sorted_items = sorted(
                items,
                key=lambda x: (x.attributes or {}).get('mention_count', 1),
                reverse=True
            )
            
            # Items
            for item in sorted_items:
                # Extraction text with mention count
                # Safely get attributes (handle None case)
                item_attrs = item.attributes if item.attributes else {}
                mention_count = item_attrs.get('mention_count', 0)
                
                if mention_count > 1:
                    text_display = f"<b>•</b> {item.extraction_text} <i>(mentioned {mention_count} times)</i>"
                else:
                    text_display = f"<b>•</b> {item.extraction_text}"
                
                text_para = Paragraph(text_display, styles['Normal'])
                story.append(text_para)
                
                # Attributes (excluding mention_count as it's already shown)
                if item_attrs:
                    for key, value in item_attrs.items():
                        if key != 'mention_count' and value:
                            # Escape special characters for XML/HTML
                            safe_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            attr_text = f"&nbsp;&nbsp;&nbsp;&nbsp;<i>{key.replace('_', ' ')}:</i> {safe_value}"
                            story.append(Paragraph(attr_text, styles['Normal']))
                
                story.append(Spacer(1, 0.12*inch))
        
        # Build PDF
        doc.build(story)
        
        return report_path
        
    except Exception as e:
        import traceback
        print(f"PDF generation error: {str(e)}")
        print(traceback.format_exc())
        raise Exception(f"Failed to generate PDF report: {str(e)}")


def _generate_executive_summary(extractions: list, doc_type: DocumentType, classification: ClassificationResult, document_text: str) -> list:
    """Generate executive summary paragraphs"""
    paragraphs = []
    
    # Classification summary
    paragraphs.append(
        f"This document has been classified as a <b>{doc_type.value.upper()}</b> "
        f"with {classification.confidence:.0%} confidence. {classification.reasoning}"
    )
    
    # Group extractions
    grouped = defaultdict(list)
    for e in extractions:
        grouped[e.extraction_class].append(e)
    
    # Document-type specific summaries
    if doc_type == DocumentType.STORY:
        char_count = len(grouped.get('character', []))
        theme_count = len(grouped.get('theme', []))
        paragraphs.append(
            f"The narrative features {char_count} main character(s) and explores {theme_count} central theme(s). "
            f"The story presents a compelling narrative with well-defined characters and meaningful themes."
        )
    
    elif doc_type == DocumentType.MEETING:
        speaker_count = len(grouped.get('speaker', []))
        action_count = len(grouped.get('action_item', []))
        decision_count = len(grouped.get('decision', []))
        paragraphs.append(
            f"The meeting involved {speaker_count} participant(s) and resulted in {decision_count} key decision(s) "
            f"with {action_count} action item(s) identified for follow-up."
        )
    
    elif doc_type == DocumentType.RESEARCH:
        finding_count = len(grouped.get('finding', []))
        paragraphs.append(
            f"This research paper presents {finding_count} significant finding(s). "
            f"The study employs rigorous methodology and contributes valuable insights to the field."
        )
    
    elif doc_type == DocumentType.TECHNICAL:
        component_count = len(grouped.get('component', []))
        function_count = len(grouped.get('function', []))
        paragraphs.append(
            f"The technical documentation covers {component_count} component(s) and {function_count} function(s), "
            f"providing comprehensive guidance for implementation and usage."
        )
    
    elif doc_type == DocumentType.LEGAL:
        party_count = len(grouped.get('party', []))
        obligation_count = len(grouped.get('obligation', []))
        paragraphs.append(
            f"This legal document involves {party_count} party/parties with {obligation_count} defined obligation(s). "
            f"The document establishes clear terms and responsibilities for all parties involved."
        )
    
    else:  # GENERAL
        total_entities = len(extractions)
        paragraphs.append(
            f"The document contains {total_entities} key entities and insights. "
            f"Analysis reveals important information across multiple categories."
        )
    
    # Overall summary
    total_extractions = len(extractions)
    unique_classes = len(grouped)
    paragraphs.append(
        f"In total, {total_extractions} unique entities were identified across {unique_classes} categories, "
        f"providing a comprehensive understanding of the document's content and context."
    )
    
    return paragraphs


def _generate_key_insights(grouped: dict, doc_type: DocumentType) -> list:
    """Generate bullet-point key insights"""
    insights = []
    
    for cls, items in grouped.items():
        if not items:
            continue
        
        # Get most mentioned items
        top_items = sorted(
            items,
            key=lambda x: (x.attributes or {}).get('mention_count', 1),
            reverse=True
        )[:3]  # Top 3
        
        if len(items) == 1:
            insights.append(
                f"{cls.replace('_', ' ').title()}: {items[0].extraction_text}"
            )
        elif len(items) <= 3:
            names = [item.extraction_text for item in items]
            insights.append(
                f"{cls.replace('_', ' ').title()}: {', '.join(names)}"
            )
        else:
            names = [item.extraction_text for item in top_items]
            insights.append(
                f"{cls.replace('_', ' ').title()} ({len(items)} total): {', '.join(names)}, and others"
            )
    
    return insights


def _get_category_order(doc_type: DocumentType) -> dict:
    """Define category display order by document type"""
    orders = {
        DocumentType.STORY: {
            'character': 1,
            'plot_point': 2,
            'theme': 3,
            'setting': 4,
            'moral': 5
        },
        DocumentType.MEETING: {
            'speaker': 1,
            'decision': 2,
            'action_item': 3,
            'agenda_item': 4,
            'discussion_point': 5
        },
        DocumentType.RESEARCH: {
            'author': 1,
            'research_question': 2,
            'finding': 3,
            'methodology': 4,
            'conclusion': 5,
            'citation': 6
        },
        DocumentType.TECHNICAL: {
            'component': 1,
            'function': 2,
            'parameter': 3,
            'configuration': 4,
            'dependency': 5,
            'example': 6
        },
        DocumentType.LEGAL: {
            'party': 1,
            'obligation': 2,
            'clause': 3,
            'deadline': 4,
            'term': 5,
            'penalty': 6
        },
        DocumentType.GENERAL: {
            'entity': 1,
            'key_point': 2,
            'topic': 3,
            'statement': 4,
            'date': 5
        }
    }
    
    return orders.get(doc_type, {})
