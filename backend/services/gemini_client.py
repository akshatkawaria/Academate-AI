"""
Gemini Client with key rotation and robust JSON cleaning.
"""
import os
import json
import logging
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def _get_api_keys() -> list:
    """Get all unique configured API keys from environment."""
    keys = [
        os.getenv("GEMINI_PLANNER_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
        os.getenv("SKILL_AGENT_GEMINI_KEY")
    ]
    seen = set()
    filtered = []
    for k in keys:
        if k and k.strip() and k not in seen:
            seen.add(k)
            filtered.append(k)
    return filtered


def get_ai_response(prompt: str, model_name: str = "gemini-2.5-flash", retries: int = 1) -> Optional[Dict[str, Any]]:
    """
    Centralized Gemini call with key rotation. Returns parsed JSON or None on failure.
    Never raises — always falls back.
    """
    keys = _get_api_keys()
    if not keys:
        logger.error("[Gemini Client] No Gemini API keys configured in .env")
        return None

    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.8,
        top_k=20,
        max_output_tokens=1024,
        response_mime_type="application/json",
    )

    for idx, key in enumerate(keys):
        logger.info(f"[Gemini Client] Calling model {model_name} with Key #{idx+1}/{len(keys)}...")
        try:
            from google.genai.types import HttpOptions, HttpRetryOptions
            http_options = HttpOptions(
                retry_options=HttpRetryOptions(attempts=1, initial_delay=1.0)
            )
            client = genai.Client(api_key=key, http_options=http_options)

            for attempt in range(retries + 1):
                if attempt > 0:
                    time.sleep(1)
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )

                    text = response.text.strip()
                    # Strip accidental markdown
                    if "```" in text:
                        parts = text.split("```")
                        for part in parts:
                            cleaned = part.lstrip("json").strip()
                            if cleaned.startswith("{"):
                                text = cleaned
                                break

                    start = text.find("{")
                    end = text.rfind("}") + 1
                    if start == -1 or end == 0:
                        continue

                    extracted = text[start:end]

                    # Parse and clean trailing garbage / extra braces iteratively
                    parsed = None
                    clean_attempts = 0
                    while clean_attempts < 10:
                        try:
                            parsed = json.loads(extracted)
                            break
                        except json.JSONDecodeError as jde:
                            if "Extra data" in str(jde):
                                extracted = extracted[:jde.pos].strip()
                                clean_attempts += 1
                            else:
                                break

                    if parsed is not None:
                        return parsed

                except Exception as attempt_err:
                    logger.warning(f"[Gemini Client] Attempt {attempt+1} failed: {attempt_err}")
                    if "429" in str(attempt_err) or "RESOURCE_EXHAUSTED" in str(attempt_err):
                        break
        except Exception as key_err:
            logger.warning(f"[Gemini Client] Key #{idx+1} failed: {key_err}")

    return None
