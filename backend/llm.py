import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Call to Primary model first, then an optional fallback in case of overload
MODELS = [m for m in (os.getenv("GEMINI_MODEL"), os.getenv("GEMINI_FALLBACK_MODEL")) if m]
RETRYABLE = {429, 500, 502, 503, 504}

def complete(system: str, messages: list[dict], retries: int = 3) -> str:
    contents = [{"role": "model" if m["role"] == "assistant" else "user",
                 "parts": [{"text": m["content"]}]} for m in messages]
    config = types.GenerateContentConfig(
        system_instruction=system, max_output_tokens=600, temperature=0)

    last_error = None
    for model in MODELS:
        for attempt in range(retries):
            try:
                resp = _client.models.generate_content(
                    model=model, contents=contents, config=config)
                return resp.text or ""
            except (errors.ServerError, errors.ClientError) as e:
                if getattr(e, "code", None) not in RETRYABLE:
                    raise                      #real error(bad key, bad model name)
                last_error = e
                time.sleep(2 ** attempt)       #wait 1s, 2s, 4s
    raise last_error