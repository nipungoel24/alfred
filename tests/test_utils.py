"""
Unit tests for Email Inbox Organizer
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    get_sender_initials, get_email_preview, format_timestamp,
    get_priority_color, get_category_emoji, extract_domain
)
from config.settings import EMAIL_CATEGORIES, PRIORITY_LEVELS


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_get_sender_initials(self):
        """Test initials extraction"""
        assert get_sender_initials("John Smith") == "JS"
        assert get_sender_initials("Sarah Wilson") == "SW"
        assert get_sender_initials("Alice") == "A"
        assert get_sender_initials("") == "??"
    
    def test_get_email_preview(self):
        """Test email preview truncation"""
        long_text = "A" * 150
        preview = get_email_preview(long_text, max_length=100)
        assert len(preview) <= 103  # 100 + "..."
        assert preview.endswith("...")
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        timestamp = "2025-01-10T10:30:00"
        formatted = format_timestamp(timestamp)
        assert "2025" in formatted or "January" in formatted
    
    def test_extract_domain(self):
        """Test email domain extraction"""
        assert extract_domain("user@example.com") == "example.com"
        assert extract_domain("test@company.org") == "company.org"
        assert extract_domain("invalid_email") == "Unknown"
    
    def test_get_priority_color(self):
        """Test priority color emoji"""
        assert get_priority_color("Critical") == "🔴"
        assert get_priority_color("High") == "🟠"
        assert get_priority_color("Medium") == "🟡"
        assert get_priority_color("Low") == "🟢"
    
    def test_get_category_emoji(self):
        """Test category emoji"""
        assert get_category_emoji("Work") == "💼"
        assert get_category_emoji("Personal") == "👤"
        assert get_category_emoji("Urgent") == "⚡"
        assert get_category_emoji("Spam") == "🚫"


class TestConfiguration:
    """Test configuration settings"""
    
    def test_email_categories_exist(self):
        """Test email categories are defined"""
        assert len(EMAIL_CATEGORIES) > 0
        assert "Work" in EMAIL_CATEGORIES
        assert "Spam" in EMAIL_CATEGORIES
    
    def test_priority_levels_exist(self):
        """Test priority levels are defined"""
        assert len(PRIORITY_LEVELS) > 0
        assert "Critical" in PRIORITY_LEVELS
        assert "Low" in PRIORITY_LEVELS
    
    def test_priority_levels_order(self):
        """Test priority levels have correct numeric order"""
        assert PRIORITY_LEVELS["Critical"] < PRIORITY_LEVELS["High"]
        assert PRIORITY_LEVELS["High"] < PRIORITY_LEVELS["Medium"]
        assert PRIORITY_LEVELS["Medium"] < PRIORITY_LEVELS["Low"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
