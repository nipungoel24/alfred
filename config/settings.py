"""
Configuration settings for Email Inbox Organizer
"""
import os
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(BASE_DIR := Path(__file__).parent.parent / ".env")

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
SRC_DIR = BASE_DIR / "src"

# API Configuration - Groq LLaMA Primary Provider
# Llama 3 8B Configuration (ONLY LLM USED)
# Using llama-3.1-8b-instant: Fast and efficient model via Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"  # Llama 3 8B model

# Set active model name to Llama 3 8B
MODEL_NAME = "llama-3.1-8b-instant"
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# LangGraph Configuration
AGENT_TIMEOUT = 30  # seconds
MAX_ITERATIONS = 10

# Email Categories
EMAIL_CATEGORIES = [
    "Work",
    "Personal",
    "Urgent",
    "Newsletter",
    "Spam",
    "Financial",
    "Meeting",
    "Social"
]

# Priority Levels
PRIORITY_LEVELS = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4
}

# Recommended Actions
RECOMMENDED_ACTIONS = [
    "Reply",
    "Schedule Meeting",
    "Archive",
    "Mark as Spam",
    "Forward",
    "Flag for Review",
    "Delete",
    "Add to Calendar"
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "email_organizer.log"

# CSV Dataset Configuration
CSV_FILE_PATH = DATA_DIR / "dataset_emails - Sheet1.csv"
REQUIRED_CSV_COLUMNS = [
    "email_id",
    "sender_email",
    "sender_name",
    "subject",
    "body",
    "timestamp",
    "has_attachment",
    "thread_id"
]

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Email Inbox Organizer"
STREAMLIT_PAGE_ICON = "📧"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_INITIAL_SIDEBAR_STATE = "expanded"

# Pagination
EMAILS_PER_PAGE = 10

# Agent Roles
AGENTS = {
    "classifier": {
        "name": "Classifier Agent",
        "role": "Categorize emails into predefined categories",
        "description": "Analyzes email content to determine appropriate category"
    },
    "prioritizer": {
        "name": "Prioritization Agent",
        "role": "Assign priority levels based on urgency and importance",
        "description": "Evaluates email importance and assigns priority scores"
    },
    "response_architect": {
        "name": "Response Architect",
        "role": "Generate appropriate responses and action recommendations",
        "description": "Creates draft responses and suggests optimal actions"
    }
}

# Keyword mappings for category detection
CATEGORY_KEYWORDS = {
    "Work": ["meeting", "project", "deadline", "deliverable", "review", "approve", "budget", "report"],
    "Urgent": ["urgent", "asap", "immediate", "emergency", "critical", "down", "broken"],
    "Newsletter": ["newsletter", "digest", "weekly", "monthly", "subscription", "unsubscribe"],
    "Spam": ["congratulations", "winner", "claim", "limited time", "act now", "click here"],
    "Personal": ["friend", "family", "personal", "hi", "hey", "catch up", "weekend"],
    "Financial": ["invoice", "payment", "billing", "expense", "purchase", "order", "refund"],
    "Meeting": ["meeting", "call", "sync", "standup", "conference", "availability"],
    "Social": ["like", "follow", "comment", "share", "post", "notification"]
}

# Priority scoring rules
PRIORITY_RULES = {
    "urgent_keywords": ["urgent", "asap", "immediate", "emergency", "critical"],
    "high_importance_senders": ["boss", "ceo", "cto", "manager", "director"],
    "low_importance_patterns": ["newsletter", "marketing", "promo", "discount"]
}
