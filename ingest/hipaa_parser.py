"""
HIPAA Parser for extracting and processing HIPAA regulations.
"""
from utils.text_extraction import extract_text_from_pdf, clean_text
import re


def parse_hipaa_regulations(file_path):
    """
    Parse HIPAA regulations from a PDF file.
    
    Args:
        file_path (str): Path to the HIPAA regulations PDF file
        
    Returns:
        list: List of regulation dictionaries
    """
    text = extract_text_from_pdf(file_path)
    text = clean_text(text)
    regulations = []
    
    # Regex patterns for HIPAA section identification
    # HIPAA typically uses format like § 164.308(a)(1)(i)
    section_pattern = r'§\s+(\d+\.\d+(?:\([a-z]\)(?:\(\d+\)(?:\([ivx]+\))?)?)?)'
    
    # Find regulation sections
    section_matches = re.finditer(section_pattern + r'\s+([^\n]+)', text)
    
    for match in section_matches:
        section_id = match.group(1)
        title = match.group(2)
        
        # Find the content (everything until the next section)
        start_pos = match.end()
        next_match = re.search(section_pattern, text[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
            content = text[start_pos:end_pos]
        else:
            content = text[start_pos:]
        
        regulation = {
            "id": f"HIPAA-{section_id}",
            "title": title,
            "description": content.strip(),
            "source": "HIPAA",
            "citation": f"45 CFR § {section_id}",
            "category": categorize_hipaa_section(section_id),
            "mapped_to": []
        }
        
        regulations.append(regulation)
    
    return regulations


def categorize_hipaa_section(section_id):
    """
    Categorize HIPAA section based on its ID.
    
    Args:
        section_id (str): Section ID (e.g., '164.308')
        
    Returns:
        str: Category name
    """
    if section_id.startswith('164.302') or section_id.startswith('164.304'):
        return "General Rules"
    elif section_id.startswith('164.306') or section_id.startswith('164.308'):
        return "Administrative Safeguards"
    elif section_id.startswith('164.310'):
        return "Physical Safeguards"
    elif section_id.startswith('164.312'):
        return "Technical Safeguards"
    elif section_id.startswith('164.314'):
        return "Organizational Requirements"
    elif section_id.startswith('164.316'):
        return "Policies and Procedures and Documentation"
    elif section_id.startswith('164.5'):
        return "Privacy Rule"
    else:
        return "Other"


def map_hipaa_to_nist(hipaa_regulations, nist_controls):
    """
    Map HIPAA regulations to NIST controls.
    
    Args:
        hipaa_regulations (list): List of HIPAA regulation dictionaries
        nist_controls (list): List of NIST control dictionaries
        
    Returns:
        list: Updated list of HIPAA regulations with mappings to NIST controls
    """
    # Mapping based on common security patterns
    # This is a simplified example and would need to be expanded with proper mappings
    mapping = {
        # Administrative Safeguards
        "HIPAA-164.308(a)(1)(i)": ["RA-1", "PM-9"],  # Risk Analysis
        "HIPAA-164.308(a)(1)(ii)(B)": ["CA-5"],  # Risk Management
        "HIPAA-164.308(a)(2)": ["PL-1"],  # Assigned Security Responsibility
        "HIPAA-164.308(a)(3)(i)": ["AC-1", "PS-1"],  # Workforce Security
        "HIPAA-164.308(a)(4)": ["AC-3", "AC-6"],  # Information Access Management
        "HIPAA-164.308(a)(5)": ["AT-1", "AT-2"],  # Security Awareness and Training
        
        # Physical Safeguards
        "HIPAA-164.310(a)(1)": ["PE-1", "PE-2", "PE-3"],  # Facility Access Controls
        "HIPAA-164.310(b)": ["PE-16"],  # Workstation Use
        "HIPAA-164.310(d)(1)": ["MP-1", "MP-4", "MP-5"],  # Device and Media Controls
        
        # Technical Safeguards
        "HIPAA-164.312(a)(1)": ["AC-2", "IA-2", "IA-4"],  # Access Control
        "HIPAA-164.312(b)": ["AU-1", "AU-2", "AU-3"],  # Audit Controls
        "HIPAA-164.312(c)(1)": ["SI-7"],  # Integrity
        "HIPAA-164.312(d)": ["IA-1", "IA-4", "IA-5"],  # Person or Entity Authentication
        "HIPAA-164.312(e)(1)": ["SC-8", "SC-9"]  # Transmission Security
    }
    
    # Apply mappings
    for reg in hipaa_regulations:
        if reg["id"] in mapping:
            nist_ids = mapping[reg["id"]]
            reg["mapped_to"] = [{"framework": "NIST 800-53", "control_ids": nist_ids}]
            
            # Also update the corresponding NIST controls
            for control in nist_controls:
                if control["id"] in nist_ids:
                    if not any(m["framework"] == "HIPAA" for m in control["mapped_to"]):
                        control["mapped_to"].append({
                            "framework": "HIPAA",
                            "regulation_ids": [reg["id"]]
                        })
    
    return hipaa_regulations