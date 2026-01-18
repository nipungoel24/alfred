# Email Inbox Organizer Package
from src.email_processor import EmailProcessor, get_email_processor
from src.agents import EmailProcessingOrchestrator

__version__ = "1.0.0"
__all__ = ["EmailProcessor", "get_email_processor", "EmailProcessingOrchestrator"]
