"""
NIST Parser for extracting and processing NIST 800-53 controls.
"""
from utils.text_extraction import extract_text_from_pdf, clean_text
import re


def parse_nist_controls(file_path):
    """
    Parse NIST 800-53 controls from a PDF file.
    
    Args:
        file_path (str): Path to the NIST 800-53 PDF file
        
    Returns:
        list: List of control dictionaries
    """
    text = extract_text_from_pdf(file_path)
    text = clean_text(text)
    controls = []
    
    # Regex patterns for control identification
    control_id_pattern = r'((?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|RA|SA|SC|SI)-\d+(?:\(\d+\))?)'
    
    # Find control sections
    control_sections = re.split(r'\n\s*' + control_id_pattern + r'\s+', text)
    
    # Process each control section
    for i in range(1, len(control_sections), 2):
        control_id = control_sections[i]
        control_text = control_sections[i+1] if i+1 < len(control_sections) else ""
        
        # Extract control details
        control_details = extract_control_details(control_id, control_text)
        if control_details:
            controls.append(control_details)
    
    return controls


def extract_control_details(control_id, control_text):
    """
    Extract detailed information about a control.
    
    Args:
        control_id (str): The ID of the control (e.g., 'AC-1')
        control_text (str): The text describing the control
        
    Returns:
        dict: Dictionary containing control details
    """
    # Extract title from the first line
    lines = control_text.strip().split('\n')
    title = lines[0] if lines else ""
    
    # Extract description
    description = '\n'.join(lines[1:10])  # First few lines as description
    
    # Extract related controls if mentioned
    related_controls = []
    related_match = re.search(r'Related controls?:\s*([^\.]+)', control_text)
    if related_match:
        related_text = related_match.group(1)
        related_controls = re.findall(r'((?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|RA|SA|SC|SI)-\d+(?:\(\d+\))?)', related_text)
    
    # Determine family based on control ID prefix
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
    
    family_prefix = control_id.split('-')[0]
    family = family_map.get(family_prefix, 'Unknown')
    
    return {
        "id": control_id,
        "title": title,
        "description": description,
        "source": "NIST 800-53",
        "framework": "FISMA",
        "family": family,
        "related_controls": related_controls,
        "mapped_to": []
    }


def map_controls_to_regulations(controls, regulation_map):
    """
    Map NIST controls to other regulations and standards.
    
    Args:
        controls (list): List of control dictionaries
        regulation_map (dict): Mapping of control IDs to regulations
        
    Returns:
        list: Updated list of controls with mappings
    """
    for control in controls:
        if control["id"] in regulation_map:
            control["mapped_to"] = regulation_map[control["id"]]
    
    return controls