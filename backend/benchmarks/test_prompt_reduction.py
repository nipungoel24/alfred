import sys; sys.path.insert(0, '.')
import asyncio
from app.ai.service import _prepare_body

test_cases = [
    {"name": "plain text", "body": "Hello, how are you?"},
    {"name": "base64 junk", "body": "Some text\n" + "A" * 300 + "=\nMore text"},
    {"name": "tracking url", "body": "Click here: http://track.example.com/click?" + "a"*150 + "\nThanks!"}
]

def get_tokens(text):
    return len(text)

for tc in test_cases:
    body = tc["body"]
    before = get_tokens(body)
    after = get_tokens(_prepare_body(body))
    print(f"{tc['name']}: before={before}, after={after}")
