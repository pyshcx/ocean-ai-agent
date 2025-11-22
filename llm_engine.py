import os
import json
# --- UPDATED IMPORTS FOR NEW LANGCHAIN VERSIONS ---
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import backend
import streamlit as st

# --- CONFIGURATION ---
# (Keep your existing configuration below this line)

# --- CONFIGURATION ---

# 1. SET YOUR GROQ API KEY HERE
# You can get one at https://console.groq.com/keys
# Ideally, set this in your terminal: export GROQ_API_KEY="gsk_..."
# If you must hardcode it for testing (don't commit this to GitHub!):
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except FileNotFoundError:
    # Fallback: If running locally without secrets.toml, check system environment
    pass

if not os.environ.get("GROQ_API_KEY"):
    print("⚠️ WARNING: GROQ_API_KEY not found! AI features will fail.")
# 2. INITIALIZE GROQ LLM
# Llama3-70b is powerful enough for categorization and drafting
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
except Exception as e:
    print(f"Error initializing Groq: {e}")
    llm = None

def process_email_with_prompt(email_data, prompt_name):
    """
    1. Fetches the LATEST prompt from the DB.
    2. Feeds the email into that prompt.
    3. Returns the LLM result.
    """
    if not llm:
        return "Error: LLM not initialized. Check API Key."

    # 1. Fetch Prompt Template from DB
    template_str = backend.get_prompt_template(prompt_name)
    
    if "Error" in template_str:
        return "Error: Prompt not found in database."

    # 2. Create LangChain Prompt
    prompt = PromptTemplate.from_template(template_str)
    
    # 3. Create Chain
    chain = prompt | llm | StrOutputParser()
    
    # 4. Run Chain
    try:
        result = chain.invoke({
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", "")
        })
        return result.strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"

def parse_action_items(email_data):
    """
    Special handler for extracting JSON tasks.
    """
    if not llm:
        return {"tasks": [], "error": "LLM not initialized"}

    template_str = backend.get_prompt_template("extract_action_items")
    prompt = PromptTemplate.from_template(template_str)
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        # Get raw string from LLM
        raw_result = chain.invoke({"body": email_data.get("body", "")})
        
        # Clean up markdown if LLM adds ```json ... ```
        clean_result = raw_result.replace("```json", "").replace("```", "").strip()
        
        # Parse to Python Dict to ensure it's valid JSON
        return json.loads(clean_result) 
    except Exception as e:
        # Fallback for parsing errors
        return {"tasks": [], "error": f"Failed to parse JSON: {str(e)}"}

def chat_with_email(email_data, user_query):
    """
    Allows the user to ask questions about a specific email.
    """
    if not llm:
        return "Error: LLM not initialized."

    # Dynamic prompt for chat
    chat_template = """
    You are a helpful email assistant.
    
    Email Context:
    Subject: {subject}
    Body: {body}
    
    User Question: {query}
    
    Answer the question based strictly on the email provided. Keep it concise.
    """
    
    prompt = PromptTemplate.from_template(chat_template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        return chain.invoke({
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "query": user_query
        })
    except Exception as e:
        return f"Error processing chat: {str(e)}"