"""
Email Processor - Manages email loading, processing, and caching
"""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from datetime import datetime
import hashlib
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logger
from src.agents import EmailProcessingOrchestrator, EmailProcessingState
from src.utils import load_emails_from_csv
from config.settings import CSV_FILE_PATH

logger = setup_logger(__name__)


class EmailProcessor:
    """Manages email processing pipeline with caching"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize email processor
        
        Args:
            cache_dir: Directory for caching processed results
        """
        self.orchestrator = EmailProcessingOrchestrator()
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.processed_emails: Dict[str, Dict[str, Any]] = {}
        logger.info("Email Processor initialized")
    
    def _get_cache_key(self, email_id: str) -> str:
        """Generate cache key for email"""
        return hashlib.md5(f"email_{email_id}".encode()).hexdigest()
    
    def _get_cache_file(self, email_id: str) -> Path:
        """Get cache file path for email"""
        return self.cache_dir / f"{self._get_cache_key(email_id)}.json"
    
    def _load_from_cache(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Load processed email from cache
        
        Args:
            email_id: Email ID
        
        Returns:
            Cached result or None
        """
        cache_file = self._get_cache_file(email_id)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache for {email_id}: {str(e)}")
                return None
        return None
    
    def _save_to_cache(self, email_id: str, data: Dict[str, Any]) -> None:
        """
        Save processed email to cache
        
        Args:
            email_id: Email ID
            data: Processed data
        """
        try:
            cache_file = self._get_cache_file(email_id)
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error writing cache for {email_id}: {str(e)}")
    
    def _state_to_dict(self, state: EmailProcessingState) -> Dict[str, Any]:
        """Convert EmailProcessingState to dictionary"""
        return {
            "email_id": state.get("email_id"),
            "sender_email": state.get("sender_email"),
            "sender_name": state.get("sender_name"),
            "subject": state.get("subject"),
            "body": state.get("body"),
            "timestamp": state.get("timestamp"),
            "has_attachment": state.get("has_attachment"),
            "thread_id": state.get("thread_id"),
            "category": state.get("category"),
            "priority": state.get("priority"),
            "confidence_score": state.get("confidence_score"),
            "key_info": state.get("key_info"),
            "action_recommendation": state.get("action_recommendation"),
            "draft_response": state.get("draft_response"),
            "reasoning": state.get("reasoning"),
            "processing_status": state.get("processing_status"),
            "error_message": state.get("error_message")
        }
    
    def process_email(self, email_data: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        Process a single email with validation
        
        Args:
            email_data: Email data dictionary
            use_cache: Whether to use cached results
        
        Returns:
            Processed email dictionary
        """
        # Validate email_data
        if not email_data or not isinstance(email_data, dict):
            logger.warning("Invalid email_data provided")
            return {
                "email_id": "unknown",
                "processing_status": "error",
                "error_message": "Invalid email data"
            }
        
        email_id = str(email_data.get('email_id', 'unknown'))
        
        # Skip header rows
        if email_id.lower() == 'email_id':
            return None
        
        # Check cache
        if use_cache:
            cached_result = self._load_from_cache(email_id)
            if cached_result:
                logger.info(f"Using cached result for email {email_id}")
                return cached_result
        
        # Validate required fields
        required_fields = ['sender_email', 'sender_name', 'subject', 'body']
        for field in required_fields:
            if field not in email_data or not email_data.get(field):
                logger.warning(f"Missing required field '{field}' for email {email_id}")
                email_data[field] = 'Unknown' if field != 'body' else 'No content'
        
        # Process email
        logger.info(f"Processing email {email_id}")
        state = self.orchestrator.process_email(email_data)
        result = self._state_to_dict(state)
        
        # Cache result
        self._save_to_cache(email_id, result)
        
        self.processed_emails[email_id] = result
        return result
    
    def process_emails_batch(self, emails: List[Dict[str, Any]], 
                           use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple emails with filtering
        
        Args:
            emails: List of email dictionaries
            use_cache: Whether to use cached results
        
        Returns:
            List of processed email dictionaries (None entries filtered out)
        """
        results = []
        for i, email in enumerate(emails):
            if email is None:
                continue
                
            try:
                result = self.process_email(email, use_cache=use_cache)
                if result is not None:
                    results.append(result)
                logger.info(f"Processed {i+1}/{len(emails)} emails")
            except Exception as e:
                logger.error(f"Error processing email {email.get('email_id') if email else 'unknown'}: {str(e)}")
                if email:
                    error_result = {
                        **email,
                        "processing_status": "error",
                        "error_message": str(e)
                    }
                    results.append(error_result)
        
        # Filter out None results
        return [r for r in results if r is not None]
    
    def load_and_process_csv(self, csv_path: Optional[str] = None, 
                            use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load emails from CSV and process them.
        Uses data_loader.py from Data_clean folder for robust CSV parsing.
        
        Pipeline:
        1. Load and clean CSV using data_loader.py
        2. Process through multi-agent AI system (Google Gemini 2.0 Flash)
        3. Return with categories, priorities, recommendations, draft responses
        
        Args:
            csv_path: Path to CSV file (uses default if not provided)
            use_cache: Whether to use cached results
        
        Returns:
            List of processed emails with complete AI analysis
        """
        csv_path = csv_path or str(CSV_FILE_PATH)
        logger.info(f"[STEP 1] Loading CSV from {csv_path} using data_loader.py...")
        
        try:
            # Step 1: Load and clean CSV using data_loader.py
            emails = load_emails_from_csv(csv_path)
            logger.info(f"[STEP 1] Complete: Loaded and cleaned {len(emails)} emails")
            
            # Step 2: Process emails through multi-agent system
            logger.info(f"[STEP 2] Processing emails through AI agents (Google Gemini 2.0 Flash):")
            logger.info(f"         - Classifier Agent (categorization)")
            logger.info(f"         - Prioritization Agent (priority assignment)")
            logger.info(f"         - Response Architect (recommendations & draft responses)")
            processed_emails = self.process_emails_batch(emails, use_cache=use_cache)
            logger.info(f"[STEP 2] Complete: Processed {len(processed_emails)} emails successfully")
            
            # Step 3: Return processed emails with all AI analysis
            logger.info(f"[STEP 3] Returning {len(processed_emails)} emails with:")
            logger.info(f"         - Email categories (Work, Personal, Urgent, etc.)")
            logger.info(f"         - Priority levels (Critical, High, Medium, Low)")
            logger.info(f"         - Key information extraction (dates, names, action items)")
            logger.info(f"         - Action recommendations (Reply, Schedule, Archive, etc.)")
            logger.info(f"         - Draft responses for applicable emails")
            return processed_emails
        
        except Exception as e:
            logger.error(f"Error in data pipeline: {str(e)}")
            raise
    
    def get_statistics(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics from processed emails
        
        Args:
            emails: List of processed emails
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = {
                "total_emails": len(emails),
                "categories": {},
                "priorities": {},
                "actions": {},
                "has_attachments": 0,
                "errors": 0
            }
            
            for email in emails:
                # Category stats
                category = email.get('category', 'Unknown')
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                # Priority stats
                priority = email.get('priority', 'Unknown')
                stats['priorities'][priority] = stats['priorities'].get(priority, 0) + 1
                
                # Action stats
                action = email.get('action_recommendation', 'Unknown')
                stats['actions'][action] = stats['actions'].get(action, 0) + 1
                
                # Attachments
                if email.get('has_attachment', False):
                    stats['has_attachments'] += 1
                
                # Errors
                if email.get('processing_status') == 'error':
                    stats['errors'] += 1
            
            return stats
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {"error": str(e)}
    
    def get_urgent_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get urgent emails
        
        Args:
            emails: List of processed emails
        
        Returns:
            List of urgent emails
        """
        return [e for e in emails if e.get('priority') in ['Critical', 'High']]
    
    def get_emails_by_category(self, emails: List[Dict[str, Any]], 
                              category: str) -> List[Dict[str, Any]]:
        """
        Get emails by category
        
        Args:
            emails: List of processed emails
            category: Category filter
        
        Returns:
            Filtered list of emails
        """
        return [e for e in emails if e.get('category') == category]
    
    def get_emails_by_sender(self, emails: List[Dict[str, Any]], 
                            sender_name: str) -> List[Dict[str, Any]]:
        """
        Get emails by sender
        
        Args:
            emails: List of processed emails
            sender_name: Sender name to filter
        
        Returns:
            Filtered list of emails
        """
        return [e for e in emails if sender_name.lower() in e.get('sender_name', '').lower()]
    
    def search_emails(self, emails: List[Dict[str, Any]], 
                     query: str) -> List[Dict[str, Any]]:
        """
        Search emails by subject, body, or sender
        
        Args:
            emails: List of processed emails
            query: Search query
        
        Returns:
            Filtered list of emails
        """
        query_lower = query.lower()
        return [e for e in emails if 
               query_lower in e.get('subject', '').lower() or
               query_lower in e.get('body', '').lower() or
               query_lower in e.get('sender_name', '').lower()]


# Singleton instance
_processor_instance: Optional[EmailProcessor] = None


def get_email_processor() -> EmailProcessor:
    """Get or create email processor singleton"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = EmailProcessor()
    return _processor_instance
