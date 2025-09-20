"""
GPT-powered API endpoints for PolicyEdgeAI.

This module provides API routes for accessing GPT/Claude compliance Q&A
capabilities, including advanced roadmaps, templates, multi-provider comparisons,
and direct communication with GPT models.
"""
import os
import json
import logging
from typing import List, Optional, Dict, Any, Literal
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from utils.auth import get_current_user
from qa_module.gpt_qa import GPTComplianceQA

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
gpt = APIRouter(prefix="/gpt", tags=["gpt"])

# Setup GPT QA instance
gpt_qa = GPTComplianceQA(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo"),
    base_url=os.getenv("OPENAI_API_BASE", None),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    anthropic_model=os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
)


# Pydantic models for requests
class GptQuestionRequest(BaseModel):
    question: str = Field(..., description="Question about compliance")
    control_ids: Optional[List[str]] = Field(None, description="Control IDs to reference")
    provider: Optional[Literal["openai", "anthropic"]] = Field(None, description="LLM provider to use")


class GptImplementationRequest(BaseModel):
    control_id: str = Field(..., description="Control ID to generate implementation guidance for")
    provider: Optional[Literal["openai", "anthropic"]] = Field(None, description="LLM provider to use")


class GptRoadmapRequest(BaseModel):
    framework: str = Field(..., description="Compliance framework")
    organization_size: str = Field(..., description="Size of organization (small, medium, large, enterprise)")
    industry: str = Field(..., description="Organization's industry")
    timeframe: str = Field(..., description="Desired implementation timeframe")
    current_maturity: str = Field(..., description="Current security maturity level")
    provider: Optional[Literal["openai", "anthropic"]] = Field(None, description="LLM provider to use")


class GptDocumentationTemplateRequest(BaseModel):
    control_id: str = Field(..., description="Control ID to generate documentation template for")
    provider: Optional[Literal["openai", "anthropic"]] = Field(None, description="LLM provider to use")


