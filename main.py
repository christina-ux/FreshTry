"""
PolicyEdgeAI - Main application entry point.

This application provides tools for parsing, analyzing, and mapping regulatory
compliance requirements across different frameworks (NIST, HIPAA, etc.).
Includes PDF-to-JSON conversion, Zero Trust mapping, compliance reporting,
LLM-powered Q&A capabilities, and integrations with enterprise IT and security tools.
"""
import os
import argparse
import logging
import uvicorn
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv

# Import auth utilities
from utils.auth import get_current_user, Token

# Import components from different modules
from converter.pdf_converter import PDFConverter
from zta_mapping.zta_mapper import ZTAMapper, ReportConfig
from reporting.report_generator import ReportGenerator
from qa_module.llm_qa import ComplianceQA
from qa_module.gpt_qa import GPTComplianceQA
from models.compliance_model import ComplianceModel
from api.integrations import integrations
from api.dashboard import dashboard
from api.scoring import scoring
from api.upload import upload
from api.gpt_api import gpt
from api.intelligence_api import router as intelligence_router

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Pydantic models for API request/response
class ConversionRequest(BaseModel):
    file_path: str = Field(..., description="Path to the PDF file to convert")


class MappingRequest(BaseModel):
    control_id: str = Field(..., description="ID of the control to map")
    control_framework: str = Field(..., description="Framework the control belongs to")
    zta_component_id: str = Field(..., description="ID of the ZTA component to map to")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0 to 1.0)")
    implementation_notes: Optional[str] = Field(None, description="Notes about implementation")


class ReportRequest(BaseModel):
    title: str = Field(..., description="Report title")
    framework: str = Field(..., description="Framework to report on")
    organization: str = Field("Your Organization", description="Organization name")
    include_executive_summary: bool = Field(True, description="Include executive summary")
    include_gap_analysis: bool = Field(True, description="Include gap analysis")
    include_implementation_status: bool = Field(True, description="Include implementation status")
    include_zta_mapping: bool = Field(False, description="Include ZTA mapping")
    output_format: str = Field("pdf", description="Output format ('pdf' or 'html')")


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Question about compliance")
    control_ids: Optional[List[str]] = Field(None, description="Control IDs to reference")


class ImplementationRequest(BaseModel):
    control_id: str = Field(..., description="Control ID to generate implementation guidance for")


class MappingExplanationRequest(BaseModel):
    source_control_id: str = Field(..., description="Source control ID")
    target_control_id: str = Field(..., description="Target control ID")


class CompliancePlanRequest(BaseModel):
    framework: str = Field(..., description="Compliance framework")
    scope: str = Field(..., description="Scope of implementation")
    timeframe: str = Field(..., description="Desired timeframe for implementation")


class GapAnalysisRequest(BaseModel):
    implemented_controls: List[str] = Field(..., description="List of implemented control IDs")
    framework: str = Field(..., description="Target compliance framework")


