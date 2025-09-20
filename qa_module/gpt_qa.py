"""
GPT-powered Q&A Module for compliance questions.

This module provides enhanced GPT capabilities for compliance questions,
explanations, and implementation guidance using the latest GPT models.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Literal
import time
import re
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GPTComplianceQA:
    """GPT-powered Compliance Q&A system with enhanced capabilities."""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "gpt-4-turbo", 
                 base_url: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 anthropic_model: str = "claude-3-opus-20240229"):
        """
        Initialize the GPT Compliance Q&A system.
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to env var)
            model (str): Model to use for GPT queries (default: gpt-4-turbo)
            base_url (str, optional): Alternative API base URL (for Azure, etc.)
            anthropic_api_key (str, optional): Anthropic API key for Claude models
            anthropic_model (str): Claude model to use if anthropic_api_key is provided
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        
        self.model = model
        self.anthropic_model = anthropic_model
        self.base_url = base_url
        
        # Set up API client based on available keys
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except ImportError:
                logger.warning("OpenAI library not installed. Run 'pip install openai'")
                self.client = None
        else:
            logger.warning("No OpenAI API key provided. GPT functionality will be limited.")
            self.client = None
            
        # Set up Anthropic client if API key is provided
        if self.anthropic_api_key:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
                logger.info(f"Anthropic client initialized with model: {self.anthropic_model}")
            except ImportError:
                logger.warning("Anthropic library not installed. Run 'pip install anthropic'")
                self.anthropic_client = None
        else:
            logger.warning("No Anthropic API key provided. Claude functionality will be disabled.")
            self.anthropic_client = None
        
        # Cache to store recent query results
        self.cache = {}
        
        # Load control data
        self.controls = []
        self.control_lookup = {}
        self.load_controls()
    
    def load_controls(self, data_path: Optional[str] = None):
        """
        Load control data from JSON files.
        
        Args:
            data_path (str, optional): Path to data directory
        """
        if not data_path:
            data_path = os.path.join(os.getcwd(), "data", "converted")
        
        if not os.path.exists(data_path):
            logger.warning(f"Data path does not exist: {data_path}")
            return
        
        try:
            # Find all JSON files in the data directory
            json_files = [f for f in os.listdir(data_path) if f.endswith('.json')]
            
            for file in json_files:
                try:
                    with open(os.path.join(data_path, file), 'r') as f:
                        data = json.load(f)
                        
                    # Extract controls
                    if "controls" in data:
                        for control in data["controls"]:
                            # Add to controls list
                            self.controls.append(control)
                            
                            # Add to lookup dictionary
                            control_id = control.get("id")
                            if control_id:
                                self.control_lookup[control_id] = control
                
                except Exception as e:
                    logger.error(f"Error loading {file}: {str(e)}")
            
            logger.info(f"Loaded {len(self.controls)} controls from {len(json_files)} files")
            
        except Exception as e:
            logger.error(f"Error loading controls: {str(e)}")
    
    def get_control_by_id(self, control_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a control by its ID.
        
        Args:
            control_id (str): Control ID
            
        Returns:
            Optional[Dict[str, Any]]: Control data or None if not found
        """
        return self.control_lookup.get(control_id.strip().upper())
    
    def search_controls(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search controls using simple keyword matching.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Matching controls
        """
        query = query.lower()
        
        # Split query into keywords
        keywords = [k.strip() for k in query.split() if len(k.strip()) > 2]
        
        # Score each control
        scored_controls = []
        for control in self.controls:
            score = 0
            
            # Check ID (high weight)
            if query in control.get("id", "").lower():
                score += 10
            
            # Check title (high weight)
            for keyword in keywords:
                if keyword in control.get("title", "").lower():
                    score += 5
            
            # Check description (lower weight)
            for keyword in keywords:
                if keyword in control.get("description", "").lower():
                    score += 2
            
            # Check family (medium weight)
            for keyword in keywords:
                if keyword in control.get("family", "").lower():
                    score += 3
            
            if score > 0:
                scored_controls.append((score, control))
        
        # Sort by score (descending) and return top results
        scored_controls.sort(reverse=True)
        return [control for (_, control) in scored_controls[:limit]]
    
    def determine_llm_provider(self, provider_preference: Optional[Literal["openai", "anthropic"]] = None) -> Literal["openai", "anthropic", "none"]:
        """
        Determine which LLM provider to use based on availability and preference.
        
        Args:
            provider_preference (str, optional): Preferred provider ("openai" or "anthropic")
            
        Returns:
            str: Provider to use ("openai", "anthropic", or "none")
        """
        if provider_preference == "openai" and self.client:
            return "openai"
        
        if provider_preference == "anthropic" and self.anthropic_client:
            return "anthropic"
        
        # If no preference or preferred provider not available, use what's available
        if self.client:
            return "openai"
        
        if self.anthropic_client:
            return "anthropic"
        
        return "none"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_gpt(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Query OpenAI GPT models with retry logic.
        
        Args:
            system_prompt (str): System role content
            user_prompt (str): User role content
            max_tokens (int): Maximum tokens to generate
            temperature (float): Sampling temperature
            
        Returns:
            Dict[str, Any]: Response with content and usage statistics
        """
        if not self.client:
            raise ValueError("OpenAI client not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response.choices[0].message.content.strip(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"Error querying GPT: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Query Anthropic Claude models with retry logic.
        
        Args:
            system_prompt (str): System role content
            user_prompt (str): User role content
            max_tokens (int): Maximum tokens to generate
            temperature (float): Sampling temperature
            
        Returns:
            Dict[str, Any]: Response with content and usage statistics
        """
        if not self.anthropic_client:
            raise ValueError("Anthropic client not configured")
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"Error querying Claude: {str(e)}")
            raise
    
    def query_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, 
                  temperature: float = 0.3, provider: Optional[Literal["openai", "anthropic"]] = None) -> Dict[str, Any]:
        """
        Query LLM provider based on availability and preference.
        
        Args:
            system_prompt (str): System role content
            user_prompt (str): User role content
            max_tokens (int): Maximum tokens to generate
            temperature (float): Sampling temperature
            provider (str, optional): Provider preference ("openai" or "anthropic")
            
        Returns:
            Dict[str, Any]: Response with content and usage statistics
        """
        provider_to_use = self.determine_llm_provider(provider)
        
        if provider_to_use == "openai":
            return self.query_gpt(system_prompt, user_prompt, max_tokens, temperature)
        
        if provider_to_use == "anthropic":
            return self.query_claude(system_prompt, user_prompt, max_tokens, temperature)
        
        raise ValueError("No LLM provider available. Configure either OpenAI or Anthropic API keys.")
    
    def ask(self, question: str, context: Optional[List[str]] = None, 
            provider: Optional[Literal["openai", "anthropic"]] = None) -> Dict[str, Any]:
        """
        Ask a question about compliance using the specified LLM provider.
        
        Args:
            question (str): The question to ask
            context (List[str], optional): List of control IDs to provide as context
            provider (str, optional): LLM provider to use ("openai" or "anthropic")
            
        Returns:
            Dict[str, Any]: Response with answer and references
        """
        provider_to_use = self.determine_llm_provider(provider)
        
        if provider_to_use == "none":
            return {
                "answer": "API key not configured. Cannot generate response.",
                "references": [],
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"{question}_{','.join(context or [])}_{provider_to_use}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Prepare context
            context_text = ""
            references = []
            
            if context:
                # Add specified controls to context
                for control_id in context:
                    control = self.get_control_by_id(control_id)
                    if control:
                        context_text += f"\nControl ID: {control.get('id')}\n"
                        context_text += f"Title: {control.get('title')}\n"
                        context_text += f"Description: {control.get('description')}\n"
                        context_text += f"Family: {control.get('family')}\n"
                        context_text += f"Framework: {control.get('framework')}\n"
                        context_text += f"Source: {control.get('source')}\n\n"
                        
                        references.append({
                            "id": control.get("id"),
                            "title": control.get("title"),
                            "framework": control.get("framework"),
                            "source": control.get("source")
                        })
            else:
                # Find relevant controls using search
                relevant_controls = self.search_controls(question)
                for control in relevant_controls:
                    context_text += f"\nControl ID: {control.get('id')}\n"
                    context_text += f"Title: {control.get('title')}\n"
                    context_text += f"Description: {control.get('description')}\n"
                    context_text += f"Family: {control.get('family')}\n"
                    context_text += f"Framework: {control.get('framework')}\n"
                    context_text += f"Source: {control.get('source')}\n\n"
                    
                    references.append({
                        "id": control.get("id"),
                        "title": control.get("title"),
                        "framework": control.get("framework"),
                        "source": control.get("source")
                    })
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance expert assistant specialized in cybersecurity frameworks like NIST 800-53, HIPAA, and others.
Answer questions about compliance requirements, control implementations, and regulatory guidelines.
Base your answers on the control information provided and your knowledge of compliance frameworks.
Always cite specific controls in your answer and be precise about requirements.
If you're not sure about something, acknowledge the limitations rather than making up information.
Format your response using markdown for readability.
"""

            # Prepare user prompt
            user_prompt = f"""Question: {question}

Relevant controls and context:
{context_text}

Please provide a clear, accurate answer about the compliance requirements, citing specific controls where appropriate.
"""

            # Query LLM
            response = self.query_llm(system_prompt, user_prompt, 1000, 0.3, provider)
            
            # Extract answer
            answer = response["content"]
            
            # Prepare result
            result = {
                "answer": answer,
                "references": references,
                "model": self.model if provider_to_use == "openai" else self.anthropic_model,
                "provider": provider_to_use,
                "usage": response["usage"]
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "references": [],
                "error": str(e)
            }
    
    def generate_implementation_guidance(self, control_id: str, 
                                        provider: Optional[Literal["openai", "anthropic"]] = None) -> Dict[str, Any]:
        """
        Generate implementation guidance for a specific control.
        
        Args:
            control_id (str): Control ID
            provider (str, optional): LLM provider to use ("openai" or "anthropic")
            
        Returns:
            Dict[str, Any]: Implementation guidance
        """
        provider_to_use = self.determine_llm_provider(provider)
        
        if provider_to_use == "none":
            return {
                "guidance": "API key not configured. Cannot generate guidance.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"guidance_{control_id}_{provider_to_use}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Get control
            control = self.get_control_by_id(control_id)
            if not control:
                return {
                    "guidance": f"Control {control_id} not found.",
                    "error": "Control not found"
                }
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance implementation expert specialized in cybersecurity frameworks.
Your task is to provide detailed, actionable implementation guidance for specific security controls.
Focus on practical steps, technical considerations, and best practices.
Include specific tools, configurations, or processes where applicable.
Format your response using markdown, with clear sections and bullet points for actions.
"""

            # Prepare user prompt
            user_prompt = f"""Control ID: {control.get('id')}
Title: {control.get('title')}
Description: {control.get('description')}
Framework: {control.get('framework')}
Source: {control.get('source')}

Please provide detailed implementation guidance for this control, including:
1. Practical steps for implementation
2. Technical solutions or tools that can help meet this requirement
3. Common pitfalls or challenges
4. How to verify and document compliance
5. Best practices for maintaining compliance over time

Format the guidance with clear sections and actionable items.
"""

            # Query LLM
            response = self.query_llm(system_prompt, user_prompt, 1500, 0.2, provider)
            
            # Extract guidance
            guidance = response["content"]
            
            # Prepare result
            result = {
                "control": {
                    "id": control.get("id"),
                    "title": control.get("title"),
                    "framework": control.get("framework"),
                    "source": control.get("source")
                },
                "guidance": guidance,
                "model": self.model if provider_to_use == "openai" else self.anthropic_model,
                "provider": provider_to_use,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": response["usage"]
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating implementation guidance: {str(e)}")
            return {
                "guidance": f"An error occurred: {str(e)}",
                "error": str(e)
            }
    
    def compare_llm_providers(self, question: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare responses from different LLM providers for the same question.
        
        Args:
            question (str): The question to ask
            context (List[str], optional): List of control IDs to provide as context
            
        Returns:
            Dict[str, Any]: Responses from different providers
        """
        results = {}
        
        # Check if OpenAI client is available
        if self.client:
            try:
                openai_response = self.ask(question, context, provider="openai")
                results["openai"] = openai_response
            except Exception as e:
                logger.error(f"Error getting OpenAI response: {str(e)}")
                results["openai"] = {"error": str(e)}
        
        # Check if Anthropic client is available
        if self.anthropic_client:
            try:
                anthropic_response = self.ask(question, context, provider="anthropic")
                results["anthropic"] = anthropic_response
            except Exception as e:
                logger.error(f"Error getting Anthropic response: {str(e)}")
                results["anthropic"] = {"error": str(e)}
        
        return {
            "question": question,
            "results": results,
            "comparison_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def extract_references_from_text(self, text: str) -> List[str]:
        """
        Extract control references from answer text.
        
        Args:
            text (str): Text to extract references from
            
        Returns:
            List[str]: List of control references
        """
        # Common patterns for control IDs
        patterns = [
            r'([A-Z]{2}-\d+)',  # Format like AC-1
            r'(\d+\.\d+\.\d+)',  # Format like 3.1.1
            r'(?:Control|control|requirement|Requirement) ([A-Z0-9\.-]+)'  # Controls mentioned by name
        ]
        
        references = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            references.update(matches)
        
        return list(references)
    
    def generate_compliance_roadmap(self, 
                                   framework: str, 
                                   organization_size: str,
                                   industry: str,
                                   timeframe: str,
                                   current_maturity: str,
                                   provider: Optional[Literal["openai", "anthropic"]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance roadmap with implementation timeline.
        
        Args:
            framework (str): Compliance framework
            organization_size (str): Size of organization (small, medium, large, enterprise)
            industry (str): Organization's industry
            timeframe (str): Desired implementation timeframe
            current_maturity (str): Current security maturity level
            provider (str, optional): LLM provider to use ("openai" or "anthropic")
            
        Returns:
            Dict[str, Any]: Comprehensive roadmap
        """
        provider_to_use = self.determine_llm_provider(provider)
        
        if provider_to_use == "none":
            return {
                "roadmap": "API key not configured. Cannot generate roadmap.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"roadmap_{framework}_{organization_size}_{industry}_{timeframe}_{current_maturity}_{provider_to_use}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Find framework controls
            framework_controls = [c for c in self.controls if c.get("framework") == framework]
            
            # Prepare context with a sample of controls (max 5 for prompt size)
            context_text = ""
            
            # Group controls by family for better context
            families = {}
            for control in framework_controls:
                family = control.get("family", "Other")
                if family not in families:
                    families[family] = []
                families[family].append(control)
            
            # Add a sample of controls from each family
            for family, controls in families.items():
                context_text += f"\nFamily: {family}\n"
                context_text += f"Control Count: {len(controls)}\n"
                sample = controls[:2]  # Take first 2 controls as samples
                for control in sample:
                    context_text += f"- {control.get('id')}: {control.get('title')}\n"
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance roadmap planning expert specialized in cybersecurity frameworks and regulations.
Your task is to create a comprehensive compliance implementation roadmap tailored to specific organization needs.
Focus on providing practical, actionable steps organized into realistic phases and timeline.
Include resource requirements, key stakeholders, and critical dependencies.
Identify high-priority controls that should be addressed first based on risk and impact.
Format your response using markdown with clear sections, phases, and milestones.
"""

            # Prepare user prompt
            user_prompt = f"""Framework: {framework}
Organization Size: {organization_size}
Industry: {industry}
Current Security Maturity: {current_maturity}
Implementation Timeframe: {timeframe}

Framework overview:
{context_text}

Please generate a comprehensive compliance roadmap that includes:

1. Executive Summary
   - Key objectives and business benefits
   - Resource requirements overview

2. Current State Assessment
   - Gap analysis approach
   - Key areas likely needing attention based on industry and size

3. Implementation Phases with Timeline
   - Phase 1: Foundation (with specific weeks/months)
   - Phase 2: Core Implementation (with specific weeks/months)
   - Phase 3: Advanced Controls (with specific weeks/months)
   - Phase 4: Optimization and Continuous Improvement

4. Priority Controls by Phase
   - List specific high-priority controls to implement first
   - Group remaining controls by implementation phase
   - Provide rationale for prioritization

5. Resource Requirements
   - Staffing needs by role and phase
   - Technology investments
   - Potential external support requirements

6. Key Stakeholders and Responsibilities
   - RACI matrix overview
   - Cross-functional dependencies

7. Verification and Evidence Collection Strategy
   - How to document compliance
   - Continuous monitoring approach

The roadmap should be realistic for an {organization_size} organization in the {industry} industry with {current_maturity} current maturity, achievable within the specified {timeframe} timeframe.
"""

            # Query LLM
            response = self.query_llm(system_prompt, user_prompt, 2500, 0.3, provider)
            
            # Extract roadmap
            roadmap = response["content"]
            
            # Prepare result
            result = {
                "framework": framework,
                "organization_info": {
                    "size": organization_size,
                    "industry": industry,
                    "current_maturity": current_maturity,
                    "timeframe": timeframe
                },
                "control_count": len(framework_controls),
                "families": list(families.keys()),
                "roadmap": roadmap,
                "model": self.model if provider_to_use == "openai" else self.anthropic_model,
                "provider": provider_to_use,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": response["usage"]
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating compliance roadmap: {str(e)}")
            return {
                "roadmap": f"An error occurred: {str(e)}",
                "error": str(e)
            }
    
    def generate_control_documentation_template(self, control_id: str, 
                                              provider: Optional[Literal["openai", "anthropic"]] = None) -> Dict[str, Any]:
        """
        Generate a documentation template for a specific control.
        
        Args:
            control_id (str): Control ID
            provider (str, optional): LLM provider to use ("openai" or "anthropic")
            
        Returns:
            Dict[str, Any]: Documentation template
        """
        provider_to_use = self.determine_llm_provider(provider)
        
        if provider_to_use == "none":
            return {
                "template": "API key not configured. Cannot generate template.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"template_{control_id}_{provider_to_use}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Get control
            control = self.get_control_by_id(control_id)
            if not control:
                return {
                    "template": f"Control {control_id} not found.",
                    "error": "Control not found"
                }
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance documentation expert specialized in cybersecurity frameworks.
Your task is to create a comprehensive documentation template for a specific security control.
The template should help organizations document their implementation and gather appropriate evidence.
Focus on practical fields, required evidence, and verification methods.
Format your response using markdown, with clear sections and fields.
"""

            # Prepare user prompt
            user_prompt = f"""Control ID: {control.get('id')}
Title: {control.get('title')}
Description: {control.get('description')}
Framework: {control.get('framework')}
Source: {control.get('source')}

Please create a comprehensive documentation template for this control, including:

1. Control Overview Section
   - Fields for control identifiers, references, and dependencies
   - Responsibility assignments (roles)

2. Implementation Details Section
   - Policy references
   - Technical implementation specifics
   - Procedural implementation specifics

3. Evidence Collection Section
   - Types of evidence required
   - Evidence collection frequency
   - Evidence storage location

4. Assessment & Testing Section
   - Assessment methods
   - Testing procedures
   - Testing frequency

5. Risk Assessment Section
   - Potential risks if control fails
   - Potential impacts
   - Compensating controls

6. Approval & Review Section
   - Approval workflow
   - Review timeline
   - Change management process

Format the template with clear sections, fields with descriptions, and examples where helpful.
"""

            # Query LLM
            response = self.query_llm(system_prompt, user_prompt, 1500, 0.2, provider)
            
            # Extract template
            template = response["content"]
            
            # Prepare result
            result = {
                "control": {
                    "id": control.get("id"),
                    "title": control.get("title"),
                    "framework": control.get("framework"),
                    "source": control.get("source")
                },
                "template": template,
                "model": self.model if provider_to_use == "openai" else self.anthropic_model,
                "provider": provider_to_use,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": response["usage"]
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating documentation template: {str(e)}")
            return {
                "template": f"An error occurred: {str(e)}",
                "error": str(e)
            }