import os, json
PROMPT_TEMPLATE = """You are an assistant that extracts structured hiring needs from a free-form job query or job description.
Input:
{query}

Return a JSON object with keys:
- role (string)
- seniority (one of: entry-level, junior, mid-level, senior, lead) (if unknown, leave empty)
- skills (array of skill strings)
- personality_traits (array of trait strings)
- domain (string)
- weights (an object with numeric weights summing to 1, keys 'skills' and 'personality')

Return only valid JSON with those keys.
"""

def call_llm(prompt: str) -> str:
    # Replace with your LLM provider call (OpenAI/Gemini). For offline testing this returns a sample JSON.
    return json.dumps({
        "role":"",
        "seniority":"",
        "skills":[],
        "personality_traits":[],
        "domain":"",
        "weights":{"skills":0.6,"personality":0.4}
    })

def extract_structured(query: str):
    prompt = PROMPT_TEMPLATE.format(query=query)
    raw = call_llm(prompt)
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {
            "role":"",
            "seniority":"",
            "skills":[],
            "personality_traits":[],
            "domain":"",
            "weights":{"skills":0.6,"personality":0.4}
        }
    return parsed
