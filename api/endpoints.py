"""
API endpoints for the PolicyEdgeAI application.
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from models.compliance_model import ComplianceModel, ComplianceControl
from ingest.nist_parser import parse_nist_controls
from ingest.hipaa_parser import parse_hipaa_regulations, map_hipaa_to_nist


# Pydantic models for API
class ControlBase(BaseModel):
    """Base model for compliance controls in API requests/responses."""
    id: str
    title: str
    description: str
    source: str
    framework: str
    family: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "AC-1",
                "title": "Access Control Policy and Procedures",
                "description": "The organization develops, documents, and disseminates...",
                "source": "NIST 800-53",
                "framework": "FISMA",
                "family": "Access Control"
            }
        }


class ControlCreate(ControlBase):
    """Model for creating a new control."""
    related_controls: List[str] = []
    mapped_to: List[Dict[str, Any]] = []


class ControlResponse(ControlBase):
    """Model for control responses including relationships."""
    related_controls: List[str] = []
    mapped_to: List[Dict[str, Any]] = []


class GapAnalysisRequest(BaseModel):
    """Request model for gap analysis."""
    framework1: str
    framework2: str


class SearchRequest(BaseModel):
    """Request model for searching controls."""
    framework: Optional[str] = None
    family: Optional[str] = None
    keyword: Optional[str] = None


# API Setup
def create_api(compliance_model: ComplianceModel = None):
    """
    Create and configure the FastAPI application.
    
    Args:
        compliance_model (ComplianceModel, optional): Compliance model instance
        
    Returns:
        FastAPI: Configured FastAPI application
    """
    api = FastAPI(
        title="PolicyEdgeAI API",
        description="API for regulatory compliance analysis and mapping",
        version="1.0.0"
    )
    
    # Set up CORS
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Dependency for getting the compliance model
    def get_compliance_model():
        """Get the compliance model instance."""
        nonlocal compliance_model
        if compliance_model is None:
            # Initialize with default model if not provided
            compliance_model = ComplianceModel()
            
            # Load controls from file if available
            data_file = os.path.join("data", "controls.json")
            if os.path.exists(data_file):
                compliance_model.load_from_file(data_file)
                
        return compliance_model
    
    # API routes
    @api.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint providing API information."""
        return {
            "name": "PolicyEdgeAI API",
            "version": "1.0.0",
            "description": "Regulatory compliance analysis and mapping API"
        }
    
    @api.post("/controls/search", response_model=List[ControlResponse])
    async def search_controls(
        request: SearchRequest,
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Search controls by framework, family, or keyword.
        
        Args:
            request (SearchRequest): Search criteria
            model (ComplianceModel): Compliance model instance
            
        Returns:
            List[ControlResponse]: Matching controls
        """
        controls = model.filter_controls(
            framework=request.framework,
            family=request.family,
            keyword=request.keyword
        )
        
        return [ControlResponse(**control.to_dict()) for control in controls]
    
    @api.get("/controls/{control_id}", response_model=ControlResponse)
    async def get_control(
        control_id: str,
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Get a control by its ID.
        
        Args:
            control_id (str): Control ID to fetch
            model (ComplianceModel): Compliance model instance
            
        Returns:
            ControlResponse: Control details
        """
        control = model.get_control_by_id(control_id)
        if not control:
            raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
        
        return ControlResponse(**control.to_dict())
    
    @api.post("/controls", response_model=ControlResponse)
    async def create_control(
        control: ControlCreate,
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Create a new control.
        
        Args:
            control (ControlCreate): Control to create
            model (ComplianceModel): Compliance model instance
            
        Returns:
            ControlResponse: Created control
        """
        # Check if control already exists
        existing = model.get_control_by_id(control.id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Control {control.id} already exists")
        
        # Create and add control
        new_control = ComplianceControl.from_dict(control.dict())
        model.controls.append(new_control)
        
        # Save updated controls
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        model.save_to_file(os.path.join(data_dir, "controls.json"))
        
        return ControlResponse(**new_control.to_dict())
    
    @api.post("/upload/nist", response_model=Dict[str, Any])
    async def upload_nist_document(
        file: UploadFile = File(...),
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Upload and parse NIST 800-53 document.
        
        Args:
            file (UploadFile): PDF file to upload
            model (ComplianceModel): Compliance model instance
            
        Returns:
            Dict[str, Any]: Upload result information
        """
        # Save uploaded file
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, file.filename)
        
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Parse controls
            controls = parse_nist_controls(file_path)
            model.add_controls(controls)
            
            # Save to file
            model.save_to_file(os.path.join(data_dir, "controls.json"))
            
            return {
                "message": "NIST document processed successfully",
                "controls_found": len(controls),
                "file": file.filename
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing NIST document: {str(e)}"
            )
    
    @api.post("/upload/hipaa", response_model=Dict[str, Any])
    async def upload_hipaa_document(
        file: UploadFile = File(...),
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Upload and parse HIPAA document.
        
        Args:
            file (UploadFile): PDF file to upload
            model (ComplianceModel): Compliance model instance
            
        Returns:
            Dict[str, Any]: Upload result information
        """
        # Save uploaded file
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, file.filename)
        
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Parse regulations
            hipaa_regulations = parse_hipaa_regulations(file_path)
            
            # Get existing NIST controls
            nist_controls = [c.to_dict() for c in model.controls if c.source == "NIST 800-53"]
            
            # Map HIPAA to NIST
            hipaa_regulations = map_hipaa_to_nist(hipaa_regulations, nist_controls)
            
            # Add to model
            model.add_controls(hipaa_regulations)
            
            # Save to file
            model.save_to_file(os.path.join(data_dir, "controls.json"))
            
            return {
                "message": "HIPAA document processed successfully",
                "regulations_found": len(hipaa_regulations),
                "file": file.filename
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing HIPAA document: {str(e)}"
            )
    
    @api.post("/analysis/gap", response_model=Dict[str, Any])
    async def analyze_gap(
        request: GapAnalysisRequest,
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Perform gap analysis between two frameworks.
        
        Args:
            request (GapAnalysisRequest): Frameworks to compare
            model (ComplianceModel): Compliance model instance
            
        Returns:
            Dict[str, Any]: Gap analysis results
        """
        result = model.analyze_compliance_gap(request.framework1, request.framework2)
        return result
    
    @api.post("/analysis/summary")
    async def generate_summary(
        request: SearchRequest,
        model: ComplianceModel = Depends(get_compliance_model)
    ):
        """
        Generate a summary of compliance requirements.
        
        Args:
            request (SearchRequest): Filters for controls to summarize
            model (ComplianceModel): Compliance model instance
            
        Returns:
            Dict[str, str]: Summary
        """
        controls = model.filter_controls(
            framework=request.framework,
            family=request.family,
            keyword=request.keyword
        )
        
        summary = model.generate_compliance_summary(controls)
        return {"summary": summary}
    
    return api