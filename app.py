import streamlit as st
import pandas as pd
import backend
import llm_engine

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="OceanAI Email Agent",
    page_icon="📧",
    layout="wide"
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📧 OceanAI Agent")
page = st.sidebar.radio("Navigate", ["Inbox", "Email Agent (Chat)", "Prompt Brain"])

st.sidebar.divider()

# Ingestion Control
st.sidebar.subheader("System Controls")
if st.sidebar.button("📥 Load Mock Inbox"):
    with st.spinner("Ingesting emails..."):
        success, msg = backend.load_inbox_from_json()
        if success:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)

if st.sidebar.button("🤖 Process Emails (AI)"):
    with st.spinner("Running AI Categorization & Task Extraction..."):
        emails = backend.get_all_emails()
        progress_bar = st.sidebar.progress(0)
        
        for i, email in enumerate(emails):
            # 1. Categorize
            if not email['category']:
                cat = llm_engine.process_email_with_prompt(email, "categorize_email")
                backend.update_email_metadata(email['id'], category=cat)
            
            # 2. Extract Tasks
            if not email['action_items']:
                tasks = llm_engine.parse_action_items(email)
                backend.update_email_metadata(email['id'], action_items=tasks)
            
            progress_bar.progress((i + 1) / len(emails))
        
        st.sidebar.success("Processing Complete!")
        st.rerun()

# --- PAGE 1: INBOX ---
if page == "Inbox":
    st.title("📨 Unified Inbox")
    
    emails = backend.get_all_emails()
    
    if not emails:
        st.info("Inbox is empty. Click 'Load Mock Inbox' in the sidebar.")
    else:
        # Create a simple dataframe for the list view
        df = pd.DataFrame(emails)
        df['display'] = df['sender'] + " | " + df['subject']
        
        # Layout: List on left, Details on right
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Messages")
            selected_email_index = st.radio(
                "Select Email:", 
                options=range(len(emails)), 
                format_func=lambda x: f"{emails[x]['sender']}: {emails[x]['subject'][:30]}..."
            )
            
        with col2:
            if selected_email_index is not None:
                email = emails[selected_email_index]
                
                # Header
                st.subheader(email['subject'])
                st.caption(f"From: {email['sender']} | Time: {email['timestamp']}")
                
                # Tags
                col_tags1, col_tags2 = st.columns(2)
                with col_tags1:
                    st.write(f"**Category:** `{email['category'] or 'Unprocessed'}`")
                with col_tags2:
                    # Display Action Items if they exist
                    if email['action_items']:
                        try:
                            import json
                            tasks = json.loads(email['action_items'])
                            if tasks.get('tasks'):
                                st.warning(f"⚠️ Action Items: {len(tasks['tasks'])}")
                        except:
                            pass

                st.divider()
                
                # Body
                st.write(email['body'])
                
                st.divider()
                
                # Action Items Section
                if email['action_items']:
                    st.markdown("### 📝 Extracted Tasks")
                    try:
                        tasks_data = json.loads(email['action_items'])
                        tasks_list = tasks_data.get("tasks", [])
                        if tasks_list:
                            for t in tasks_list:
                                st.checkbox(f"{t.get('task')} (Due: {t.get('deadline')})")
                        else:
                            st.info("No specific tasks extracted.")
                    except Exception as e:
                        st.error(f"Error parsing tasks: {e}")

                # Auto-Draft Section
                st.markdown("### ✍️ Quick Actions")
                if st.button("Generate Draft Reply"):
                    with st.spinner("Drafting reply..."):
                        draft_text = llm_engine.process_email_with_prompt(email, "suggest_reply")
                        backend.save_draft(email['id'], draft_text, f"Re: {email['subject']}")
                        st.session_state['current_draft'] = draft_text
                        st.success("Draft saved!")

                # Show saved drafts
                drafts = backend.get_drafts_for_email(email['id'])
                if drafts:
                    st.info(f"Found {len(drafts)} saved drafts.")
                    for d in drafts:
                        with st.expander(f"Draft: {d['draft_subject']}"):
                            st.text_area("Content", d['draft_body'], height=150)
                            st.button("Send (Mock)", key=f"send_{d['id']}", disabled=True, help="Sending disabled for assignment safety")

# --- PAGE 2: AGENT CHAT ---
elif page == "Email Agent (Chat)":
    st.title("🤖 Email Agent Chat")
    
    emails = backend.get_all_emails()
    if not emails:
        st.error("No emails found. Please load inbox first.")
    else:
        # Select context
        selected_id = st.selectbox(
            "Select an email to discuss:",
            options=[e['id'] for e in emails],
            format_func=lambda x: next((e['subject'] for e in emails if e['id'] == x), "Unknown")
        )
        
        current_email = next((e for e in emails if e['id'] == selected_id), None)
        
        if current_email:
            with st.expander("View Email Content"):
                st.write(current_email['body'])
            
            # Chat Interface
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # User Input
            if prompt := st.chat_input("Ask about this email (e.g., 'Summarize this', 'Draft a reply')"):
                # User message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Assistant response
                with st.chat_message("assistant"):
                    response = llm_engine.chat_with_email(current_email, prompt)
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- PAGE 3: PROMPT BRAIN ---
elif page == "Prompt Brain":
    st.title("🧠 Prompt Brain")
    st.markdown("Edit the system prompts here. The Agent's behavior will change immediately.")
    
    prompts = backend.get_all_prompts()
    
    for p in prompts:
        with st.expander(f"Edit: {p['prompt_name'].replace('_', ' ').title()}", expanded=True):
            new_template = st.text_area(
                "Prompt Template", 
                value=p['prompt_template'], 
                height=200,
                key=f"area_{p['prompt_name']}"
            )
            
            if st.button("Save Changes", key=f"save_{p['prompt_name']}"):
                backend.update_prompt_template(p['prompt_name'], new_template)
                st.success(f"Updated {p['prompt_name']} successfully!")