# Create FastAPI application
app = FastAPI(
    title="PolicyEdgeAI",
    description="Regulatory compliance analysis, mapping, and reporting tool with enterprise integrations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencies for components
def get_pdf_converter():
    return PDFConverter()


def get_zta_mapper():
    return ZTAMapper()


def get_report_generator():
    return ReportGenerator()


def get_compliance_qa():
    api_key = os.getenv("OPENAI_API_KEY")
    return ComplianceQA(api_key=api_key)


def get_gpt_compliance_qa():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
    
    return GPTComplianceQA(
        api_key=openai_api_key,
        model=openai_model,
        base_url=os.getenv("OPENAI_API_BASE", None),
        anthropic_api_key=anthropic_api_key,
        anthropic_model=anthropic_model
    )


def get_compliance_model():
    api_key = os.getenv("OPENAI_API_KEY")
    return ComplianceModel(api_key=api_key)


# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="frontend/templates")

# Include integrations router
app.include_router(integrations)

# Include dashboard router
app.include_router(dashboard)

# Include scoring router
app.include_router(scoring)

# Include upload router
app.include_router(upload)

# Include GPT router
app.include_router(gpt)

# Include Intelligence router
app.include_router(intelligence_router)


# API routes

# Root endpoint (web interface)
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# PDF Converter endpoints
@app.post("/api/convert/pdf", summary="Convert PDF to structured JSON")
async def convert_pdf(
    file: UploadFile = File(...),
    converter: PDFConverter = Depends(get_pdf_converter)
):
    """
    Convert a regulatory PDF document to structured JSON format.
    
    Uploads a PDF file containing regulatory content (NIST, HIPAA, etc.)
    and converts it to a structured JSON representation of controls.
    """
    try:
        # Save uploaded file
        data_dir = os.path.join(os.getcwd(), "data", "uploads")
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, file.filename)
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Convert PDF
        result = converter.convert_pdf(file_path)
        
        return JSONResponse(
            content=result,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error converting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert/batch", summary="Batch convert PDFs in a directory")
async def batch_convert(
    directory: str = Form(...),
    converter: PDFConverter = Depends(get_pdf_converter)
):
    """
    Batch convert all PDFs in a directory to structured JSON.
    
    Processes all PDF files in the specified directory and converts
    them to structured JSON representations of controls.
    """
    try:
        results = converter.batch_convert(directory)
        return JSONResponse(
            content={"results": results},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error batch converting PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ZTA Mapping endpoints
@app.get("/api/zta/components", summary="Get all ZTA components")
async def get_zta_components(
    mapper: ZTAMapper = Depends(get_zta_mapper)
):
    """
    Get all Zero Trust Architecture components.
    
    Returns a list of all ZTA components defined in the system.
    """
    try:
        components = mapper.get_components()
        return JSONResponse(
            content={"components": components},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error getting ZTA components: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zta/component/{component_id}", summary="Get a specific ZTA component")
async def get_zta_component(
    component_id: str,
    mapper: ZTAMapper = Depends(get_zta_mapper)
):
    """
    Get a specific Zero Trust Architecture component by ID.
    
    Returns detailed information about a specific ZTA component.
    """
    try:
        component = mapper.get_component(component_id)
        if not component:
            raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
        
        return JSONResponse(
            content=component,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ZTA component: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zta/mapping", summary="Add a new ZTA mapping")
async def add_zta_mapping(
    request: MappingRequest,
    mapper: ZTAMapper = Depends(get_zta_mapper)
):
    """
    Add a new mapping between a control and a ZTA component.
    
    Creates a relationship between a specific control and a Zero Trust
    Architecture component, with a relevance score and optional notes.
    """
    try:
        mapping = mapper.add_mapping(
            control_id=request.control_id,
            control_framework=request.control_framework,
            zta_component_id=request.zta_component_id,
            relevance_score=request.relevance_score,
            implementation_notes=request.implementation_notes or ""
        )
        
        return JSONResponse(
            content=mapping,
            status_code=200
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding ZTA mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zta/mappings/control/{control_id}", summary="Get ZTA mappings for a control")
async def get_mappings_for_control(
    control_id: str,
    framework: str = Query(None, description="Control framework"),
    mapper: ZTAMapper = Depends(get_zta_mapper)
):
    """
    Get ZTA mappings for a specific control.
    
    Returns all ZTA components mapped to a specific control,
    along with relevance scores and implementation notes.
    """
    try:
        if not framework:
            raise HTTPException(status_code=400, detail="Framework parameter is required")
        
        mappings = mapper.get_mappings_for_control(control_id, framework)
        
        return JSONResponse(
            content={"mappings": mappings},
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mappings for control: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zta/coverage", summary="Generate ZTA coverage report")
async def generate_zta_coverage(
    framework: str = Query(None, description="Filter controls by framework"),
    mapper: ZTAMapper = Depends(get_zta_mapper),
    model: ComplianceModel = Depends(get_compliance_model)
):
    """
    Generate a Zero Trust Architecture coverage report.
    
    Analyzes how well the current controls cover Zero Trust
    Architecture components and principles.
    """
    try:
        # Get controls, optionally filtered by framework
        if framework:
            controls = model.filter_controls(framework=framework)
        else:
            controls = model.controls
        
        # Convert to dict format expected by ZTA mapper
        control_dicts = [c.to_dict() for c in controls]
        
        # Generate coverage report
        coverage = mapper.generate_zta_coverage_report(control_dicts)
        
        return JSONResponse(
            content=coverage,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating ZTA coverage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Reporting endpoints
@app.post("/api/reports/generate", summary="Generate a compliance report")
async def generate_report(
    request: ReportRequest,
    generator: ReportGenerator = Depends(get_report_generator),
    model: ComplianceModel = Depends(get_compliance_model),
    mapper: ZTAMapper = Depends(get_zta_mapper)
):
    """
    Generate a comprehensive compliance report.
    
    Creates a detailed compliance report for a specific framework,
    including status, gaps, and implementation details.
    """
    try:
        # Get controls for the specified framework
        controls = model.filter_controls(framework=request.framework)
        
        if not controls:
            raise HTTPException(status_code=404, detail=f"No controls found for framework {request.framework}")
        
        # Convert to dict format expected by report generator
        control_dicts = [c.to_dict() for c in controls]
        
        # Get ZTA data if requested
        zta_data = None
        if request.include_zta_mapping:
            zta_data = mapper.generate_zta_coverage_report(control_dicts)
        
        # Create report config
        config = ReportConfig(
            title=request.title,
            framework=request.framework,
            organization=request.organization,
            include_executive_summary=request.include_executive_summary,
            include_gap_analysis=request.include_gap_analysis,
            include_implementation_status=request.include_implementation_status,
            include_zta_mapping=request.include_zta_mapping,
            output_format=request.output_format
        )
        
        # Generate report
        report_paths = generator.generate_report(control_dicts, config, zta_data)
        
        # Return the path to the generated report(s)
        return JSONResponse(
            content={"report_paths": report_paths},
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_name}", summary="Download a report")
async def download_report(
    report_name: str
):
    """
    Download a generated report.
    
    Returns the specified report file for download.
    """
    try:
        report_dir = os.path.join(os.getcwd(), "data", "reports")
        report_path = os.path.join(report_dir, report_name)
        
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail=f"Report {report_name} not found")
        
        return FileResponse(report_path, filename=report_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports", summary="List available reports")
async def list_reports():
    """
    List all available reports.
    
    Returns a list of all generated reports available for download.
    """
    try:
        report_dir = os.path.join(os.getcwd(), "data", "reports")
        if not os.path.exists(report_dir):
            return JSONResponse(
                content={"reports": []},
                status_code=200
            )
        
        reports = []
        for filename in os.listdir(report_dir):
            file_path = os.path.join(report_dir, filename)
            if os.path.isfile(file_path):
                reports.append({
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "created": os.path.getctime(file_path)
                })
        
        return JSONResponse(
            content={"reports": reports},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Q&A endpoints
@app.post("/api/qa/question", summary="Ask a question about compliance")
async def ask_question(
    request: QuestionRequest,
    qa: ComplianceQA = Depends(get_compliance_qa)
):
    """
    Ask a natural language question about compliance.
    
    Uses LLM to answer questions about compliance requirements,
    providing references to specific controls.
    """
    try:
        if not qa.client:
            raise HTTPException(status_code=400, detail="API key not configured for Q&A functionality")
        
        answer = qa.ask(request.question, request.control_ids)
        
        return JSONResponse(
            content=answer,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa/implementation", summary="Generate implementation guidance")
async def generate_implementation_guidance(
    request: ImplementationRequest,
    qa: ComplianceQA = Depends(get_compliance_qa)
):
    """
    Generate implementation guidance for a specific control.
    
    Uses LLM to create detailed, actionable guidance for implementing
    a specific security control.
    """
    try:
        if not qa.client:
            raise HTTPException(status_code=400, detail="API key not configured for Q&A functionality")
        
        guidance = qa.generate_implementation_guidance(request.control_id)
        
        if "error" in guidance and guidance.get("error") == "Control not found":
            raise HTTPException(status_code=404, detail=f"Control {request.control_id} not found")
        
        return JSONResponse(
            content=guidance,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating implementation guidance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa/mapping_explanation", summary="Explain control mapping")
async def explain_control_mapping(
    request: MappingExplanationRequest,
    qa: ComplianceQA = Depends(get_compliance_qa)
):
    """
    Explain how two controls from different frameworks map to each other.
    
    Uses LLM to provide a detailed explanation of the relationship between
    two controls from different frameworks.
    """
    try:
        if not qa.client:
            raise HTTPException(status_code=400, detail="API key not configured for Q&A functionality")
        
        explanation = qa.explain_control_mapping(request.source_control_id, request.target_control_id)
        
        if "error" in explanation:
            if explanation.get("error") == "Source control not found":
                raise HTTPException(status_code=404, detail=f"Source control {request.source_control_id} not found")
            if explanation.get("error") == "Target control not found":
                raise HTTPException(status_code=404, detail=f"Target control {request.target_control_id} not found")
        
        return JSONResponse(
            content=explanation,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining control mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa/compliance_plan", summary="Generate compliance plan")
async def generate_compliance_plan(
    request: CompliancePlanRequest,
    qa: ComplianceQA = Depends(get_compliance_qa)
):
    """
    Generate a compliance implementation plan.
    
    Uses LLM to create a comprehensive plan for implementing
    a specific compliance framework.
    """
    try:
        if not qa.client:
            raise HTTPException(status_code=400, detail="API key not configured for Q&A functionality")
        
        plan = qa.generate_compliance_plan(request.framework, request.scope, request.timeframe)
        
        return JSONResponse(
            content=plan,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating compliance plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa/gap_analysis", summary="Analyze compliance gaps")
async def analyze_compliance_gaps(
    request: GapAnalysisRequest,
    qa: ComplianceQA = Depends(get_compliance_qa)
):
    """
    Analyze gaps between implemented controls and framework requirements.
    
    Uses LLM to identify and analyze gaps in compliance coverage,
    providing recommendations for addressing them.
    """
    try:
        if not qa.client:
            raise HTTPException(status_code=400, detail="API key not configured for Q&A functionality")
        
        analysis = qa.analyze_control_gaps(request.implemented_controls, request.framework)
        
        return JSONResponse(
            content=analysis,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error analyzing compliance gaps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint.
    
    Returns a JWT token for use in the Authorization header.
    """
    from utils.auth import authenticate_user, create_access_token
    from datetime import timedelta
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)  # Adjust as needed
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    
    Requires a valid JWT token in the Authorization header.
    """
    return current_user


def main():
    """
    Main entry point for the PolicyEdgeAI application.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="PolicyEdgeAI - Compliance Analysis Tool")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    # PDF conversion command
    convert_parser = subparsers.add_parser("convert", help="Convert PDF documents to JSON")
    convert_parser.add_argument("--input", type=str, required=True, help="Input PDF file or directory")
    convert_parser.add_argument("--output", type=str, help="Output directory (default: data/converted)")
    
    # ZTA mapping command
    zta_parser = subparsers.add_parser("zta", help="Work with ZTA mappings")
    zta_parser.add_argument("--export", type=str, help="Export mappings to CSV file")
    zta_parser.add_argument("--import", dest="import_file", type=str, help="Import mappings from CSV file")
    zta_parser.add_argument("--generate-default", action="store_true", help="Generate default NIST mappings")
    
    # Process arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "api":
        # Run the server
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    elif args.command == "convert":
        # Convert PDF to JSON
        converter = PDFConverter()
        if os.path.isdir(args.input):
            results = converter.batch_convert(args.input)
            print(f"Converted {len(results)} files")
        else:
            result = converter.convert_pdf(args.input)
            print(f"Conversion result: {len(result.get('controls', []))} controls extracted")
    elif args.command == "zta":
        # Work with ZTA mappings
        mapper = ZTAMapper()
        if args.export:
            success = mapper.export_mappings_to_csv(args.export)
            if success:
                print(f"Exported mappings to {args.export}")
            else:
                print("Error exporting mappings")
        elif args.import_file:
            count = mapper.import_mappings_from_csv(args.import_file)
            print(f"Imported {count} mappings from {args.import_file}")
        elif args.generate_default:
            count = mapper.generate_default_nist_mappings()
            print(f"Generated {count} default NIST mappings")
        else:
            print("No ZTA action specified")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()