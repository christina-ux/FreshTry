"""
LLM-powered Q&A Module for compliance questions.

This module provides capability to ask natural language questions about compliance,
get explanations, and generate implementation guidance.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
import time
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComplianceQA:
    """LLM-powered Compliance Q&A system."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the Compliance Q&A system.
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to env var)
            model (str): Model to use for LLM queries (default: gpt-4)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided for LLM. Q&A functionality will be limited.")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
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
    
    def ask(self, question: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ask a question about compliance.
        
        Args:
            question (str): The question to ask
            context (List[str], optional): List of control IDs to provide as context
            
        Returns:
            Dict[str, Any]: Response with answer and references
        """
        if not self.client:
            return {
                "answer": "API key not configured. Cannot generate response.",
                "references": [],
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"{question}_{','.join(context or [])}"
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

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Extract answer
            answer = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "answer": answer,
                "references": references,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
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
    
    def generate_implementation_guidance(self, control_id: str) -> Dict[str, Any]:
        """
        Generate implementation guidance for a specific control.
        
        Args:
            control_id (str): Control ID
            
        Returns:
            Dict[str, Any]: Implementation guidance
        """
        if not self.client:
            return {
                "guidance": "API key not configured. Cannot generate guidance.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"guidance_{control_id}"
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

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            # Extract guidance
            guidance = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "control": {
                    "id": control.get("id"),
                    "title": control.get("title"),
                    "framework": control.get("framework"),
                    "source": control.get("source")
                },
                "guidance": guidance,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
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
    
    def explain_control_mapping(self, source_control_id: str, target_control_id: str) -> Dict[str, Any]:
        """
        Explain how two controls from different frameworks map to each other.
        
        Args:
            source_control_id (str): Source control ID
            target_control_id (str): Target control ID
            
        Returns:
            Dict[str, Any]: Explanation of mapping
        """
        if not self.client:
            return {
                "explanation": "API key not configured. Cannot generate explanation.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"mapping_{source_control_id}_{target_control_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Get controls
            source_control = self.get_control_by_id(source_control_id)
            target_control = self.get_control_by_id(target_control_id)
            
            if not source_control:
                return {
                    "explanation": f"Source control {source_control_id} not found.",
                    "error": "Source control not found"
                }
            
            if not target_control:
                return {
                    "explanation": f"Target control {target_control_id} not found.",
                    "error": "Target control not found"
                }
            
            # Prepare system prompt
            system_prompt = f"""You are an expert in compliance framework mapping.
Your task is to explain how controls from different frameworks relate to each other.
Analyze the similarities, differences, and coverage between the two controls.
Provide detailed explanation of the relationship, including any gaps or overlaps.
Use specific language from the control descriptions to support your analysis.
Format your response using markdown for readability.
"""

            # Prepare user prompt
            user_prompt = f"""Source Control:
ID: {source_control.get('id')}
Title: {source_control.get('title')}
Description: {source_control.get('description')}
Framework: {source_control.get('framework')}
Source: {source_control.get('source')}

Target Control:
ID: {target_control.get('id')}
Title: {target_control.get('title')}
Description: {target_control.get('description')}
Framework: {target_control.get('framework')}
Source: {target_control.get('source')}

Please explain how these two controls map to each other:
1. Key similarities and differences
2. How the controls overlap in requirements
3. Any gaps where one control covers requirements not addressed by the other
4. The strength of the mapping relationship (strong, moderate, weak)
5. Special considerations for compliance with both controls
"""

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            # Extract explanation
            explanation = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "source_control": {
                    "id": source_control.get("id"),
                    "title": source_control.get("title"),
                    "framework": source_control.get("framework"),
                    "source": source_control.get("source")
                },
                "target_control": {
                    "id": target_control.get("id"),
                    "title": target_control.get("title"),
                    "framework": target_control.get("framework"),
                    "source": target_control.get("source")
                },
                "explanation": explanation,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating mapping explanation: {str(e)}")
            return {
                "explanation": f"An error occurred: {str(e)}",
                "error": str(e)
            }
    
    def generate_compliance_plan(self, framework: str, scope: str, timeframe: str) -> Dict[str, Any]:
        """
        Generate a compliance implementation plan for a specific framework.
        
        Args:
            framework (str): Compliance framework
            scope (str): Scope of implementation
            timeframe (str): Desired timeframe for implementation
            
        Returns:
            Dict[str, Any]: Implementation plan
        """
        if not self.client:
            return {
                "plan": "API key not configured. Cannot generate plan.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"plan_{framework}_{hash(scope)}_{hash(timeframe)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Find framework controls
            framework_controls = [c for c in self.controls if c.get("framework") == framework]
            
            # Prepare context with a sample of controls (max 5 for prompt size)
            context_text = ""
            if framework_controls:
                sample_controls = framework_controls[:5]
                for control in sample_controls:
                    context_text += f"\nControl ID: {control.get('id')}\n"
                    context_text += f"Title: {control.get('title')}\n"
                    context_text += f"Description: {control.get('description')[:200]}...\n"
                    context_text += f"Family: {control.get('family')}\n\n"
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance planning expert specializing in cybersecurity frameworks and regulations.
Your task is to create a comprehensive compliance implementation plan tailored to specific needs.
Focus on providing practical, actionable steps organized into phases.
Include timelines, resource considerations, and key stakeholders.
Identify high-priority controls that should be addressed first.
Format your response using markdown with clear sections and timelines.
"""

            # Prepare user prompt
            user_prompt = f"""Framework: {framework}
Scope: {scope}
Timeframe: {timeframe}

Sample controls from this framework:
{context_text}

Please generate a comprehensive compliance implementation plan that includes:
1. Initial assessment and gap analysis approach
2. Implementation phases with clear milestones
3. Priority controls to address first
4. Resource requirements and stakeholder involvement
5. Documentation and evidence collection strategy
6. Verification and ongoing monitoring approach

The plan should be realistic for the given timeframe and provide actionable guidance.
"""

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.4
            )
            
            # Extract plan
            plan = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "framework": framework,
                "scope": scope,
                "timeframe": timeframe,
                "plan": plan,
                "control_count": len(framework_controls),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating compliance plan: {str(e)}")
            return {
                "plan": f"An error occurred: {str(e)}",
                "error": str(e)
            }
    
    def analyze_control_gaps(self, implemented_controls: List[str], framework: str) -> Dict[str, Any]:
        """
        Analyze gaps between implemented controls and framework requirements.
        
        Args:
            implemented_controls (List[str]): List of implemented control IDs
            framework (str): Target compliance framework
            
        Returns:
            Dict[str, Any]: Gap analysis results
        """
        if not self.client:
            return {
                "analysis": "API key not configured. Cannot generate analysis.",
                "error": "No API key provided"
            }
        
        # Check cache first
        cache_key = f"gaps_{framework}_{','.join(sorted(implemented_controls))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Find framework controls
            framework_controls = [c for c in self.controls if c.get("framework") == framework]
            
            # Find implemented controls
            implemented = []
            for control_id in implemented_controls:
                control = self.get_control_by_id(control_id)
                if control:
                    implemented.append(control)
            
            # Identify missing controls
            implemented_ids = set(c.get("id") for c in implemented)
            missing_controls = [c for c in framework_controls if c.get("id") not in implemented_ids]
            
            # Prepare context
            implemented_context = "\n".join([f"- {c.get('id')}: {c.get('title')}" for c in implemented[:10]])
            missing_context = "\n".join([f"- {c.get('id')}: {c.get('title')}" for c in missing_controls[:10]])
            
            # Prepare system prompt
            system_prompt = f"""You are a compliance gap analysis expert specialized in cybersecurity frameworks.
Your task is to analyze gaps between implemented controls and framework requirements.
Identify critical gaps, their potential impact, and provide recommendations for addressing them.
Prioritize gaps based on security impact and implementation complexity.
Format your response using markdown with clear sections.
"""

            # Prepare user prompt
            user_prompt = f"""Framework: {framework}
Total Framework Controls: {len(framework_controls)}
Implemented Controls: {len(implemented)} ({len(implemented)*100/len(framework_controls):.1f}% coverage)
Missing Controls: {len(missing_controls)}

Sample Implemented Controls:
{implemented_context}

Sample Missing Controls:
{missing_context}

Please provide a comprehensive gap analysis that includes:
1. Overall assessment of compliance status and gaps
2. Critical gaps that pose the highest risk and should be addressed first
3. Medium-priority gaps that should be addressed in the medium term
4. Analysis of potential impacts of these gaps
5. Recommendations for closing the gaps efficiently
6. Suggested implementation roadmap based on priority and dependencies

Focus on actionable insights and practical recommendations.
"""

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1800,
                temperature=0.3
            )
            
            # Extract analysis
            analysis = response.choices[0].message.content.strip()
            
            # Calculate basic stats for families
            family_stats = {}
            for control in framework_controls:
                family = control.get("family", "Unknown")
                if family not in family_stats:
                    family_stats[family] = {"total": 0, "implemented": 0}
                family_stats[family]["total"] += 1
            
            for control in implemented:
                family = control.get("family", "Unknown")
                if family in family_stats:
                    family_stats[family]["implemented"] += 1
            
            # Calculate coverage for each family
            for family, stats in family_stats.items():
                if stats["total"] > 0:
                    stats["coverage"] = (stats["implemented"] / stats["total"]) * 100
                else:
                    stats["coverage"] = 0
            
            # Prepare result
            result = {
                "framework": framework,
                "total_controls": len(framework_controls),
                "implemented_controls": len(implemented),
                "missing_controls": len(missing_controls),
                "coverage_percentage": (len(implemented) / len(framework_controls) * 100) if framework_controls else 0,
                "family_coverage": family_stats,
                "analysis": analysis,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating gap analysis: {str(e)}")
            return {
                "analysis": f"An error occurred: {str(e)}",
                "error": str(e)
            }