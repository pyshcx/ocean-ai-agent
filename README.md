# 📧 OceanAI Email Productivity Agent

A prompt-driven intelligent email agent capable of categorizing emails, extracting action items, and drafting replies using LLMs. The system features a **Prompt Brain** that allows users to customize the agent's behavior by editing the underlying system prompts.

---

## 🚀 Live Demo

[👉 **Live Demo**](https://ocean-ai-agent-22bci0156-pranayshah.streamlit.app/)

*(Note: The live demo runs on the Streamlit Community Cloud. If the app is asleep, please allow a moment for it to wake up.)*

---

## 📋 Features

- **Unified Inbox**  
  View emails with AI-generated tags (Category, Urgency) and extracted tasks.

- **Prompt-Driven Architecture**  
  The "Brain" of the agent is fully editable. Change the prompt templates in the UI, and the agent's behavior updates immediately.

- **Auto-Categorization**  
  Automatically sorts emails into *Important, Newsletter, Spam, To-Do,* or *Project Update*.

- **Action Item Extraction**  
  Parses emails to find specific tasks and deadlines, presenting them as structured checklists.

- **AI Chat Assistant**  
  Chat with your inbox. Ask questions like:  
  “Summarize this email” or “What are the deadlines for today?”

- **Draft Generation**  
  Generates context-aware replies based on user-defined tones. Drafts are stored locally and never auto-sent.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Python)  
- **LLM Orchestration:** LangChain  
- **Model:** Llama-3.3-70b-versatile (via Groq API)  
- **Database:** SQLite  
- **Data Handling:** Pandas, JSON  

---

## ⚙️ Installation & Local Setup

If you prefer to run the agent locally instead of using the live link, follow these steps.

### 1. Clone the Repository

```bash
git clone https://github.com/pyshcx/ocean-ai-agent.git
cd ocean-ai-agent
````

### 2. Install Dependencies

Ensure you have Python 3.10+ installed.

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

This project uses Groq for high-speed inference.

#### Option A: Secrets File *(Recommended)*

Create a `.streamlit` folder, then add a `secrets.toml` file:

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_your_api_key_here"
```

#### Option B: Environment Variable

```bash
export GROQ_API_KEY="gsk_your_api_key_here"
```

### 4. Initialize Database

Run the setup script:

```bash
python db_setup.py
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at **[http://localhost:8501](http://localhost:8501)**.

---

## 📖 Usage Guide

### 1. Load the Mock Inbox

* Open the sidebar.
* Click **📥 Load Mock Inbox**.
* This loads 15–20 sample emails from `inbox.json` into SQLite.

### 2. Process Emails

Click **🤖 Process Emails (AI)**.

The agent will analyze all unread emails, applying your Categorization and Action Extraction prompts.

### 3. Configure Prompts (“The Brain”)

* Open **Prompt Brain** in the sidebar.
* Expand a prompt (e.g., `suggest_reply`).
* Edit the text (e.g., change “Draft a polite reply” to “Draft a reply like a pirate”).
* Save changes and test immediately in the Inbox.

### 4. Email Agent (Chat)

Ask things like:

* “Summarize this email in 3 bullets.”
* “Does this email mention a specific time?”
* “Draft a decline message for this meeting.”

---

## 📂 Project Structure

```
ocean-ai-agent/
├── app.py              # Main Streamlit application (UI)
├── backend.py          # Database interactions & state management
├── llm_engine.py       # LangChain logic & Groq integration
├── db_setup.py         # Database initialization script
├── inbox.json          # Mock email data
├── email_agent.db      # SQLite database
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## 🛡️ Safety & Constraints

* **No Auto-Send:**
  The agent saves drafts only. No SMTP integration prevents accidental outgoing messages.

* **Data Privacy:**
  All processing happens via the LLM API. No permanent external storage.

---

Developed for the **OceanAI (MariApps) Super Dream Internship Assignment — Nov 2025**.
