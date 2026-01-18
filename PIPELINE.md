# Email Inbox Organizer - Data Pipeline

## Overview
The complete data pipeline for processing emails from messy CSV files to intelligent AI-powered insights.

---

## Pipeline Architecture

### Stage 1: Data Loading & Cleaning
**File:** `Data_clean/data_loader.py`

- Loads messy CSV files with double-quoted format and escaped characters
- Parses complex multiline email bodies
- Cleans and validates all fields
- Returns cleaned email dictionaries

**Input:** Raw CSV file from `data/dataset_emails - Sheet1.csv`
**Output:** List of cleaned email dictionaries with 8 fields:
- `email_id`: Unique identifier
- `sender_email`: Sender email address
- `sender_name`: Sender display name
- `subject`: Email subject line
- `body`: Email body content
- `timestamp`: ISO format timestamp
- `has_attachment`: Boolean flag
- `thread_id`: Thread identifier

### Stage 2: Data Validation & Normalization
**File:** `src/utils.py` → `clean_email_record()`

- Validates all required fields are present
- Normalizes data types (boolean, strings)
- Handles missing/None values with sensible defaults
- Removes escaped quotes and newlines
- Truncates long fields to reasonable lengths

**Output:** Validated and normalized email records

### Stage 3: AI Processing - Multi-Agent System
**File:** `src/agents.py`

Uses **Google Gemini Flash 1.5** (ONLY LLM USED) through a 3-agent workflow:

#### Agent 1: Classifier Agent
- **Role:** Categorizes emails
- **Categories:** Work, Personal, Urgent, Newsletter, Spam, Financial, Meeting, Social
- **Output:** 
  - `category`: Selected category
  - `confidence_score`: Confidence level (0-1)

#### Agent 2: Prioritization Agent
- **Role:** Assigns priority levels
- **Priority Levels:** Critical, High, Medium, Low
- **Considers:** Urgency indicators, sender importance, category, time sensitivity
- **Output:**
  - `priority`: Priority level
  - `reasoning`: Explanation for priority

#### Agent 3: Response Architect Agent
- **Role:** Extracts key information and generates recommendations
- **Actions:** Reply, Schedule Meeting, Archive, Mark as Spam, Forward, Flag for Review, Delete, Add to Calendar
- **Output:**
  - `action_recommendation`: Suggested action
  - `key_info`: Extracted dates, names, action items
  - `draft_response`: Draft email response (if applicable)
  - `reasoning`: Explanation for recommendation

### Stage 4: Data Organization & Display
**File:** `src/app.py` (Streamlit Frontend)

#### Features:
1. **Dashboard Metrics**
   - Total emails count
   - Urgent emails count
   - Emails with attachments
   - Processing errors

2. **Email Filtering**
   - Filter by category
   - Filter by priority
   - Filter by sender
   - Filter by date range
   - Has attachment filter

3. **Search Functionality**
   - Search in subject, body, sender name
   - Real-time search results

4. **Email Display**
   - Email list with sender avatars
   - Priority color coding
   - Category emoji indicators
   - Timestamp formatting

5. **Detailed View**
   - Full email content
   - AI analysis (category, priority, confidence)
   - Extracted key information
   - Action recommendation with reasoning
   - Draft response with copy/send options

6. **Email Statistics**
   - Category breakdown (bar chart)
   - Priority distribution (bar chart)
   - Action recommendations summary

---

## Data Flow Diagram

```
┌─────────────────────────────────┐
│  CSV File (Messy Data)          │
│  data/dataset_emails...csv      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  STAGE 1: Data Loading          │
│  Data_clean/data_loader.py      │
│  - Parse double-quoted format   │
│  - Handle multiline bodies      │
│  - Extract 8 fields             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  STAGE 2: Data Validation       │
│  src/utils.py::clean_record()   │
│  - Validate required fields     │
│  - Normalize types              │
│  - Handle None values           │
│  - Clean escaped chars          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  STAGE 3: AI Processing         │
│  src/agents.py (LangGraph)      │
│                                 │
│  Agent 1: Classifier            │
│  ├─ Categorize email            │
│  └─ Output: category, confidence│
│                                 │
│  Agent 2: Prioritizer           │
│  ├─ Assign priority             │
│  └─ Output: priority, reasoning │
│                                 │
│  Agent 3: Response Architect    │
│  ├─ Extract key info            │
│  ├─ Generate action rec.        │
│  ├─ Draft response              │
│  └─ Output: action, info, draft │
│                                 │
│  LLM: Google Gemini Flash 1.5   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  STAGE 4: Data Organization     │
│  src/email_processor.py         │
│  - Cache results                │
│  - Compile final output         │
│  - Prepare for display          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  STAGE 5: Display (Frontend)    │
│  src/app.py (Streamlit)         │
│                                 │
│  ✓ Dashboard metrics            │
│  ✓ Filterable email list        │
│  ✓ Search functionality         │
│  ✓ Category & priority display  │
│  ✓ Action suggestions           │
│  ✓ Draft responses              │
│  ✓ Key information display      │
│  ✓ Statistics & charts          │
└─────────────────────────────────┘
```

---

## API Keys & Configuration

### Required Environment Variables
Add to `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

### Settings (config/settings.py)
- `GEMINI_MODEL = "gemini-1.5-flash"` ← ONLY LLM USED
- `TEMPERATURE = 0.7` ← Creativity level
- `MAX_TOKENS = 2000` ← Response length limit
- `EMAIL_CATEGORIES` ← Predefined categories
- `PRIORITY_LEVELS` ← Priority thresholds
- `RECOMMENDED_ACTIONS` ← Action suggestions

---

## Key Processing Functions

### Data Loading
```python
# Load and clean CSV
from src.utils import load_emails_from_csv
emails = load_emails_from_csv("data/dataset_emails - Sheet1.csv")
```

### Email Processing
```python
# Process emails through AI system
from src.email_processor import get_email_processor
processor = get_email_processor()
processed = processor.load_and_process_csv()
```

### Filtering & Search
```python
# Filter emails
from src.utils import filter_emails
filtered = filter_emails(
    emails,
    category="Work",
    priority="High",
    search_query="meeting"
)
```

---

## Cache System

- **Location:** `cache/` directory
- **Format:** JSON files
- **Key:** MD5 hash of email_id
- **Benefit:** Fast reprocessing of same emails
- **Auto-save:** Results saved after processing

---

## Error Handling

1. **CSV Loading Errors** → Returns empty list, logs error
2. **Validation Errors** → Records marked with default values
3. **LLM Errors** → Email marked for manual review
4. **Caching Errors** → Continues without cache

---

## Performance Metrics

- **CSV Loading:** ~200ms for 100 emails
- **AI Processing:** ~5-10s per email (LLM dependent)
- **Caching Speedup:** ~10-50x for cached emails
- **Display Rendering:** ~1s for 100 emails

---

## Future Enhancements

- [ ] Batch processing with progress bar
- [ ] Email reply drafting
- [ ] Calendar integration
- [ ] Custom category management
- [ ] Advanced analytics dashboard
- [ ] Email template suggestions
- [ ] Multi-language support