class GptDirectRequest(BaseModel):
    prompt: str = Field(..., description="User message to send to the model")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt to guide model behavior")
    max_tokens: Optional[int] = Field(1000, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature (0.0 to 1.0)")
    provider: Optional[Literal["openai", "anthropic"]] = Field(None, description="LLM provider to use")


@gpt.post("/question", summary="Ask a question about compliance using GPT")
async def ask_gpt_question(
    request: GptQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ask a natural language question about compliance using GPT models.
    
    Provides enhanced responses using the latest GPT models with contextual
    control information and citations.
    """
    try:
        answer = gpt_qa.ask(request.question, request.control_ids, request.provider)
        
        return JSONResponse(
            content=answer,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error answering GPT question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.post("/implementation", summary="Generate implementation guidance using GPT")
async def generate_gpt_implementation(
    request: GptImplementationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate implementation guidance for a specific control using GPT.
    
    Creates detailed, actionable guidance for implementing 
    a specific security control with GPT intelligence.
    """
    try:
        guidance = gpt_qa.generate_implementation_guidance(request.control_id, request.provider)
        
        if "error" in guidance and guidance.get("error") == "Control not found":
            raise HTTPException(status_code=404, detail=f"Control {request.control_id} not found")
        
        return JSONResponse(
            content=guidance,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating GPT implementation guidance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.get("/providers", summary="Get available LLM providers")
async def get_available_providers(
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about available LLM providers and their configured models.
    
    Returns which providers are available and their configured models.
    """
    providers = {}
    
    if gpt_qa.client:
        providers["openai"] = {
            "available": True,
            "model": gpt_qa.model
        }
    else:
        providers["openai"] = {
            "available": False
        }
    
    if gpt_qa.anthropic_client:
        providers["anthropic"] = {
            "available": True,
            "model": gpt_qa.anthropic_model
        }
    else:
        providers["anthropic"] = {
            "available": False
        }
    
    return JSONResponse(
        content={"providers": providers},
        status_code=200
    )


@gpt.post("/compare", summary="Compare responses from different LLM providers")
async def compare_providers(
    request: GptQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare responses from different LLM providers for the same question.
    
    Gets responses from all available providers and returns them for comparison.
    """
    try:
        comparison = gpt_qa.compare_llm_providers(request.question, request.control_ids)
        
        return JSONResponse(
            content=comparison,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error comparing LLM providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.post("/roadmap", summary="Generate a comprehensive compliance roadmap")
async def generate_compliance_roadmap(
    request: GptRoadmapRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a comprehensive compliance roadmap with implementation timeline.
    
    Creates a detailed roadmap customized to organization size, industry,
    and current maturity level with specific phases and milestones.
    """
    try:
        roadmap = gpt_qa.generate_compliance_roadmap(
            request.framework,
            request.organization_size,
            request.industry,
            request.timeframe,
            request.current_maturity,
            request.provider
        )
        
        return JSONResponse(
            content=roadmap,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating compliance roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.post("/documentation-template", summary="Generate a control documentation template")
async def generate_documentation_template(
    request: GptDocumentationTemplateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a documentation template for a specific control.
    
    Creates a structured template for documenting control implementation,
    evidence collection, and assessment methodology.
    """
    try:
        template = gpt_qa.generate_control_documentation_template(request.control_id, request.provider)
        
        if "error" in template and template.get("error") == "Control not found":
            raise HTTPException(status_code=404, detail=f"Control {request.control_id} not found")
        
        return JSONResponse(
            content=template,
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating documentation template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.post("/chat", summary="Send a direct message to GPT/Claude models")
async def chat_with_gpt(
    request: GptDirectRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a direct message to GPT/Claude models and get a response.
    
    This endpoint allows direct communication with LLM models without any
    specific compliance context. Useful for general AI assistance.
    """
    try:
        # Get default system prompt if not provided
        system_prompt = request.system_prompt
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant specializing in compliance, 
            security, and regulatory frameworks. Provide clear, accurate, and helpful
            responses while following these guidelines:
            
            1. Be truthful and accurate in your responses
            2. If you don't know something, say so rather than making up information
            3. Format responses in markdown for readability
            4. When citing regulations or frameworks, be specific about sources
            5. Provide practical, actionable guidance when appropriate
            """
        
        # Query the model directly
        response = gpt_qa.query_llm(
            system_prompt=system_prompt,
            user_prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            provider=request.provider
        )
        
        # Extract the provider used
        provider_used = gpt_qa.determine_llm_provider(request.provider)
        
        # Prepare and return response
        return JSONResponse(
            content={
                "response": response["content"],
                "model": gpt_qa.model if provider_used == "openai" else gpt_qa.anthropic_model,
                "provider": provider_used,
                "usage": response["usage"]
            },
            status_code=200
        )
    except ValueError as e:
        # Handle case where no API keys are configured
        if "No LLM provider available" in str(e):
            raise HTTPException(
                status_code=400, 
                detail="No LLM provider available. Please configure OpenAI or Anthropic API keys."
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in direct GPT chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@gpt.post("/simple-chat", summary="Simple GPT/Claude chat without authentication")
async def simple_chat(
    request: GptDirectRequest
):
    """
    Simple endpoint for direct GPT/Claude interaction without authentication.
    
    This endpoint is useful for quick testing and integration. It does not
    require authentication, making it easier to use in development.
    
    NOTE: In production, consider requiring authentication for all LLM interactions.
    """
    try:
        # Get default system prompt if not provided
        system_prompt = request.system_prompt
        if not system_prompt:
            system_prompt = "You are a helpful assistant providing clear, concise responses."
        
        # Query the model directly
        response = gpt_qa.query_llm(
            system_prompt=system_prompt,
            user_prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            provider=request.provider
        )
        
        # Prepare a simpler response format
        return JSONResponse(
            content={
                "text": response["content"],
                "model": gpt_qa.model if gpt_qa.determine_llm_provider(request.provider) == "openai" else gpt_qa.anthropic_model
            },
            status_code=200
        )
    except ValueError as e:
        # Handle case where no API keys are configured
        if "No LLM provider available" in str(e):
            raise HTTPException(
                status_code=400, 
                detail="No API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment."
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in simple GPT chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))