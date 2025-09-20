"""
Compliance model module for analyzing and processing compliance requirements.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import os
from openai import OpenAI


@dataclass
class ComplianceControl:
    """Represents a compliance control from any framework."""
    id: str
    title: str
    description: str
    source: str
    framework: str
    family: Optional[str] = None
    related_controls: List[str] = field(default_factory=list)
    mapped_to: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "framework": self.framework,
            "family": self.family,
            "related_controls": self.related_controls,
            "mapped_to": self.mapped_to
        }

    @classmethod
    def from_dict(cls, data):
        """Create a ComplianceControl from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            source=data["source"],
            framework=data["framework"],
            family=data.get("family"),
            related_controls=data.get("related_controls", []),
            mapped_to=data.get("mapped_to", [])
        )


class ComplianceModel:
    """Model for compliance analysis and processing."""
    
    def __init__(self, api_key=None):
        """
        Initialize the compliance model.
        
        Args:
            api_key (str, optional): OpenAI API key for AI-powered compliance analysis
        """
        self.controls = []
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None
        
    def add_controls(self, controls_data):
        """
        Add controls to the model.
        
        Args:
            controls_data (list): List of control dictionaries
        """
        for control_data in controls_data:
            control = ComplianceControl.from_dict(control_data)
            self.controls.append(control)
    
    def get_control_by_id(self, control_id):
        """
        Get a control by its ID.
        
        Args:
            control_id (str): Control ID to find
            
        Returns:
            ComplianceControl or None: The found control or None
        """
        for control in self.controls:
            if control.id == control_id:
                return control
        return None
    
    def filter_controls(self, framework=None, family=None, keyword=None):
        """
        Filter controls by various criteria.
        
        Args:
            framework (str, optional): Framework to filter by
            family (str, optional): Control family to filter by
            keyword (str, optional): Keyword to search in title or description
            
        Returns:
            list: Filtered controls
        """
        filtered = self.controls
        
        if framework:
            filtered = [c for c in filtered if c.framework == framework]
            
        if family:
            filtered = [c for c in filtered if c.family == family]
            
        if keyword:
            keyword = keyword.lower()
            filtered = [c for c in filtered if (
                keyword in c.title.lower() or 
                keyword in c.description.lower()
            )]
            
        return filtered
    
    def save_to_file(self, file_path):
        """
        Save controls to a JSON file.
        
        Args:
            file_path (str): Path to save the JSON file
        """
        data = [control.to_dict() for control in self.controls]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, file_path):
        """
        Load controls from a JSON file.
        
        Args:
            file_path (str): Path to the JSON file
        """
        if not os.path.exists(file_path):
            return
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        self.controls = [ComplianceControl.from_dict(item) for item in data]
    
    def analyze_compliance_gap(self, framework1, framework2):
        """
        Analyze compliance gaps between two frameworks.
        
        Args:
            framework1 (str): First framework
            framework2 (str): Second framework
            
        Returns:
            dict: Gap analysis results
        """
        framework1_controls = [c for c in self.controls if c.framework == framework1]
        framework2_controls = [c for c in self.controls if c.framework == framework2]
        
        # Find controls in framework1 that don't map to framework2
        gaps = []
        for control in framework1_controls:
            maps_to_framework2 = False
            for mapping in control.mapped_to:
                if mapping.get("framework") == framework2:
                    maps_to_framework2 = True
                    break
            
            if not maps_to_framework2:
                gaps.append(control)
        
        return {
            "framework1": framework1,
            "framework2": framework2,
            "total_controls_framework1": len(framework1_controls),
            "total_controls_framework2": len(framework2_controls),
            "unmapped_controls": [c.to_dict() for c in gaps],
            "gap_percentage": len(gaps) / len(framework1_controls) * 100 if framework1_controls else 0
        }
    
    def generate_compliance_summary(self, controls=None):
        """
        Generate a natural language summary of compliance requirements.
        
        Args:
            controls (list, optional): List of controls to summarize
            
        Returns:
            str: Summary text
        """
        if self.client is None:
            return "API key not provided. Cannot generate summary."
            
        controls_to_summarize = controls or self.controls
        if not controls_to_summarize:
            return "No controls to summarize."
            
        # Prepare data for the API
        control_texts = []
        for control in controls_to_summarize[:20]:  # Limit to 20 controls to avoid token limits
            control_texts.append(f"{control.id} ({control.title}): {control.description[:200]}...")
            
        prompt = "Please provide a concise summary of the following compliance controls:\n\n"
        prompt += "\n\n".join(control_texts)
        prompt += "\n\nSummary should include:\n"
        prompt += "1. Main themes and requirements\n"
        prompt += "2. High-level objectives\n"
        prompt += "3. Key security or privacy principles addressed"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a compliance expert tasked with summarizing regulatory requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"