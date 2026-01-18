"""
Utility functions for Email Inbox Organizer
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logger

logger = setup_logger(__name__)

def load_emails_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    Load emails from CSV file with proper handling of messy data.
    Uses data_loader from Data_clean folder for robust parsing.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        List of cleaned email dictionaries
    """
    try:
        # Import data_loader from Data_clean folder
        sys.path.insert(0, str(Path(__file__).parent.parent / "Data_clean"))
        from data_loader import clean_and_load_emails
        
        # Open file and pass to data loader
        with open(csv_path, 'rb') as f:
            emails = clean_and_load_emails(f)
        
        # Ensure all records are cleaned
        cleaned_emails = []
        for email in emails:
            cleaned = clean_email_record(email)
            if cleaned:
                cleaned_emails.append(cleaned)
        
        logger.info(f"Successfully loaded {len(cleaned_emails)} cleaned emails from {csv_path}")
        return cleaned_emails
    
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        return []


def clean_email_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Clean and normalize email record from CSV
    Handles messy data, escaped quotes, and newlines
    
    Args:
        record: Raw email record from CSV
    
    Returns:
        Cleaned email record or None if invalid
    """
    try:
        cleaned = {}
        
        # Email ID (required)
        email_id = str(record.get('email_id', '')).strip() if record.get('email_id') else ''
        if not email_id or email_id.lower() in ['email_id', 'nan']:
            return None
        cleaned['email_id'] = email_id
        
        # Sender Email (required)
        sender_email = str(record.get('sender_email', '')).strip().lower() if record.get('sender_email') else ''
        if not sender_email or '@' not in sender_email or sender_email.lower() == 'sender_email':
            logger.warning(f"Invalid sender_email for email {email_id}")
            sender_email = 'unknown@domain.com'
        cleaned['sender_email'] = sender_email
        
        # Sender Name (required)
        sender_name = str(record.get('sender_name', '')).strip() if record.get('sender_name') else ''
        if not sender_name or sender_name.lower() in ['sender_name', 'nan', 'none']:
            sender_name = 'Unknown Sender'
        cleaned['sender_name'] = sender_name
        
        # Subject (required)
        subject = str(record.get('subject', '')).strip() if record.get('subject') else ''
        if not subject or subject.lower() in ['subject', 'nan']:
            subject = 'No Subject'
        # Remove embedded quotes and newlines
        subject = subject.replace('\\n', ' ').replace('""', '"').strip()
        # Clean up escaped newlines and quotes
        subject = re.sub(r'\n+', ' ', subject)
        cleaned['subject'] = subject[:200]  # Limit to 200 chars
        
        # Body (required)
        body = str(record.get('body', '')).strip() if record.get('body') else ''
        if not body or body.lower() in ['body', 'nan']:
            body = 'No content'
        # Clean up body: remove escaped characters, normalize whitespace
        body = body.replace('\\n', '\n').replace('""', '"').strip()
        # Remove excessive whitespace and normalize newlines
        body = '\n'.join([line.strip() for line in body.split('\n') if line.strip()])
        cleaned['body'] = body
        
        # Timestamp (required)
        timestamp = str(record.get('timestamp', '')).strip() if record.get('timestamp') else ''
        if not timestamp or timestamp.lower() in ['timestamp', 'nan']:
            timestamp = datetime.utcnow().isoformat() + 'Z'
        cleaned['timestamp'] = timestamp
        
        # Has Attachment (boolean)
        has_attachment_str = str(record.get('has_attachment', 'FALSE')).strip().upper() if record.get('has_attachment') else 'FALSE'
        cleaned['has_attachment'] = has_attachment_str in ['TRUE', 'YES', '1', 'T']
        
        # Thread ID (required)
        thread_id = str(record.get('thread_id', '')).strip() if record.get('thread_id') else ''
        if not thread_id or thread_id.lower() in ['thread_id', 'nan']:
            thread_id = f"thread_{email_id}"
        cleaned['thread_id'] = thread_id
        
        return cleaned
        
    except Exception as e:
        logger.warning(f"Error in clean_email_record: {str(e)}")
        return None

def format_timestamp(timestamp_str: str) -> str:
    """
    Format ISO timestamp to readable format
    Handles various timestamp formats and None values
    
    Args:
        timestamp_str: ISO format timestamp or string
    
    Returns:
        Formatted timestamp string
    """
    try:
        if not timestamp_str or timestamp_str is None:
            return "Unknown Date"
            
        timestamp_str = str(timestamp_str).strip()
        
        # Try ISO format with Z suffix
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1]
        
        # Try different datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            dt = datetime.fromisoformat(timestamp_str)
            
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception as e:
        logger.warning(f"Error formatting timestamp: {str(e)}")
        return "Unknown Date"

def extract_domain(email_address: str) -> str:
    """
    Extract domain from email address
    
    Args:
        email_address: Email address
    
    Returns:
        Domain name
    """
    try:
        return email_address.split('@')[1] if '@' in email_address else "Unknown"
    except Exception as e:
        logger.warning(f"Error extracting domain: {str(e)}")
        return "Unknown"

def get_sender_initials(sender_name: str) -> str:
    """
    Get initials from sender name
    
    Args:
        sender_name: Full name of sender
    
    Returns:
        Initials (uppercase)
    """
    try:
        if not sender_name or sender_name is None:
            return "??"
        words = sender_name.strip().split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[-1][0]}".upper()
        elif len(words) == 1:
            return words[0][0].upper()
        else:
            return "??"
    except Exception as e:
        logger.warning(f"Error getting initials: {str(e)}")
        return "??"

def get_email_preview(body: Optional[str], max_length: int = 100) -> str:
    """
    Get preview text from email body
    Handles None values and messy formatting
    
    Args:
        body: Email body text (can be None)
        max_length: Maximum preview length
    
    Returns:
        Preview text
    """
    try:
        if not body or body is None:
            return "No content"
        body = str(body).strip()
        # Remove extra whitespace and newlines
        preview = ' '.join(body.split())
        # Truncate and add ellipsis if needed
        if len(preview) > max_length:
            preview = preview[:max_length] + "..."
        return preview
    except Exception as e:
        logger.warning(f"Error getting email preview: {str(e)}")
        return "No content"

def calculate_age_in_days(timestamp_str: str) -> int:
    """
    Calculate age of email in days
    
    Args:
        timestamp_str: ISO format timestamp
    
    Returns:
        Age in days
    """
    try:
        email_date = datetime.fromisoformat(timestamp_str)
        age = (datetime.now() - email_date).days
        return max(0, age)
    except Exception as e:
        logger.warning(f"Error calculating age: {str(e)}")
        return 0

def filter_emails(emails: List[Dict[str, Any]], 
                  category: str = None, 
                  priority: str = None,
                  search_query: str = None) -> List[Dict[str, Any]]:
    """
    Filter emails based on criteria
    
    Args:
        emails: List of email dictionaries
        category: Category filter
        priority: Priority filter
        search_query: Search query for subject/body
    
    Returns:
        Filtered list of emails
    """
    filtered = emails
    
    if category and category != "All":
        filtered = [e for e in filtered if e.get('category') == category]
    
    if priority and priority != "All":
        filtered = [e for e in filtered if e.get('priority') == priority]
    
    if search_query and search_query.strip():
        query = search_query.lower()
        filtered = [e for e in filtered if 
                   query in e.get('subject', '').lower() or 
                   query in e.get('body', '').lower() or
                   query in e.get('sender_name', '').lower()]
    
    return filtered

def get_priority_color(priority: str) -> str:
    """
    Get color for priority level
    
    Args:
        priority: Priority level
    
    Returns:
        Color code
    """
    priority_colors = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢"
    }
    return priority_colors.get(priority, "⚪")

def get_category_emoji(category: str) -> str:
    """
    Get emoji for category
    
    Args:
        category: Email category
    
    Returns:
        Emoji character
    """
    category_emojis = {
        "Work": "💼",
        "Personal": "👤",
        "Urgent": "⚡",
        "Newsletter": "📬",
        "Spam": "🚫",
        "Financial": "💰",
        "Meeting": "📅",
        "Social": "👥"
    }
    return category_emojis.get(category, "📧")
