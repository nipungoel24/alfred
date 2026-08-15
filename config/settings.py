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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Set active model name
MODEL_NAME = "llama-3.1-8b-instant"
TEMPERATURE = 0.6  # Slightly lowered to reduce hallucination/randomness
MAX_TOKENS = 2000

# LangGraph Configuration
AGENT_TIMEOUT = 30
MAX_ITERATIONS = 10

# Email Categories
# REMOVED: "Urgent" (Handled by Priority now)
# ADDED: "General" (Fallback for uncategorized emails)
EMAIL_CATEGORIES = [
    "Work",
    "Personal",
    "Newsletter",
    "Spam",
    "Financial",
    "Meeting",
    "Social",
    "General" 
]

# Priority Levels
# REMOVED: "Critical" to align with Agent outputs
PRIORITY_LEVELS = {
    "High": 1,
    "Medium": 2,
    "Low": 3
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
    "Add to Calendar",
    "Read & Archive"
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

# Streamlit Configuration (Updated to match app.py branding)
STREAMLIT_PAGE_TITLE = "Alfred | Intelligent Inbox"
STREAMLIT_PAGE_ICON = "🕴️"
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

# Expanded Keyword mappings for better categorization accuracy
CATEGORY_KEYWORDS = {
    "Work": [
        "meeting", "project", "deadline", "deliverable", "review", "approve", 
        "budget", "report", "presentation", "deck", "sync", "status", "update",
        "quarterly", "roadmap", "client", "contract", "proposal"
    ],
    "Newsletter": [
        "newsletter", "digest", "weekly", "monthly", "subscription", "unsubscribe", 
        "edition", "trends", "insights", "top stories", "curated", "webinar", "reader"
    ],
    "Spam": [
        "congratulations", "winner", "claim", "limited time", "act now", "click here",
        "lottery", "inheritance", "viagra", "casino", "verify your account", "urgent assistance"
    ],
    "Personal": [
        "friend", "family", "personal", "hi", "hey", "catch up", "weekend", 
        "dinner", "lunch", "party", "love", "mom", "dad", "vacation", "trip"
    ],
    "Financial": [
        "invoice", "payment", "billing", "expense", "purchase", "order", "refund",
        "receipt", "transaction", "bank", "statement", "credit card", "salary"
    ],
    "Meeting": [
        "meeting", "call", "sync", "standup", "conference", "availability", 
        "schedule", "calendar", "invite", "zoom", "teams", "google meet"
    ],
    "Social": [
        "like", "follow", "comment", "share", "post", "notification", 
        "linkedin", "facebook", "twitter", "instagram", "friend request"
    ],
    "General": [
        "info", "enquiry", "question", "feedback", "contact"
    ]
}

# Enhanced Priority Rules
PRIORITY_RULES = {
    "high_indicators": [
        "urgent", "asap", "immediate", "emergency", "critical", "deadline", 
        "overdue", "important", "action required", "server down", "breach"
    ],
    "high_importance_roles": [
        "boss", "ceo", "cto", "manager", "director", "vp", "head of", "founder"
    ],
    "low_importance_patterns": [
        "newsletter", "marketing", "promo", "discount", "digest", "unsubscribe", "no-reply"
    ]
}