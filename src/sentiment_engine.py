"""Sentiment engine wrapping an LLM prompt and fallbacks.

This module exposes a high-level function that takes arbitrary text and
returns a strict numerical score [-1.0, 1.0] together with a one-sentence
summary. The implementation uses an LLM (via OpenAI) with a carefully
crafted prompt to force JSON output. If the API call fails or returns
non-JSON, a keyword heuristic fallback is used.
"""
import os
import json

from sentiment import analyze_text_sentiment

try:
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
except ImportError:
    genai = None

PROMPT_TEMPLATE = (
    "You are a financial sentiment analyzer.\n"
    "Read the provided text and respond with a JSON object ONLY, no text explanation.\n"
    "The JSON must have the following keys:\n"
    "  - score: a number between -1.0 (very negative) and 1.0 (very positive)\n"
    "  - summary: a single-sentence summary of the sentiment.\n"
    "Do not include any other keys or comments.\n"
    "Analyze this text:\n"
    '"""{text}"""\n'
)


def analyze_with_llm(text: str) -> dict:
    """Analyze text using the Gemini 1.5 Flash engine.

    Returns a dict with keys 'score' (float) and 'summary' (str). Falls
    back to a simple heuristic if the API call fails for any reason.
    """
    if client is None:
        return {
            "score": analyze_text_sentiment(text),
            "summary": "API SDK missing. " + text.strip().replace("\n", " ")[:100] + "...",
        }

    prompt = PROMPT_TEMPLATE.format(text=text)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        output = response.text.strip()
        result = json.loads(output)
        
        # sanitize score boundary
        if "score" in result:
            result["score"] = max(-1.0, min(1.0, float(result["score"])))
            
        return result
        
    except Exception as e:
        print(f"API Error traceback: {e}")
        # Fallback to mathematical sentiment heuristic if LLM throws error
        return {
            "score": analyze_text_sentiment(text),
            "summary": f"LLM parsing failed. {text.strip().replace(chr(10), ' ')[:100]}...",
        }


def analyze_text(text: str) -> dict:
    """Public API: always return a dict with score and summary.

    This is the function other modules should call.
    """
    # ensure text is not empty
    if not text or not text.strip():
        text = "No content available. Market data could not be retrieved."
    return analyze_with_llm(text)
