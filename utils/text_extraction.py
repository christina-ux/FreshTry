"""
Utility functions for extracting text from various document formats.
"""
import PyPDF2
import re
import os


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
        
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return text


def clean_text(text):
    """
    Clean extracted text by removing extra whitespace and normalizing line breaks.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def extract_sections(text, section_pattern=r'^([A-Z][A-Z\s-]+):\s*$'):
    """
    Extract sections from text based on a section header pattern.
    
    Args:
        text (str): Text to parse
        section_pattern (str): Regex pattern for section headers
        
    Returns:
        dict: Dictionary mapping section headers to their content
    """
    sections = {}
    current_section = None
    section_content = []
    
    for line in text.split('\n'):
        section_match = re.match(section_pattern, line.strip())
        if section_match:
            if current_section:
                sections[current_section] = '\n'.join(section_content)
            current_section = section_match.group(1)
            section_content = []
        elif current_section:
            section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content)
    
    return sections