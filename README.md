<div align="center">

# 🤵 ALFRED
### The Intelligent Inbox Protocol

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange?style=for-the-badge)
![Llama 3](https://img.shields.io/badge/AI-Llama%203%20(Groq)-purple?style=for-the-badge)

<p align="center">
  <b>"I shall endeavor to filter the noise, sir."</b><br>
  An agentic AI system designed to triage, prioritize, and manage high-volume inboxes with the discretion and efficiency of a world-class executive assistant.
</p>

</div>

---

## 📑 Assignment Compliance Matrix

This project was built specifically to address the **Email Inbox Organizer** assignment. Below is a mapping of requirements to the implemented solution.

| Category | Requirement | Alfred Implementation Status |
| :--- | :--- | :--- |
| **Email Organization** | Categorize & Prioritize | ✅ **Router Agent** classifies emails (Work, Personal, Spam) and assigns priority (High, Medium, Low). |
| | Extract Key Info | ✅ **Analyzer Agent** extracts entities (dates, names, amounts) into a dedicated "Key Entities" panel. |
| **Action & Reason** | Suggest Actions | ✅ **Decision Engine** recommends next steps (Reply, Archive, Meeting) with explicit reasoning. |
| | Generate Drafts | ✅ **Response Architect** generates context-aware draft replies automatically. |
| **User Interface** | Organized View | ✅ **3-Pane Gmail-Style Layout** (Sidebar, Scrollable List, Reading Pane) implemented in Streamlit. |
| | Filtering & Search | ✅ Sidebar includes **Multi-select Category/Priority filters** and global search. |
| **Architecture** | Agentic Framework | ✅ Built on **LangGraph**, orchestrating a stateful workflow between specialized agents. |
| | Specialized Agents | ✅ Three distinct agents: **Router** (Triage), **Analyzer** (Entity Extraction), **Writer** (Drafting). |

---

## 🏗️ System Architecture

Alfred utilizes a **Multi-Agent Pattern** orchestrated by LangGraph. Instead of a single LLM call, the process is broken down into specialized nodes that pass a shared state.

### The Agentic Workflow
1.  **📥 Ingestion:** Raw CSV data is loaded and cleaned.
2.  **🚦 Triage Node (The Router):**
    * Analyzes the subject and sender.
    * Determines **Category** (Work, Personal, Newsletter, etc.).
    * Assigns **Priority** based on urgency keywords.
3.  **🧠 Analysis Node (The Brain):**
    * Reads the full email body.
    * Extracts **Key Entities** (Deadlines, monetary values, specific requests).
    * Formulates a **Reasoning** chain for why an email is important.
    * Decides the **Recommended Action**.
4.  **✍️ Drafting Node (The Scribe):**
    * If an action requires a reply, this node drafts a professional response using the context from the previous nodes.
5.  **🖥️ UI Presentation:** The final state is rendered in the Streamlit frontend.

---

## 🚀 Features

### 📨 Smart Inbox Interface
* **Split-View Layout:** A professional 3-column design featuring a sticky sidebar, a scrollable email list, and a focused reading pane.
* **Visual Cues:** Color-coded badges for Priority (🔴 High, 🟠 Medium, 🟢 Low) and Categories.

### 🤖 Intelligent Processing
* **Auto-Drafting:** Alfred pre-fills the "Compose" box with a draft reply for actionable emails. If no reply is needed, the system informs the user.
* **Noise Filtering:** Automatically identifies and tags Newsletters and Spam, allowing users to focus on "Work" and "Urgent" items.
* **Entity Recognition:** Highlights dates, times, and names in a dedicated "Key Information" box, so you don't have to hunt through the text.

---

## 🛠️ Installation & Setup

Follow these steps to run Alfred locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/alfred-inbox.git](https://github.com/your-username/alfred-inbox.git)
cd alfred-inbox

```

### 2. Set up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure Environment

Create a `.env` file in the root directory. You will need a **Groq API Key** (Free Tier available for Llama 3).

```env
GROQ_API_KEY=gsk_your_key_here...

```

### 5. Run the Application

```bash
streamlit run app.py

```

---

## 📂 Project Structure

```text
alfred/
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration (Prompts, Model settings)
├── data/
│   └── dataset_emails.csv    # Raw dataset for testing
├── Data_clean/
│   ├── data_loader.py        # Data ingestion and cleaning logic
│   └── test_parser.py        # Parser testing utilities
├── logs/
│   └── email_organizer.log   # Application runtime logs
├── src/
│   ├── __init__.py
│   ├── agents.py             # LangGraph Agent definitions (Router, Analyzer, Writer)
│   ├── app.py                # Main Streamlit UI application
│   ├── email_processor.py    # Core processing orchestration
│   ├── logger.py             # Logging configuration
│   └── utils.py              # Helper functions
├── tests/
│   └── test_utils.py         # Unit tests
├── .env                      # Environment variables (API Keys)
├── .gitignore                # Git ignore rules
├── CHANGELOG.md              # Version history
├── PIPELINE.md               # Architecture documentation
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
└── run_app.py                # Execution entry point

```

---

## 🧪 Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) - For the production-ready UI.
* **LLM Backend:** [Groq](https://groq.com/) (Llama 3-70b) - Chosen for high-speed inference and reasoning capabilities.
* **Orchestration:** [LangChain](https://www.langchain.com/) & [LangGraph](https://www.google.com/search?q=https://python.langchain.com/docs/langgraph) - For stateful multi-agent workflows.
* **Data Processing:** [Pandas](https://pandas.pydata.org/) - For efficient CSV manipulation.
