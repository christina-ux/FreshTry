"""
PDF to JSON converter for regulatory documents.
"""
import fitz  # PyMuPDF
import re
import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for a regulatory document."""
    title: str
    source: str
    version: str = ""
    publication_date: str = ""
    document_id: str = ""
    issuing_organization: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class ControlComponent:
    """Component of a control (e.g., assessment procedure, guidance)."""
    type: str
    content: str
    references: List[str] = field(default_factory=list)


@dataclass
class Control:
    """Regulatory control extracted from a document."""
    id: str
    title: str
    description: str
    family: str = ""
    source: str = ""
    framework: str = ""
    priority: str = ""
    impact: List[str] = field(default_factory=list)
    components: List[ControlComponent] = field(default_factory=list)
    related_controls: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    supplemental_guidance: str = ""


class PDFConverter:
    """Converts regulatory PDFs to structured JSON."""
    
    def __init__(self):
        """Initialize the converter."""
        self.supported_formats = ["NIST", "HIPAA", "ISO27001", "CMMC"]
        self.output_dir = os.path.join(os.getcwd(), "data", "converted")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def detect_format(self, text: str) -> str:
        """
        Detect the regulatory format from text content.
        
        Args:
            text (str): Document text
            
        Returns:
            str: Detected format
        """
        if "NIST Special Publication 800-53" in text:
            return "NIST"
        elif "Health Insurance Portability and Accountability Act" in text or "HIPAA" in text:
            return "HIPAA"
        elif "ISO/IEC 27001" in text:
            return "ISO27001"
        elif "Cybersecurity Maturity Model Certification" in text or "CMMC" in text:
            return "CMMC"
        else:
            return "UNKNOWN"
    
    def extract_metadata(self, text: str, format_type: str) -> DocumentMetadata:
        """
        Extract document metadata.
        
        Args:
            text (str): Document text
            format_type (str): Detected format type
            
        Returns:
            DocumentMetadata: Extracted metadata
        """
        metadata = DocumentMetadata(
            title="",
            source=format_type,
            issuing_organization=""
        )
        
        # Extract title
        if format_type == "NIST":
            title_match = re.search(r'(NIST Special Publication [0-9-]+)[:\r\n]+(.*?)[:\r\n]+', text)
            if title_match:
                metadata.title = title_match.group(2).strip()
                metadata.document_id = title_match.group(1).strip()
                metadata.issuing_organization = "National Institute of Standards and Technology"
            
            # Extract version
            version_match = re.search(r'Revision ([0-9]+)', text)
            if version_match:
                metadata.version = f"Revision {version_match.group(1)}"
                
            # Extract date
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text)
            if date_match:
                metadata.publication_date = date_match.group(0)
        
        elif format_type == "HIPAA":
            metadata.title = "Health Insurance Portability and Accountability Act"
            metadata.issuing_organization = "U.S. Department of Health & Human Services"
        
        return metadata
    
    def convert_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Convert PDF to structured JSON.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict[str, Any]: Structured data
        """
        logger.info(f"Converting PDF: {pdf_path}")
        
        try:
            # Extract text from PDF
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Detect format
            format_type = self.detect_format(text)
            logger.info(f"Detected format: {format_type}")
            
            if format_type == "UNKNOWN":
                logger.warning("Unknown document format. Unable to convert.")
                return {"error": "Unknown document format"}
            
            # Extract metadata
            metadata = self.extract_metadata(text, format_type)
            
            # Extract controls based on format
            controls = []
            if format_type == "NIST":
                controls = self.extract_nist_controls(text)
            elif format_type == "HIPAA":
                controls = self.extract_hipaa_rules(text)
            
            # Create result
            result = {
                "metadata": asdict(metadata),
                "controls": [asdict(control) for control in controls]
            }
            
            # Save to file
            filename = os.path.basename(pdf_path).replace(".pdf", ".json")
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Conversion complete. Output saved to: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error converting PDF: {str(e)}")
            return {"error": str(e)}
    
    def extract_nist_controls(self, text: str) -> List[Control]:
        """
        Extract NIST controls from text.
        
        Args:
            text (str): Document text
            
        Returns:
            List[Control]: Extracted controls
        """
        controls = []
        
        # Regular expressions for NIST control extraction
        control_pattern = re.compile(
            r'((?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|RA|SA|SC|SI)-\d+(?:\(\d+\))?)\s+(.*?)(?=\n\w)'
        )
        
        # Family mapping
        family_map = {
            'AC': 'Access Control',
            'AT': 'Awareness and Training',
            'AU': 'Audit and Accountability',
            'CA': 'Assessment, Authorization, and Monitoring',
            'CM': 'Configuration Management',
            'CP': 'Contingency Planning',
            'IA': 'Identification and Authentication',
            'IR': 'Incident Response',
            'MA': 'Maintenance',
            'MP': 'Media Protection',
            'PE': 'Physical and Environmental Protection',
            'PL': 'Planning',
            'PM': 'Program Management',
            'PS': 'Personnel Security',
            'RA': 'Risk Assessment',
            'SA': 'System and Services Acquisition',
            'SC': 'System and Communications Protection',
            'SI': 'System and Information Integrity'
        }
        
        # Find all controls
        for match in control_pattern.finditer(text):
            control_id = match.group(1)
            title = match.group(2).strip()
            
            # Determine family
            family_prefix = control_id.split('-')[0]
            family = family_map.get(family_prefix, "Unknown")
            
            # Extract description (simplified for this implementation)
            description_start = match.end()
            next_match = control_pattern.search(text, description_start)
            if next_match:
                description_end = next_match.start()
                description = text[description_start:description_end].strip()
            else:
                description = text[description_start:description_start + 1000].strip()
            
            # Create control
            control = Control(
                id=control_id,
                title=title,
                description=description,
                family=family,
                source="NIST 800-53",
                framework="FISMA"
            )
            
            # Extract related controls if mentioned
            related_match = re.search(r'Related controls?:\s*([^\.]+)', description)
            if related_match:
                related_text = related_match.group(1)
                control.related_controls = re.findall(
                    r'((?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|RA|SA|SC|SI)-\d+(?:\(\d+\))?)', 
                    related_text
                )
            
            controls.append(control)
        
        return controls
    
    def extract_hipaa_rules(self, text: str) -> List[Control]:
        """
        Extract HIPAA rules from text.
        
        Args:
            text (str): Document text
            
        Returns:
            List[Control]: Extracted rules as controls
        """
        controls = []
        
        # Regular expression for HIPAA section extraction
        section_pattern = re.compile(r'§\s+(\d+\.\d+(?:\([a-z]\)(?:\(\d+\)(?:\([ivx]+\))?)?)?)\s+([^\n]+)')
        
        # Find all sections
        for match in section_pattern.finditer(text):
            section_id = match.group(1)
            title = match.group(2).strip()
            
            # Extract description
            description_start = match.end()
            next_match = section_pattern.search(text, description_start)
            if next_match:
                description_end = next_match.start()
                description = text[description_start:description_end].strip()
            else:
                description = text[description_start:description_start + 1000].strip()
            
            # Determine family based on section
            family = "Unknown"
            if section_id.startswith('164.3'):
                family = "General Provisions"
            elif section_id.startswith('164.5'):
                family = "Privacy Rule"
            elif section_id.startswith('164.3'):
                family = "Security Rule"
            
            # Create control
            control = Control(
                id=f"HIPAA-{section_id}",
                title=title,
                description=description,
                family=family,
                source="HIPAA",
                framework="HIPAA"
            )
            
            controls.append(control)
        
        return controls
    
    def batch_convert(self, directory: str) -> List[Dict[str, Any]]:
        """
        Batch convert all PDFs in a directory.
        
        Args:
            directory (str): Directory containing PDFs
            
        Returns:
            List[Dict[str, Any]]: Conversion results
        """
        results = []
        
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return results
        
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory, filename)
                result = self.convert_pdf(file_path)
                results.append({
                    "file": filename,
                    "result": result
                })
        
        return results