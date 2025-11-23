import os
import json
from dotenv import load_dotenv

# Load local .env (for local development)
load_dotenv()

# Read Gemini API key (from .env or Render environment variables)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Import the Gemini SDK
import google.generativeai as genai

# Configure Gemini API
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
else:
    print("⚠️ WARNING: GEMINI_API_KEY not found. Using fallback empty structure only.")


# ------------------ PROMPT TEMPLATE ------------------

PROMPT_TEMPLATE = """
You are an assistant that extracts structured hiring needs from a free-form job query or job description.

Input:
{query}

Return a JSON object with EXACTLY these keys:

- role (string)
- seniority (one of: entry-level, junior, mid-level, senior, lead)
- skills (array of skill strings)
- personality_traits (array of trait strings)
- domain (string)
- weights (an object with numeric weights 'skills' and 'personality' that sum to 1)

Return ONLY valid JSON. No explanations.
"""


# ------------------ CALL GEMINI LLM ------------------

def call_llm(prompt: str) -> str:
    """
    Calls Google Gemini API. Returns text response.
    Fallback: returns empty JSON structure.
    """
    # If key missing → fallback
    if not GEMINI_KEY:
        return json.dumps({
            "role": "",
            "seniority": "",
            "skills": [],
            "personality_traits": [],
            "domain": "",
            "weights": {"skills": 0.6, "personality": 0.4}
        })

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("❌ Gemini API Error:", e)
        # fallback structure
        return json.dumps({
            "role": "",
            "seniority": "",
            "skills": [],
            "personality_traits": [],
            "domain": "",
            "weights": {"skills": 0.6, "personality": 0.4}
        })


# ------------------ FINAL PARSER FUNCTION ------------------

def extract_structured(query: str):
    """
    Creates prompt → calls Gemini → parses JSON safely.
    """
    prompt = PROMPT_TEMPLATE.format(query=query)
    raw = call_llm(prompt)

    try:
        parsed = json.loads(raw)
    except:
        parsed = {
            "role": "",
            "seniority": "",
            "skills": [],
            "personality_traits": [],
            "domain": "",
            "weights": {"skills": 0.6, "personality": 0.4}
        }

    return parsed
