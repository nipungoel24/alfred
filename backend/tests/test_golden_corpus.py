import json
import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas import Email, EmailAnalysis, ActionItem
from app.services.task_derivation import derive_tasks

def test_golden_corpus():
    corpus_path = Path(__file__).parent.parent / "benchmarks" / "golden_emails.json"
    with open(corpus_path, "r") as f:
        corpus = json.load(f)

    for item in corpus:
        email = Email(
            id=item["id"],
            subject=item["subject"],
            sender=item["sender"],
            body=item["body"],
            received_at="2026-08-16T10:00:00Z"
        )
        
        # We simulate the LLM naively identifying an action item from the text
        # so that our derivation logic is tested to see if it filters it out
        # if it's noise, third-party, etc.
        
        # If it's a legit task, LLM finds it:
        if item["id"] == "email_legit_task":
            analysis = EmailAnalysis(
                short_summary="Report needed",
                category="work",
                priority="high",
                priority_score=80,
                reason_for_priority="boss",
                needs_reply=False,
                action_items=[ActionItem(description="Send Q3 report by Friday")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        elif item["id"] == "email_third_party":
            analysis = EmailAnalysis(
                short_summary="Ticket update",
                category="notification",
                priority="low",
                priority_score=10,
                reason_for_priority="ticket",
                needs_reply=False,
                action_items=[ActionItem(description="Update the server configurations tomorrow", owner="John")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        elif item["id"] == "email_marketing":
            analysis = EmailAnalysis(
                short_summary="Shoe sale",
                category="promotion",
                priority="low",
                priority_score=10,
                reason_for_priority="sale",
                needs_reply=False,
                action_items=[ActionItem(description="Buy now and save 50%"), ActionItem(description="Complete your purchase today")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        elif item["id"] == "email_base64":
            analysis = EmailAnalysis(
                short_summary="Alert",
                category="notification",
                priority="low",
                priority_score=10,
                reason_for_priority="log",
                needs_reply=False,
                action_items=[ActionItem(description="Decode the base64 string to see full details.")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        elif item["id"] == "email_password_reset":
            analysis = EmailAnalysis(
                short_summary="Reset",
                category="security",
                priority="high",
                priority_score=80,
                reason_for_priority="security",
                needs_reply=False,
                action_items=[ActionItem(description="Check if the user has a pending password reset request."), ActionItem(description="Verify your account credentials.")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        elif item["id"] == "email_tiktok":
            analysis = EmailAnalysis(
                short_summary="Login",
                category="security",
                priority="high",
                priority_score=80,
                reason_for_priority="security",
                needs_reply=False,
                action_items=[ActionItem(description="Verify the user's TikTok account credentials to continue.")],
                deadlines=[],
                important_entities=[],
                important_details=[]
            )
        else:
            continue
            
        tasks = derive_tasks(email, analysis)
        assert len(tasks) == item["expected_tasks"], f"Failed on {item['id']}: expected {item['expected_tasks']} tasks, got {len(tasks)}"
