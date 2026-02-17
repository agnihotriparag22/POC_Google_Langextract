"""Extraction Templates for Different Document Types"""
import langextract as lx
from app.core.schemas import DocumentType, ExtractionTemplate


# Story/Narrative Template
STORY_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract key narrative elements from this story in order of appearance.
    Focus on: characters with their traits, major plot points, themes/morals, and setting details.
    Use exact text for extractions. Provide meaningful attributes for context.""",
    
    examples=[
        lx.data.ExampleData(
            text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="character",
                    extraction_text="ROMEO",
                    attributes={"emotional_state": "wonder", "role": "protagonist"}
                ),
                lx.data.Extraction(
                    extraction_class="plot_point",
                    extraction_text="What light through yonder window breaks?",
                    attributes={"significance": "Romeo sees Juliet"}
                ),
                lx.data.Extraction(
                    extraction_class="theme",
                    extraction_text="Juliet is the sun",
                    attributes={"type": "metaphor", "meaning": "love and admiration"}
                ),
            ]
        )
    ],
    
    extraction_classes=["character", "plot_point", "theme", "setting", "moral"],
    report_sections=["Characters", "Plot Summary", "Themes & Morals", "Setting"]
)


# Meeting Transcript Template
MEETING_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract meeting elements in order of discussion.
    Focus on: speakers with roles, agenda items, action items with owners, decisions made, and key discussion points.
    Use exact text. Include deadlines and responsibilities in attributes.""",
    
    examples=[
        lx.data.ExampleData(
            text="John (PM): We need to finalize the Q4 roadmap by Friday. Sarah, can you prepare the budget analysis?",
            extractions=[
                lx.data.Extraction(
                    extraction_class="speaker",
                    extraction_text="John",
                    attributes={"role": "PM", "title": "Project Manager"}
                ),
                lx.data.Extraction(
                    extraction_class="agenda_item",
                    extraction_text="finalize the Q4 roadmap",
                    attributes={"deadline": "Friday", "priority": "high"}
                ),
                lx.data.Extraction(
                    extraction_class="action_item",
                    extraction_text="prepare the budget analysis",
                    attributes={"owner": "Sarah", "deadline": "implied"}
                ),
            ]
        )
    ],
    
    extraction_classes=["speaker", "agenda_item", "action_item", "decision", "discussion_point"],
    report_sections=["Participants", "Agenda", "Decisions", "Action Items", "Key Discussions"]
)


# Research Paper Template
RESEARCH_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract research paper elements systematically.
    Focus on: authors, research questions, methodology, key findings, conclusions, and important citations.
    Use exact text. Include statistical data and significance in attributes.""",
    
    examples=[
        lx.data.ExampleData(
            text="Dr. Smith et al. investigated the impact of AI on productivity. Results showed a 35% improvement (p<0.05).",
            extractions=[
                lx.data.Extraction(
                    extraction_class="author",
                    extraction_text="Dr. Smith et al.",
                    attributes={"role": "lead researcher"}
                ),
                lx.data.Extraction(
                    extraction_class="research_question",
                    extraction_text="impact of AI on productivity",
                    attributes={"domain": "AI applications"}
                ),
                lx.data.Extraction(
                    extraction_class="finding",
                    extraction_text="35% improvement",
                    attributes={"significance": "p<0.05", "type": "quantitative"}
                ),
            ]
        )
    ],
    
    extraction_classes=["author", "research_question", "methodology", "finding", "conclusion", "citation"],
    report_sections=["Authors", "Research Questions", "Methodology", "Key Findings", "Conclusions"]
)


# Technical Documentation Template
TECHNICAL_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract technical documentation elements.
    Focus on: components/modules, APIs/functions, configuration parameters, dependencies, and usage examples.
    Use exact text. Include technical specifications in attributes.""",
    
    examples=[
        lx.data.ExampleData(
            text="The authenticate() function requires an API key parameter. Returns a JWT token valid for 24 hours.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="function",
                    extraction_text="authenticate()",
                    attributes={"type": "authentication", "return_type": "JWT token"}
                ),
                lx.data.Extraction(
                    extraction_class="parameter",
                    extraction_text="API key parameter",
                    attributes={"required": "true", "type": "string"}
                ),
                lx.data.Extraction(
                    extraction_class="specification",
                    extraction_text="valid for 24 hours",
                    attributes={"component": "JWT token", "duration": "24 hours"}
                ),
            ]
        )
    ],
    
    extraction_classes=["component", "function", "parameter", "dependency", "configuration", "example"],
    report_sections=["Components", "APIs/Functions", "Configuration", "Dependencies", "Usage Examples"]
)


# Legal Document Template
LEGAL_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract legal document elements carefully.
    Focus on: parties involved, key clauses, obligations, dates/deadlines, and important terms.
    Use exact text. Include legal implications in attributes.""",
    
    examples=[
        lx.data.ExampleData(
            text="The Vendor shall deliver the goods by December 31, 2024. Failure to comply results in a 10% penalty.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="The Vendor",
                    attributes={"role": "service provider"}
                ),
                lx.data.Extraction(
                    extraction_class="obligation",
                    extraction_text="deliver the goods",
                    attributes={"deadline": "December 31, 2024", "responsible_party": "Vendor"}
                ),
                lx.data.Extraction(
                    extraction_class="clause",
                    extraction_text="Failure to comply results in a 10% penalty",
                    attributes={"type": "penalty clause", "amount": "10%"}
                ),
            ]
        )
    ],
    
    extraction_classes=["party", "clause", "obligation", "deadline", "term", "penalty"],
    report_sections=["Parties", "Key Clauses", "Obligations", "Important Dates", "Terms & Conditions"]
)


# General Document Template (Fallback)
GENERAL_TEMPLATE = ExtractionTemplate(
    prompt_description="""Extract key information from this document.
    Focus on: main topics, key points, important entities (people, organizations, dates), and significant statements.
    Use exact text. Provide context in attributes.""",
    
    examples=[
        lx.data.ExampleData(
            text="The company announced a merger with TechCorp on March 15th. CEO Jane Doe stated this will increase market share by 20%.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="entity",
                    extraction_text="TechCorp",
                    attributes={"type": "organization", "context": "merger partner"}
                ),
                lx.data.Extraction(
                    extraction_class="key_point",
                    extraction_text="merger with TechCorp",
                    attributes={"date": "March 15th", "significance": "major business event"}
                ),
                lx.data.Extraction(
                    extraction_class="entity",
                    extraction_text="Jane Doe",
                    attributes={"role": "CEO", "type": "person"}
                ),
                lx.data.Extraction(
                    extraction_class="key_point",
                    extraction_text="increase market share by 20%",
                    attributes={"type": "projection", "metric": "market share"}
                ),
            ]
        )
    ],
    
    extraction_classes=["entity", "key_point", "topic", "statement", "date"],
    report_sections=["Key Topics", "Important Entities", "Main Points", "Significant Statements"]
)


# Template registry
TEMPLATES = {
    DocumentType.STORY: STORY_TEMPLATE,
    DocumentType.MEETING: MEETING_TEMPLATE,
    DocumentType.RESEARCH: RESEARCH_TEMPLATE,
    DocumentType.TECHNICAL: TECHNICAL_TEMPLATE,
    DocumentType.LEGAL: LEGAL_TEMPLATE,
    DocumentType.GENERAL: GENERAL_TEMPLATE,
}


def get_template(doc_type: DocumentType) -> ExtractionTemplate:
    """Get extraction template for document type"""
    return TEMPLATES.get(doc_type, GENERAL_TEMPLATE)
