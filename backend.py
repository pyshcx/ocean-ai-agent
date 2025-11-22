import sqlite3
import json
import os

# Configuration
DB_NAME = "email_agent.db"

def get_db_connection():
    """Creates a database connection with row factory for dictionary-like access."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

# --- PHASE 1: INGESTION ---

def load_inbox_from_json(json_file_path="inbox.json"):
    """
    Reads the Mock Inbox JSON and loads it into the SQLite database.
    [cite_start]This satisfies the 'Inbox Ingestion' requirement[cite: 34].
    """
    if not os.path.exists(json_file_path):
        return False, "JSON file not found."

    try:
        with open(json_file_path, 'r') as f:
            emails = json.load(f)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        count = 0
        for email in emails:
            # ID is used to prevent duplicates (INSERT OR IGNORE)
            cursor.execute('''
                INSERT OR IGNORE INTO emails (id, sender, subject, body, timestamp, read_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email['id'], email['sender'], email['subject'], email['body'], email['timestamp'], email['read']))
            if cursor.rowcount > 0:
                count += 1
            
        conn.commit()
        conn.close()
        return True, f"Successfully ingested {count} new emails."
    except Exception as e:
        return False, str(e)

def get_all_emails():
    """Fetches all emails to display in the Inbox UI"""# cite: 81
    conn = get_db_connection()
    emails = conn.execute('SELECT * FROM emails ORDER BY timestamp DESC').fetchall()
    conn.close()
    return [dict(e) for e in emails] # Convert to list of dicts

def get_email_by_id(email_id):
    """Fetches a single email for the Detailed View."""
    conn = get_db_connection()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()
    conn.close()
    return dict(email) if email else None

# --- PHASE 2: PROMPT BRAIN ---

def get_prompt_template(prompt_name):
    """
    Fetches the CURRENT prompt template from the DB.
    [cite_start]CRITICAL: This ensures the agent uses user-defined prompts[cite: 40].
    """
    conn = get_db_connection()
    row = conn.execute('SELECT prompt_template FROM prompts WHERE prompt_name = ?', (prompt_name,)).fetchone()
    conn.close()
    return row['prompt_template'] if row else "Error: Prompt not found."

def update_prompt_template(prompt_name, new_template):
    """Allows the user to edit and save prompts via the UI[cite: 38]."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE prompts SET prompt_template = ? WHERE prompt_name = ?', (new_template, prompt_name))
    conn.commit()
    conn.close()

def get_all_prompts():
    """Used to populate the 'Prompt Brain' configuration panel."""
    conn = get_db_connection()
    prompts = conn.execute('SELECT * FROM prompts').fetchall()
    conn.close()
    return [dict(p) for p in prompts]

# --- PHASE 3: STATE MANAGEMENT & DRAFTS ---

def update_email_metadata(email_id, category=None, action_items=None):
    """
    Saves the LLM's categorization and parsing results back to the DB.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if category:
        cursor.execute('UPDATE emails SET category = ? WHERE id = ?', (category, email_id))
    
    if action_items:
        # Ensure we store valid JSON string
        if isinstance(action_items, (dict, list)):
            action_items = json.dumps(action_items)
        cursor.execute('UPDATE emails SET action_items = ? WHERE id = ?', (action_items, email_id))
        
    conn.commit()
    conn.close()

def save_draft(email_id, draft_body, draft_subject="Re:"):
    """
    Saves a draft reply to the DB.
    [cite_start]Requirement: 'Drafts are safely stored, not sent'[cite: 36].
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO drafts (email_id, draft_subject, draft_body, status)
        VALUES (?, ?, ?, 'saved')
    ''', (email_id, draft_subject, draft_body))
    conn.commit()
    conn.close()

def get_drafts_for_email(email_id):
    conn = get_db_connection()
    drafts = conn.execute('SELECT * FROM drafts WHERE email_id = ?', (email_id,)).fetchall()
    conn.close()
    return [dict(d) for d in drafts]