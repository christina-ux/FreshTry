"""
Tests for the NIST parser module.
"""
import unittest
import os
import json
from pathlib import Path
from ingest.nist_parser import parse_nist_controls, extract_control_details


class TestNistParser(unittest.TestCase):
    """Test cases for NIST parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data directory if it doesn't exist
        self.test_data_dir = Path("tests/test_data")
        self.test_data_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a simple mock NIST control text
        self.mock_control_id = "AC-1"
        self.mock_control_text = """Access Control Policy and Procedures
The organization:
a. Develops, documents, and disseminates to [Assignment: organization-defined personnel or roles]:
    1. An access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    2. Procedures to facilitate the implementation of the access control policy and associated access controls; and
b. Reviews and updates the current:
    1. Access control policy [Assignment: organization-defined frequency]; and
    2. Access control procedures [Assignment: organization-defined frequency].

Related controls: PM-9, PS-8, SI-12."""
    
    def test_extract_control_details(self):
        """Test extracting details from a control."""
        control = extract_control_details(self.mock_control_id, self.mock_control_text)
        
        # Check that control has expected fields
        self.assertEqual(control["id"], "AC-1")
        self.assertEqual(control["title"], "Access Control Policy and Procedures")
        self.assertEqual(control["source"], "NIST 800-53")
        self.assertEqual(control["framework"], "FISMA")
        self.assertEqual(control["family"], "Access Control")
        
        # Check that related controls are extracted
        self.assertIn("PM-9", control["related_controls"])
        self.assertIn("PS-8", control["related_controls"])
        self.assertIn("SI-12", control["related_controls"])
    
    def test_parse_nist_controls_with_fake_data(self):
        """Test parsing NIST controls with fake data."""
        # Create a simple mock NIST document
        mock_nist_content = f"""
        AC-1 Access Control Policy and Procedures
        The organization:
        a. Develops, documents, and disseminates to [Assignment: organization-defined personnel or roles]:
            1. An access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
            2. Procedures to facilitate the implementation of the access control policy and associated access controls; and
        b. Reviews and updates the current:
            1. Access control policy [Assignment: organization-defined frequency]; and
            2. Access control procedures [Assignment: organization-defined frequency].
        
        Related controls: PM-9, PS-8, SI-12.
        
        AC-2 Account Management
        The organization:
        a. Identifies and selects the following types of information system accounts to support organizational missions/business functions: [Assignment: organization-defined information system account types];
        b. Assigns account managers for information system accounts;
        c. Establishes conditions for group and role membership;
        d. Specifies authorized users of the information system, group and role membership, and access authorizations (i.e., privileges) and other attributes (as required) for each account;
        
        Related controls: AC-3, AC-4, AC-5, AC-6, AC-10, AC-17, AC-19, AC-20, AU-9, IA-2, IA-4, IA-5, IA-8, CM-5, CM-6, CM-11, MA-3, MA-4, MA-5, PL-4, SC-13.
        """
        
        # Write mock data to a temporary file
        mock_file_path = self.test_data_dir / "mock_nist.txt"
        with open(mock_file_path, "w") as f:
            f.write(mock_nist_content)
        
        # Mock the extract_text_from_pdf function
        def mock_extract_text(*args, **kwargs):
            with open(mock_file_path, "r") as f:
                return f.read()
        
        # Monkeypatch the extract_text_from_pdf function
        import ingest.nist_parser
        original_extract = ingest.nist_parser.extract_text_from_pdf
        ingest.nist_parser.extract_text_from_pdf = mock_extract
        
        try:
            # Test the parser
            controls = parse_nist_controls(str(mock_file_path))
            
            # Basic validation
            self.assertTrue(len(controls) > 0)
            self.assertEqual(controls[0]["id"], "AC-1")
            self.assertEqual(controls[0]["family"], "Access Control")
            
            # Check for related controls
            self.assertIn("PM-9", controls[0]["related_controls"])
            
            # Check second control
            if len(controls) > 1:
                self.assertEqual(controls[1]["id"], "AC-2")
                self.assertEqual(controls[1]["title"], "Account Management")
        finally:
            # Restore the original function
            ingest.nist_parser.extract_text_from_pdf = original_extract
            
            # Clean up
            if mock_file_path.exists():
                mock_file_path.unlink()


if __name__ == "__main__":
    unittest.main()