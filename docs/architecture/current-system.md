# Current system (pre-migration)

The original runtime is `run_app.py`, which launches the Streamlit UI in `src/app.py`. It loads CSV data through `Data_clean/data_loader.py` (or `src.utils` as a fallback), retains processed mail only in Streamlit session state, and renders a list plus reading pane.

`src/agents.py` builds a LangGraph workflow with classifier, prioritization, and response-architect roles. The active provider is Groq (`ChatGroq` and a Llama model); configuration in `config/settings.py` exposes `GROQ_API_KEY`. `src/email_processor.py` wraps that workflow and has an in-repository cache directory. Thus a normal imported email can incur several provider-oriented stages and draft generation is eager.

Useful behavior retained in the replacement is permissive CSV cleanup: sender, subject, body, timestamp, attachment and thread fields. Replaced pieces are Streamlit/session-only persistence, cloud inference, LangGraph production orchestration, regex/prose-style agent output, and eager drafts.
