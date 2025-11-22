import sqlite3

def init_db():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('email_agent.db')
    cursor = conn.cursor()

    # 1. Create PROMPTS table (The "Brain")
    # This stores the templates. The Agent MUST read from here.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt_name TEXT UNIQUE NOT NULL,
        prompt_template TEXT NOT NULL
    )
    ''')

    # 2. Create EMAILS table
    # We will load the JSON into this table so we can tag them easily.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id TEXT PRIMARY KEY,
        sender TEXT,
        subject TEXT,
        body TEXT,
        timestamp TEXT,
        read_status BOOLEAN,
        category TEXT DEFAULT NULL,
        action_items TEXT DEFAULT NULL
    )
    ''')

    # 3. Create DRAFTS table
    # Requirement: "Drafts are safely stored, not sent" [cite: 36]
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        draft_subject TEXT,
        draft_body TEXT,
        status TEXT DEFAULT 'saved',
        FOREIGN KEY(email_id) REFERENCES emails(id)
    )
    ''')

    # --- INSERT DEFAULT PROMPTS [cite: 61-70] ---
    # Using UPSERT (OR REPLACE) to ensure defaults exist
    prompts_data = [
        (
            "categorize_email",
            """
            Role: You are an advanced email classifier.
            Task: Categorize the following email into one of these categories: 'Important', 'Newsletter', 'Spam', 'To-Do', 'Project Update'.
            
            Rules:
            1. 'To-Do' must include a direct request requiring user action.
            2. 'Important' is for urgent deadlines or HR matters.
            3. Output ONLY the category name, nothing else.
            
            Email Content:
            Subject: {subject}
            Body: {body}
            """
        ),
        (
            "extract_action_items",
            """
            Role: You are a task extractor.
            Task: Extract action items and deadlines from the email.
            
            Format: Respond strictly in JSON format: {"tasks": [{"task": "...", "deadline": "..."}]}
            If no tasks, return {"tasks": []}.
            
            Email Content:
            {body}
            """
        ),
        (
            "suggest_reply",
            """
            Role: You are a helpful email assistant.
            Task: Draft a polite and professional reply to this email.
            
            Context:
            - If it's a meeting request, ask for an agenda and propose 2 PM as a time.
            - If it's a task, confirm receipt and estimate completion by EOD.
            - Keep it concise.
            
            Incoming Email:
            {body}
            """
        )
    ]

    cursor.executemany('''
    INSERT OR REPLACE INTO prompts (prompt_name, prompt_template)
    VALUES (?, ?)
    ''', prompts_data)

    conn.commit()
    conn.close()
    print("Database 'email_agent.db' initialized successfully with default prompts.")

if __name__ == "__main__":
    init_db()