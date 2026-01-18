import streamlit as st
import time
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# --- PATH SETUP (Crucial for Imports) ---
# This ensures Python can find your 'src' and 'Data_clean' folders
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_clean_dir = os.path.join(parent_dir, 'Data_clean') # Point to Data_clean folder

# Add all necessary paths
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)
if data_clean_dir not in sys.path: sys.path.append(data_clean_dir)

# --- IMPORTS ---
try:
    # Try importing from local directory first, then src
    try:
        from data_loader import clean_and_load_emails
        from agents import EmailProcessingOrchestrator
    except ImportError:
        from src.utils import load_emails_from_csv as clean_and_load_emails
        from src.agents import EmailProcessingOrchestrator
except ImportError as e:
    # Fallback to catch-all
    st.error(f"⚠️ Critical Error: Missing backend files. {e}")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Alfred | Intelligent Inbox",
    page_icon="🕴️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS (Dark Mode & Layout) ---
st.markdown("""
<style>
    /* 1. Global Layout */
    .block-container { padding-top: 3rem !important; padding-bottom: 5rem; }
    
    /* 2. Scrollable Containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        scrollbar-width: thin;
    }

    /* 3. Inbox Item Styling */
    div.stButton > button:first-child {
        width: 100%;
        text-align: left !important;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: border-color 0.2s;
        height: auto;
        white-space: pre-wrap;
    }
    div.stButton > button:first-child:hover {
        border-color: var(--primary-color);
        background-color: var(--background-color);
    }
    div.stButton > button:first-child p {
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 0;
    }

    /* 4. Reading Pane */
    .email-header {
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 15px;
    }
    .email-body {
        font-family: 'Source Sans Pro', sans-serif;
        line-height: 1.6;
        white-space: pre-wrap;
        color: var(--text-color);
        padding: 10px 0;
        font-size: 1rem;
    }
    
    /* 5. Analysis Labels */
    .analysis-label {
        font-weight: bold;
        color: var(--primary-color);
        font-size: 0.85rem;
        text-transform: uppercase;
        margin-bottom: 5px;
        margin-top: 15px;
        display: block;
    }
    
    /* 6. Badges */
    .badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(128, 128, 128, 0.15);
        margin-left: 5px;
    }
    
    /* 7. Empty State */
    .empty-state {
        text-align: center;
        margin-top: 150px;
        color: gray;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def format_date(iso_str: Optional[str]) -> str:
    """Smart date formatting"""
    if not iso_str: return "Unknown"
    try:
        if 'T' in iso_str: iso_str = iso_str.split('T')[0]
        dt = datetime.fromisoformat(iso_str.replace('Z', ''))
        now = datetime.now()
        diff = (now - dt).days
        if diff == 0: return dt.strftime("%I:%M %p").lstrip('0')
        elif diff == 1: return "Yesterday"
        elif diff < 7: return dt.strftime("%A")
        return dt.strftime("%b %d")
    except:
        return str(iso_str)[:10]

def parse_manual_email(text: str) -> Dict:
    """Parses manually typed emails"""
    email = {
        'email_id': f"man_{int(time.time())}",
        'sender_name': 'Unknown',
        'sender_email': 'manual@input.com',
        'subject': '(No Subject)',
        'body': text,
        'timestamp': datetime.now().isoformat(),
        'category': 'Inbox',
        'priority': 'Medium',
        'status': 'Pending'
    }
    lines = text.strip().split('\n')
    body_lines = []
    headers_done = False
    for line in lines:
        if not headers_done and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                k = parts[0].strip().lower()
                v = parts[1].strip()
                if k == 'from': email['sender_email'] = v
                elif k == 'name': email['sender_name'] = v
                elif k == 'subject': email['subject'] = v
                elif k == 'category': email['category'] = v
                elif k == 'priority': email['priority'] = v
                else: body_lines.append(line)
        else:
            if line.strip() == "": headers_done = True
            body_lines.append(line)
    email['body'] = '\n'.join(body_lines).strip()
    return email

def format_entities_markdown(data):
    """Converts key info dictionary to clean markdown bullets"""
    if not data or str(data).lower() in ['n/a', 'none', '{}', '[]']:
        return "No specific entities identified."
    
    if isinstance(data, dict):
        return "\n".join([f"- **{k.title().replace('_', ' ')}:** {v}" for k, v in data.items()])
    
    if isinstance(data, list):
        return "\n".join([f"- {str(item)}" for item in data])
        
    return str(data)

# --- SESSION STATE ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🕴️ Alfred")
    st.caption("Intelligent Inbox Protocol")
    st.divider()

    with st.expander("📥 Data Sources", expanded=not bool(st.session_state.processed_data)):
        tab_csv, tab_man = st.tabs(["Upload CSV", "Manual Add"])
        with tab_csv:
            uploaded_file = st.file_uploader("Upload Stream", type="csv", label_visibility="collapsed")
            if uploaded_file and not st.session_state.processed_data:
                with st.spinner("Alfred is indexing & analyzing..."):
                    raw_data = clean_and_load_emails(uploaded_file)
                    if raw_data:
                        orchestrator = EmailProcessingOrchestrator()
                        prog = st.progress(0)
                        results = []
                        total = len(raw_data)
                        for i, email in enumerate(raw_data):
                            try:
                                res = orchestrator.process_email(email)
                                email.update(res)
                                email['status'] = 'Processed'
                            except Exception as e:
                                email['status'] = 'Error'
                            results.append(email)
                            prog.progress((i+1)/total)
                        st.session_state.processed_data = results
                        st.rerun()

        with tab_man:
            manual_text = st.text_area("Paste content:", height=150, placeholder="From: ...\nSubject: ...\nBody: ...")
            if st.button("Add Email"):
                new_email = parse_manual_email(manual_text)
                try:
                    orc = EmailProcessingOrchestrator()
                    res = orc.process_email(new_email)
                    new_email.update(res)
                    new_email['status'] = 'Processed'
                except: pass
                st.session_state.processed_data.insert(0, new_email)
                st.rerun()

    if st.session_state.processed_data:
        total = len(st.session_state.processed_data)
        urgent = sum(1 for e in st.session_state.processed_data if e.get('priority') == 'High')
        c1, c2 = st.columns(2)
        c1.metric("Total", total)
        c2.metric("High Prio", urgent)

    st.divider()
    st.subheader("Filters")
    search_query = st.text_input("Search", placeholder="Keywords...")
    filter_prio = st.multiselect("Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    current_cats = set([e.get('category', 'Inbox') for e in st.session_state.processed_data])
    std_cats = {"Work", "Personal", "Newsletter", "Urgent", "Spam", "Inbox"}
    all_cats = sorted(list(current_cats.union(std_cats)))
    filter_cat = st.multiselect("Category", all_cats, default=all_cats)

# --- FILTERING ---
filtered_emails = st.session_state.processed_data
if search_query:
    q = search_query.lower()
    filtered_emails = [e for e in filtered_emails if q in str(e.get('subject','')).lower() or q in str(e.get('sender_name','')).lower()]
if filter_prio:
    filtered_emails = [e for e in filtered_emails if e.get('priority', 'Unknown') in filter_prio or e.get('priority') == 'Unknown']
if filter_cat:
    filtered_emails = [e for e in filtered_emails if e.get('category', 'Inbox') in filter_cat]

# --- MAIN LAYOUT ---
col_list, col_read = st.columns([1.5, 2.5], gap="medium")

# === COLUMN 2: INBOX LIST ===
with col_list:
    st.markdown("### 📥 Inbox")
    with st.container(height=750, border=True):
        if not filtered_emails:
            st.info("No emails found.")
        for email in filtered_emails:
            sender = email.get('sender_name') or email.get('sender_email', 'Unknown')
            subj = email.get('subject', '(No Subject)')
            prio = email.get('priority', 'Unknown')
            icon = "⚪"
            if prio == 'High': icon = "🔴"
            if prio == 'Medium': icon = "🟠"
            if prio == 'Low': icon = "🟢"
            date_str = format_date(email.get('timestamp'))
            label = f"{icon} **{sender}** | {date_str}\n{subj[:45]}..."
            if st.button(label, key=f"btn_{email.get('email_id')}", use_container_width=True):
                st.session_state.selected_email = email
                st.rerun()

# === COLUMN 3: READING PANE ===
with col_read:
    st.markdown("### 📄 Reading Pane")
    # FIX: Remove fixed height to allow expansion
    with st.container(border=True):
        selected = st.session_state.selected_email
        
        if selected:
            st.markdown(f"""
            <div class="email-header">
                <h3>{selected.get('subject', 'No Subject')}</h3>
                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                    <div>
                        <small>From: <b>{selected.get('sender_name', 'Unknown')}</b></small><br>
                        <small style="color:gray;">{selected.get('sender_email')}</small>
                    </div>
                    <div>
                        <span class="badge">{selected.get('category', 'General')}</span>
                        <span class="badge">{format_date(selected.get('timestamp'))}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Message:**")
            st.markdown(f"""<div class="email-body">{selected.get('body', 'No content.')}</div>""", unsafe_allow_html=True)
            st.divider()
            
            if selected.get('status') == 'Processed':
                st.markdown("**🕴️ Alfred's Report:**")
                
                # Fetch Data safely
                reasoning = selected.get('reasoning', 'No reasoning available.')
                action = selected.get('action_recommendation', 'No action recommended.')
                raw_entities = selected.get('key_info', {})
                
                # Format Entities
                formatted_entities = format_entities_markdown(raw_entities)

                # Render Analysis (Using native columns)
                st.markdown('<span class="analysis-label">💡 Reasoning</span>', unsafe_allow_html=True)
                st.info(reasoning)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<span class="analysis-label">✅ Action</span>', unsafe_allow_html=True)
                    st.success(action)
                with c2:
                    st.markdown('<span class="analysis-label">🔑 Key Entities</span>', unsafe_allow_html=True)
                    st.warning(formatted_entities)

                st.divider()

                # --- 4. DRAFT REPLY SECTION (SMART LOGIC) ---
                st.markdown("**✍️ Draft Reply:**")
                
                # 1. Search for AI draft (Case-insensitive & Safe)
                possible_keys = [
                    'draft_response', 'draft_reply', 'email_draft', 
                    'response_email', 'draft', 'reply', 'generated_response'
                ]
                
                raw_draft = None
                email_data_lower = {k.lower(): v for k, v in selected.items()}
                
                for k in possible_keys:
                    val = email_data_lower.get(k)
                    if val and isinstance(val, str):
                        clean_val = val.strip()
                        # Only filter "n/a" if the text is very short (prevents blocking long valid emails)
                        is_short_placeholder = len(clean_val) < 20 and ("n/a" in clean_val.lower() or "none" in clean_val.lower())
                        
                        if not is_short_placeholder and len(clean_val) > 5:
                            raw_draft = clean_val
                            break
                
                # 2. Logic: Show Draft vs Template vs Empty
                if raw_draft:
                    final_draft = raw_draft
                    caption_text = "✅ Alfred generated a draft for you:"
                else:
                    # Only show template if action implies a reply is needed
                    action_str = str(action).lower()
                    if "reply" in action_str or "respond" in action_str:
                        sender = selected.get('sender_name') or "there"
                        subject = selected.get('subject') or "your email"
                        final_draft = f"""Hi {sender},

Thank you for your email regarding "{subject}".

[Alfred suggests a reply, but couldn't generate a draft. Please add your response here.]

Best regards,
[Your Name]"""
                        caption_text = "ℹ️ Reply recommended. Using template:"
                    else:
                        # Action is Archive, Read, etc. -> No template needed
                        final_draft = ""
                        caption_text = "ℹ️ No reply recommended."

                st.caption(caption_text)

                # 3. Render Draft Box (Populated or Empty)
                edited_draft = st.text_area(
                    "Compose Reply", 
                    value=final_draft, 
                    height=250, 
                    placeholder="Type your reply here...",
                    key=f"draft_{selected.get('email_id', 'unknown')}",
                    label_visibility="collapsed"
                )
                
                c1, c2 = st.columns([1, 4])
                with c1:
                    if st.button("Send ✉️", type="primary", key=f"send_{selected.get('email_id')}"):
                        st.toast("Reply dispatched.", icon="🚀")
                with c2:
                    if st.button("Archive 📥", key=f"archive_{selected.get('email_id')}"):
                        st.toast("Thread archived.", icon="📦")
                
                with st.expander("🔍 Debug Raw Data"):
                    st.json(selected)

            else:
                st.warning("Analysis pending. Please wait or reload.")
        else:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size: 4rem;">🕴️</div>
                <h3>Alfred is ready.</h3>
                <p>Select a communication from the inbox to begin review.</p>
            </div>
            """, unsafe_allow_html=True)