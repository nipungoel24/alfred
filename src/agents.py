"""
LangGraph-based multi-agent system for email processing
Architecture: Three specialized agents coordinating through a graph workflow
- Classifier Agent: Categorizes emails
- Prioritization Agent: Assigns priority levels
- Response Architect: Generates recommendations and draft responses
"""

from typing import TypedDict, Dict, Any, List, Optional, Annotated
from datetime import datetime
import json
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import operator

from src.logger import setup_logger
from config.settings import (
    MODEL_NAME, TEMPERATURE, MAX_TOKENS, EMAIL_CATEGORIES, 
    PRIORITY_LEVELS, RECOMMENDED_ACTIONS, CATEGORY_KEYWORDS, PRIORITY_RULES,
    GROQ_API_KEY, GROQ_MODEL
)

logger = setup_logger(__name__)

# Helper function to initialize LLM based on configuration
def get_llm():
    """
    Create and return Llama 3 8B LLM instance via Groq.
    This is the ONLY LLM used in this system.
    Uses llama-3.1-8b-instant (fast and efficient model)
    """
    logger.info("Initializing Llama 3 8B LLM via Groq")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    
    try:
        from langchain_groq import ChatGroq
        
        # Use llama-3.1-8b-instant (Groq's fast model)
        model = "llama-3.1-8b-instant"
        
        llm = ChatGroq(
            model=model,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            groq_api_key=GROQ_API_KEY
        )
        
        logger.info(f"Successfully initialized {model} via Groq")
        return llm
        
    except ImportError:
        logger.error("langchain_groq not installed. Please run: pip install langchain-groq")
        raise
    except Exception as e:
        logger.error(f"Error initializing Llama 3 8B LLM: {str(e)}")
        raise

# Define the state structure for the graph
class EmailProcessingState(TypedDict):
    """State structure for email processing workflow"""
    email_id: str
    sender_email: str
    sender_name: str
    subject: str
    body: str
    timestamp: str
    has_attachment: bool
    thread_id: str
    
    # Processing results
    category: Optional[str]
    priority: Optional[str]
    confidence_score: Optional[float]
    key_info: Optional[Dict[str, Any]]
    action_recommendation: Optional[str]
    draft_response: Optional[str]
    reasoning: Optional[str]
    processing_status: str  # 'pending', 'processing', 'completed', 'error'
    error_message: Optional[str]


class EmailClassifierAgent:
    """Agent responsible for categorizing emails"""
    
    def __init__(self):
        self.llm = get_llm()
        self.categories = EMAIL_CATEGORIES
        logger.info("Classifier Agent initialized")
    
    def classify_email(self, state: EmailProcessingState) -> Dict[str, Any]:
        """
        Classify email into categories
        Handles messy email content and None values
        
        Args:
            state: Current email processing state
        
        Returns:
            Updated state with category information
        """
        try:
            subject = str(state.get('subject') or 'No Subject').strip()
            body = str(state.get('body') or 'No content').strip()
            sender_name = str(state.get('sender_name') or 'Unknown').strip()
            sender_email = str(state.get('sender_email') or 'unknown@domain.com').strip()
            has_attachment = state.get('has_attachment', False)
            
            email_content = f"""
Subject: {subject[:200]}
Body: {body[:500]}
Sender: {sender_name} ({sender_email})
Has Attachment: {has_attachment}
"""
            
            system_prompt = f"""You are an expert email classifier. Analyze the email and categorize it into ONE of these categories:
{', '.join(self.categories)}

Consider:
- Email content and tone
- Sender information
- Subject line
- Keywords and context
- Business vs personal nature

Respond in JSON format with these fields:
{{
    "category": "selected_category",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=email_content)
            ]
            
            response = self.llm.invoke(messages)
            result = json.loads(response.content)
            
            category = result.get("category", "Personal")
            # Validate category
            if category not in self.categories:
                category = "Personal"
            
            logger.info(f"Classified email {state['email_id']}: {category}")
            
            return {
                "category": category,
                "confidence_score": float(result.get("confidence", 0.5)),
                "processing_status": "processing"
            }
        
        except Exception as e:
            logger.error(f"Classification error for email {state['email_id']}: {str(e)}")
            return {
                "category": "Personal",
                "confidence_score": 0.0,
                "processing_status": "processing",
                "error_message": str(e)
            }


class EmailPrioritizationAgent:
    """Agent responsible for prioritizing emails"""
    
    def __init__(self):
        self.llm = get_llm()
        self.priority_levels = list(PRIORITY_LEVELS.keys())
        logger.info("Prioritization Agent initialized")
    
    def prioritize_email(self, state: EmailProcessingState) -> Dict[str, Any]:
        """
        Assign priority level to email
        Handles messy email content and None values
        
        Args:
            state: Current email processing state
        
        Returns:
            Updated state with priority information
        """
        try:
            subject = str(state.get('subject') or 'No Subject').strip()
            body = str(state.get('body') or 'No content').strip()
            sender_name = str(state.get('sender_name') or 'Unknown').strip()
            category = str(state.get('category') or 'Unknown').strip()
            has_attachment = state.get('has_attachment', False)
            
            try:
                timestamp = state.get('timestamp', '')
                if timestamp and timestamp.endswith('Z'):
                    timestamp = timestamp[:-1]
                email_age = (datetime.now() - datetime.fromisoformat(timestamp)).days if timestamp else 0
            except:
                email_age = 0
            
            email_content = f"""
