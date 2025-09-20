"""
Zero Trust Architecture (ZTA) Mapping Module.

Maps controls from different frameworks to ZTA principles and components
based on NIST SP 800-207 Zero Trust Architecture.
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any, Set
import csv
from dataclasses import dataclass, field, asdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    title: str
    framework: str
    organization: str = "Your Organization"
    include_executive_summary: bool = True
    include_gap_analysis: bool = True
    include_implementation_status: bool = True
    include_zta_mapping: bool = False
    output_format: str = "pdf"  # "pdf" or "html"


@dataclass
class ZTAComponent:
    """Represents a component of Zero Trust Architecture."""
    id: str
    name: str
    description: str
    category: str
    nist_references: List[str] = field(default_factory=list)
    principles: List[str] = field(default_factory=list)


@dataclass
class ZTAMapping:
    """Mapping between a control and ZTA components."""
    control_id: str
    control_framework: str
    zta_component_id: str
    relevance_score: float  # 0.0 to 1.0
    implementation_notes: str = ""


class ZTAMapper:
    """Maps regulatory controls to Zero Trust Architecture components."""
    
    def __init__(self):
        """Initialize ZTA mapper with core ZTA components based on NIST SP 800-207."""
        self.components: Dict[str, ZTAComponent] = {}
        self.mappings: List[ZTAMapping] = []
        self.data_dir = os.path.join(os.getcwd(), "data", "zta")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize ZTA components
        self._initialize_components()
        
        # Load any existing mappings
        self._load_mappings()
    
    def _initialize_components(self):
        """Initialize ZTA components based on NIST SP 800-207."""
        # Core ZTA components
        components = [
            ZTAComponent(
                id="PE",
                name="Policy Engine",
                description="The policy engine is responsible for the ultimate decision to grant access to a resource.",
                category="Control Plane",
                principles=["Zero trust policy enforcement", "Continuous evaluation"]
            ),
            ZTAComponent(
                id="PA",
                name="Policy Administrator",
                description="The policy administrator is responsible for establishing and/or shutting down the communication path between a subject and a resource.",
                category="Control Plane", 
                principles=["Session management", "Resource access enforcement"]
            ),
            ZTAComponent(
                id="PEP",
                name="Policy Enforcement Point",
                description="A system element that enforces policy decisions made by the policy engine.",
                category="Data Plane",
                principles=["Security boundary enforcement", "Network segmentation"]
            ),
            ZTAComponent(
                id="CD",
                name="Continuous Diagnostics and Monitoring",
                description="System that collects, processes, and analyzes data about assets and network traffic.",
                category="Supporting Infrastructure",
                principles=["Continuous monitoring", "Threat intelligence"]
            ),
            ZTAComponent(
                id="IdM",
                name="Identity Management",
                description="Systems and processes used to create and manage user accounts and identity records.",
                category="Supporting Infrastructure",
                principles=["Identity verification", "Authentication"]
            ),
            ZTAComponent(
                id="IA",
                name="Industry Compliance Assessment",
                description="Evaluates enterprise compliance with regulatory frameworks.",
                category="Supporting Infrastructure",
                principles=["Compliance validation", "Audit"]
            ),
            ZTAComponent(
                id="DS",
                name="Data Security",
                description="Provides data protection, encryption, and access controls.",
                category="Supporting Infrastructure",
                principles=["Data protection", "Encryption"]
            ),
            ZTAComponent(
                id="TA",
                name="Threat Intelligence",
                description="Provides information about active threats against assets.",
                category="Supporting Infrastructure",
                principles=["Threat awareness", "Risk-based decisions"]
            ),
            ZTAComponent(
                id="NR",
                name="Network Requirements",
                description="Network architecture and infrastructure needed to support ZTA.",
                category="Network Infrastructure", 
                principles=["Network security", "Software-defined perimeter"]
            ),
            ZTAComponent(
                id="DP",
                name="Device and Asset Management",
                description="Systems that track enterprise assets and their security posture.",
                category="Supporting Infrastructure",
                principles=["Asset inventory", "Posture assessment"]
            ),
        ]
        
        # Add to components dictionary
        for component in components:
            self.components[component.id] = component
    
    def _load_mappings(self):
        """Load existing mappings from file if available."""
        mapping_file = os.path.join(self.data_dir, "zta_mappings.json")
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r') as f:
                    mappings_data = json.load(f)
                    
                self.mappings = []
                for mapping_item in mappings_data:
                    self.mappings.append(ZTAMapping(
                        control_id=mapping_item["control_id"],
                        control_framework=mapping_item["control_framework"],
                        zta_component_id=mapping_item["zta_component_id"],
                        relevance_score=mapping_item["relevance_score"],
                        implementation_notes=mapping_item.get("implementation_notes", "")
                    ))
                    
                logger.info(f"Loaded {len(self.mappings)} ZTA mappings")
                
            except Exception as e:
                logger.error(f"Error loading ZTA mappings: {str(e)}")
    
    def _save_mappings(self):
        """Save mappings to file."""
        mapping_file = os.path.join(self.data_dir, "zta_mappings.json")
        try:
            mappings_data = [asdict(mapping) for mapping in self.mappings]
            with open(mapping_file, 'w') as f:
                json.dump(mappings_data, f, indent=2)
                
            logger.info(f"Saved {len(self.mappings)} ZTA mappings")
            
        except Exception as e:
            logger.error(f"Error saving ZTA mappings: {str(e)}")
    
    def get_components(self) -> List[Dict[str, Any]]:
        """Get all ZTA components."""
        return [asdict(component) for component in self.components.values()]
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific ZTA component by ID."""
        component = self.components.get(component_id)
        if component:
            return asdict(component)
        return None
    
    def add_mapping(self, control_id: str, control_framework: str, 
                    zta_component_id: str, relevance_score: float,
                    implementation_notes: str = "") -> Dict[str, Any]:
        """
        Add a new mapping between a control and ZTA component.
        
        Args:
            control_id (str): ID of the control
            control_framework (str): Framework the control belongs to
            zta_component_id (str): ID of the ZTA component
            relevance_score (float): Relevance score (0.0 to 1.0)
            implementation_notes (str, optional): Notes about implementation
            
        Returns:
            Dict[str, Any]: Created mapping
        """
        # Validate component exists
        if zta_component_id not in self.components:
            raise ValueError(f"ZTA component with ID {zta_component_id} not found")
        
        # Validate score range
        if relevance_score < 0.0 or relevance_score > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        
        # Create mapping
        mapping = ZTAMapping(
            control_id=control_id,
            control_framework=control_framework,
            zta_component_id=zta_component_id,
            relevance_score=relevance_score,
            implementation_notes=implementation_notes
        )
        
        # Add to mappings
        self.mappings.append(mapping)
        
        # Save mappings
        self._save_mappings()
        
        return asdict(mapping)
    
    def get_mappings_for_control(self, control_id: str, framework: str) -> List[Dict[str, Any]]:
        """
        Get ZTA mappings for a specific control.
        
        Args:
            control_id (str): ID of the control
            framework (str): Framework the control belongs to
            
        Returns:
            List[Dict[str, Any]]: Mappings for the control
        """
        result = []
        for mapping in self.mappings:
            if mapping.control_id == control_id and mapping.control_framework == framework:
                component = self.components.get(mapping.zta_component_id)
                if component:
                    result.append({
                        "mapping": asdict(mapping),
                        "component": asdict(component)
                    })
        
        return result
    
    def get_controls_for_component(self, component_id: str) -> List[Dict[str, Any]]:
        """
        Get controls mapped to a specific ZTA component.
        
        Args:
            component_id (str): ID of the ZTA component
            
        Returns:
            List[Dict[str, Any]]: Mappings for the component
        """
        result = []
        for mapping in self.mappings:
            if mapping.zta_component_id == component_id:
                result.append(asdict(mapping))
        
        return result
    
    def generate_zta_coverage_report(self, controls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a report on ZTA coverage for a set of controls.
        
        Args:
            controls (List[Dict[str, Any]]): List of controls to analyze
            
        Returns:
            Dict[str, Any]: ZTA coverage report
        """
        # Initialize coverage data
        coverage = {
            "total_controls": len(controls),
            "mapped_controls": 0,
            "component_coverage": {},
            "mapped_control_ids": [],
            "unmapped_control_ids": [],
            "components": {}
        }
        
        # Initialize component coverage
        for component_id, component in self.components.items():
            coverage["component_coverage"][component_id] = {
                "name": component.name,
                "category": component.category,
                "control_count": 0,
                "average_relevance": 0.0,
                "controls": []
            }
            coverage["components"][component_id] = asdict(component)
        
        # Track mapped control IDs and sum relevance scores
        mapped_control_ids = set()
        component_relevance_sums = {comp_id: 0.0 for comp_id in self.components}
        
        # Analyze each control
        for control in controls:
            control_id = control["id"]
            framework = control.get("framework", "")
            
            # Find mappings for this control
            mappings = [m for m in self.mappings if m.control_id == control_id and m.control_framework == framework]
            
            if mappings:
                mapped_control_ids.add(control_id)
                coverage["mapped_control_ids"].append(control_id)
                
                # Update component coverage
                for mapping in mappings:
                    component_id = mapping.zta_component_id
                    if component_id in coverage["component_coverage"]:
                        coverage["component_coverage"][component_id]["control_count"] += 1
                        coverage["component_coverage"][component_id]["controls"].append({
                            "id": control_id,
                            "relevance": mapping.relevance_score
                        })
                        component_relevance_sums[component_id] += mapping.relevance_score
            else:
                coverage["unmapped_control_ids"].append(control_id)
        
        # Update mapped controls count
        coverage["mapped_controls"] = len(mapped_control_ids)
        
        # Calculate average relevance for each component
        for component_id, component_data in coverage["component_coverage"].items():
            if component_data["control_count"] > 0:
                component_data["average_relevance"] = component_relevance_sums[component_id] / component_data["control_count"]
        
        # Calculate overall metrics
        coverage["overall_coverage_percentage"] = (coverage["mapped_controls"] / coverage["total_controls"]) * 100 if coverage["total_controls"] > 0 else 0
        
        # Category coverage
        categories = set(component.category for component in self.components.values())
        coverage["category_coverage"] = {}
        
        for category in categories:
            category_components = [c.id for c in self.components.values() if c.category == category]
            total_controls_in_category = sum(coverage["component_coverage"][c]["control_count"] for c in category_components)
            
            coverage["category_coverage"][category] = {
                "components": category_components,
                "control_count": total_controls_in_category
            }
        
        return coverage
    
    def export_mappings_to_csv(self, filepath: str) -> bool:
        """
        Export mappings to CSV file.
        
        Args:
            filepath (str): Path to export CSV to
            
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['control_id', 'control_framework', 'zta_component_id', 
                             'component_name', 'relevance_score', 'implementation_notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for mapping in self.mappings:
                    component = self.components.get(mapping.zta_component_id)
                    writer.writerow({
                        'control_id': mapping.control_id,
                        'control_framework': mapping.control_framework,
                        'zta_component_id': mapping.zta_component_id,
                        'component_name': component.name if component else "Unknown",
                        'relevance_score': mapping.relevance_score,
                        'implementation_notes': mapping.implementation_notes
                    })
                    
            logger.info(f"Exported {len(self.mappings)} mappings to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting mappings to CSV: {str(e)}")
            return False
    
    def import_mappings_from_csv(self, filepath: str) -> int:
        """
        Import mappings from CSV file.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            int: Number of mappings imported
        """
        imported_count = 0
        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        control_id = row.get('control_id', '')
                        control_framework = row.get('control_framework', '')
                        zta_component_id = row.get('zta_component_id', '')
                        relevance_score = float(row.get('relevance_score', 0.0))
                        implementation_notes = row.get('implementation_notes', '')
                        
                        # Validate component exists
                        if zta_component_id not in self.components:
                            logger.warning(f"Skipping row - component {zta_component_id} not found")
                            continue
                        
                        # Add mapping
                        self.add_mapping(
                            control_id=control_id,
                            control_framework=control_framework,
                            zta_component_id=zta_component_id,
                            relevance_score=relevance_score,
                            implementation_notes=implementation_notes
                        )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Error processing row: {str(e)}")
                        continue
                
            logger.info(f"Imported {imported_count} mappings from {filepath}")
            return imported_count
            
        except Exception as e:
            logger.error(f"Error importing mappings from CSV: {str(e)}")
            return 0
    
    # Pre-defined mappings for common frameworks
    def generate_default_nist_mappings(self) -> int:
        """
        Generate default mappings for NIST 800-53 controls to ZTA components.
        
        Returns:
            int: Number of mappings created
        """
        # Common mappings based on NIST 800-207 and 800-53
        default_mappings = [
            # Access Control
            {"control_id": "AC-1", "framework": "NIST 800-53", "component": "PE", "score": 0.8},
            {"control_id": "AC-2", "framework": "NIST 800-53", "component": "IdM", "score": 0.9},
            {"control_id": "AC-3", "framework": "NIST 800-53", "component": "PE", "score": 0.9},
            {"control_id": "AC-4", "framework": "NIST 800-53", "component": "PEP", "score": 0.8},
            {"control_id": "AC-17", "framework": "NIST 800-53", "component": "PEP", "score": 0.7},
            
            # Audit and Accountability
            {"control_id": "AU-2", "framework": "NIST 800-53", "component": "CD", "score": 0.8},
            {"control_id": "AU-3", "framework": "NIST 800-53", "component": "CD", "score": 0.7},
            {"control_id": "AU-6", "framework": "NIST 800-53", "component": "CD", "score": 0.8},
            
            # Identity and Authentication
            {"control_id": "IA-2", "framework": "NIST 800-53", "component": "IdM", "score": 0.9},
            {"control_id": "IA-3", "framework": "NIST 800-53", "component": "IdM", "score": 0.7},
            {"control_id": "IA-5", "framework": "NIST 800-53", "component": "IdM", "score": 0.8},
            
            # System and Communications Protection
            {"control_id": "SC-7", "framework": "NIST 800-53", "component": "PEP", "score": 0.9},
            {"control_id": "SC-8", "framework": "NIST 800-53", "component": "DS", "score": 0.8},
            {"control_id": "SC-13", "framework": "NIST 800-53", "component": "DS", "score": 0.9},
            
            # Risk Assessment
            {"control_id": "RA-3", "framework": "NIST 800-53", "component": "CD", "score": 0.7},
            {"control_id": "RA-5", "framework": "NIST 800-53", "component": "CD", "score": 0.8},
            
            # System and Information Integrity
            {"control_id": "SI-4", "framework": "NIST 800-53", "component": "CD", "score": 0.9},
            {"control_id": "SI-7", "framework": "NIST 800-53", "component": "CD", "score": 0.6},
        ]
        
        count = 0
        for mapping in default_mappings:
            try:
                self.add_mapping(
                    control_id=mapping["control_id"],
                    control_framework=mapping["framework"],
                    zta_component_id=mapping["component"],
                    relevance_score=mapping["score"],
                    implementation_notes=f"Default mapping based on NIST SP 800-207"
                )
                count += 1
            except Exception as e:
                logger.warning(f"Error adding default mapping: {str(e)}")
        
        return count