Subject: {subject[:200]}
Body: {body[:500]}
Sender: {sender_name}
Category: {category}
Has Attachment: {has_attachment}
Age: {email_age} days
"""
            
            system_prompt = f"""You are an expert email prioritization specialist. Analyze the email and assign ONE priority level:
{', '.join(self.priority_levels)}

Consider:
- Urgency indicators (URGENT, ASAP, etc.)
- Sender importance
- Email category
- Time sensitivity
- Business impact

Respond in JSON format with these fields:
{{
    "priority": "selected_priority",
    "score": 1-100,
    "reasoning": "brief explanation"
}}
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=email_content)
            ]
            
            response = self.llm.invoke(messages)
            result = json.loads(response.content)
            
            priority = result.get("priority", "Medium")
            # Validate priority
            if priority not in self.priority_levels:
                priority = "Medium"
            
            logger.info(f"Prioritized email {state['email_id']}: {priority}")
            
            return {
                "priority": priority,
                "processing_status": "processing"
            }
        
        except Exception as e:
            logger.error(f"Prioritization error for email {state['email_id']}: {str(e)}")
            return {
                "priority": "Medium",
                "processing_status": "processing",
                "error_message": str(e)
            }


class ResponseArchitectAgent:
    """Agent responsible for generating recommendations and draft responses"""
    
    def __init__(self):
        self.llm = get_llm()
        self.actions = RECOMMENDED_ACTIONS
        logger.info("Response Architect Agent initialized")
    
    def architect_response(self, state: EmailProcessingState) -> Dict[str, Any]:
        """
        Generate action recommendation and draft response
        Handles messy email content and None values
        
        Args:
            state: Current email processing state
        
        Returns:
            Updated state with recommendations and draft response
        """
        try:
            subject = str(state.get('subject') or 'No Subject').strip()
            body = str(state.get('body') or 'No content').strip()
            sender_name = str(state.get('sender_name') or 'Unknown').strip()
            sender_email = str(state.get('sender_email') or 'unknown@domain.com').strip()
            category = str(state.get('category') or 'Unknown').strip()
            priority = str(state.get('priority') or 'Medium').strip()
            has_attachment = state.get('has_attachment', False)
            
            email_content = f"""
Subject: {subject[:200]}
Body: {body[:500]}
Sender: {sender_name} ({sender_email})
Category: {category}
Priority: {priority}
Has Attachment: {has_attachment}
"""
            
            system_prompt = f"""You are an expert email response strategist. Analyze the email and provide:

1. Recommended Action (choose one): {', '.join(self.actions)}
2. Key Information Extracted (dates, names, action items, etc.)
3. Draft Response (if applicable, otherwise "N/A")
4. Reasoning for recommendation

Respond in JSON format with these fields:
{{
    "action": "recommended_action",
    "key_info": {{
        "dates": [],
        "names": [],
        "action_items": [],
        "other": ""
    }},
    "draft_response": "draft email response or N/A",
    "reasoning": "explanation of recommendation"
}}
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=email_content)
            ]
            
            response = self.llm.invoke(messages)
            result = json.loads(response.content)
            
            action = result.get("action", "Archive")
            # Validate action
            if action not in self.actions:
                action = "Archive"
            
            logger.info(f"Architected response for email {state['email_id']}: {action}")
            
            return {
                "action_recommendation": action,
                "key_info": result.get("key_info", {}),
                "draft_response": result.get("draft_response", "N/A"),
                "reasoning": result.get("reasoning", ""),
                "processing_status": "completed"
            }
        
        except Exception as e:
            logger.error(f"Response architecture error for email {state['email_id']}: {str(e)}")
            return {
                "action_recommendation": "Flag for Review",
                "key_info": {},
                "draft_response": "N/A",
                "reasoning": f"Error in processing: {str(e)}",
                "processing_status": "error",
                "error_message": str(e)
            }


def classifier_node(state: EmailProcessingState) -> Dict[str, Any]:
    """Graph node for classifier agent"""
    agent = EmailClassifierAgent()
    return agent.classify_email(state)


def prioritization_node(state: EmailProcessingState) -> Dict[str, Any]:
    """Graph node for prioritization agent"""
    agent = EmailPrioritizationAgent()
    return agent.prioritize_email(state)


def response_architect_node(state: EmailProcessingState) -> Dict[str, Any]:
    """Graph node for response architect agent"""
    agent = ResponseArchitectAgent()
    return agent.architect_response(state)


def build_email_processing_graph() -> StateGraph:
    """
    Build the LangGraph workflow for email processing
    
    Returns:
        Compiled StateGraph for email processing
    """
    graph = StateGraph(EmailProcessingState)
    
    # Add nodes
    graph.add_node("classify", classifier_node)
    graph.add_node("prioritize", prioritization_node)
    graph.add_node("architect", response_architect_node)
    
    # Define edges (workflow)
    graph.add_edge("classify", "prioritize")
    graph.add_edge("prioritize", "architect")
    graph.add_edge("architect", END)
    
    # Set entry point
    graph.set_entry_point("classify")
    
    logger.info("Email processing graph built successfully")
    return graph.compile()


class EmailProcessingOrchestrator:
    """Orchestrates the multi-agent email processing workflow"""
    
    def __init__(self):
        self.graph = build_email_processing_graph()
        logger.info("Email Processing Orchestrator initialized")
    
    def process_email(self, email_data: Dict[str, Any]) -> EmailProcessingState:
        """
        Process a single email through the multi-agent system
        
        Args:
            email_data: Email data dictionary
        
        Returns:
            Processed email state with all analysis
        """
        try:
            initial_state = EmailProcessingState(
                email_id=str(email_data.get('email_id', 'unknown')),
                sender_email=email_data.get('sender_email', ''),
                sender_name=email_data.get('sender_name', ''),
                subject=email_data.get('subject', ''),
                body=email_data.get('body', ''),
                timestamp=email_data.get('timestamp', ''),
                has_attachment=bool(email_data.get('has_attachment', False)),
                thread_id=str(email_data.get('thread_id', '')),
                category=None,
                priority=None,
                confidence_score=None,
                key_info=None,
                action_recommendation=None,
                draft_response=None,
                reasoning=None,
                processing_status="pending",
                error_message=None
            )
            
            result = self.graph.invoke(initial_state)
            logger.info(f"Email {email_data.get('email_id')} processed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error processing email {email_data.get('email_id')}: {str(e)}")
            return EmailProcessingState(
                **{k: v for k, v in email_data.items() if k in EmailProcessingState.__annotations__},
                processing_status="error",
                error_message=str(e)
            )
    
    def process_emails_batch(self, emails: List[Dict[str, Any]]) -> List[EmailProcessingState]:
        """
        Process multiple emails
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            List of processed email states
        """
        results = []
        for i, email in enumerate(emails):
            logger.info(f"Processing email {i+1}/{len(emails)}")
            result = self.process_email(email)
            results.append(result)
        
        logger.info(f"Batch processing complete: {len(results)} emails processed")
        return results
