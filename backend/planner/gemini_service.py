"""
Gemini Service — LLM Enhancement Layer.
RESPONSIBILITY: Call Gemini to enhance the pre-built schedule and generate roadmaps with key rotation.
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

logging.basicConfig(level=logging.INFO)
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


def _call_gemini_with_rotation(
    prompt: str,
    config: types.GenerateContentConfig,
    required_keys: list,
    tag: str,
    retries: int = 1
) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini with API key rotation on 429 quota exhaustion.
    Cleans trailing braces and validates required keys.
    """
    keys = _get_api_keys()
    if not keys:
        logger.error(f"[{tag}] No Gemini API keys configured in .env")
        return None

    for idx, key in enumerate(keys):
        logger.info(f"[{tag}] Calling Gemini using Key #{idx+1}/{len(keys)} (starts with {key[:8]}...)...")
        try:
            # Configure fast fail retries so we fall back to next key quickly on repeated 429s
            from google.genai.types import HttpOptions, HttpRetryOptions
            http_options = HttpOptions(
                retry_options=HttpRetryOptions(attempts=1, initial_delay=1.0)
            )
            client = genai.Client(api_key=key, http_options=http_options)

            for attempt in range(retries + 1):
                if attempt > 0:
                    logger.info(f"[{tag}] Retrying key #{idx+1} (attempt {attempt+1}/{retries+1})...")
                    time.sleep(1.5)
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=config,
                    )
                    raw = response.text
                    logger.info(f"[{tag}] Raw response length: {len(raw) if raw else 0} chars")

                    if not raw or not raw.strip():
                        logger.warning(f"[{tag}] Key #{idx+1} returned empty response.")
                        continue

                    text = raw.strip()
                    # Strip markdown json wrappers
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
                        logger.warning(f"[{tag}] No JSON object boundaries found.")
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
                                logger.warning(f"[{tag}] JSONDecodeError: {jde}. Extracted: {extracted}")
                                break

                    if parsed is None:
                        logger.warning(f"[{tag}] JSON parsing failed.")
                        try:
                            os.makedirs("scratch", exist_ok=True)
                            with open("scratch/failed_json_response.txt", "w", encoding="utf-8") as f:
                                f.write(extracted)
                            logger.info(f"[{tag}] Saved failed response to scratch/failed_json_response.txt")
                        except Exception as fe:
                            logger.error(f"[{tag}] Failed to save debug file: {fe}")
                        continue

                    # Validate required keys
                    missing = [k for k in required_keys if k not in parsed]
                    if missing:
                        logger.warning(f"[{tag}] Missing required keys: {missing}. Got: {list(parsed.keys())}")
                        continue

                    logger.info(f"[{tag}] ✅ Successful API call and parse with Key #{idx+1}!")
                    return parsed

                except Exception as attempt_err:
                    logger.warning(f"[{tag}] Attempt {attempt+1} failed with error: {attempt_err}")
                    if "429" in str(attempt_err) or "RESOURCE_EXHAUSTED" in str(attempt_err):
                        # Quota exceeded, exit attempts loop and try next key immediately
                        break
        except Exception as key_err:
            logger.warning(f"[{tag}] Key #{idx+1} client setup or call failed: {key_err}")

    logger.error(f"[{tag}] ❌ All {len(keys)} API keys failed.")
    return None


def enhance_schedule(prompt: str, retries: int = 1) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini to enhance the pre-built schedule.
    """
    config = types.GenerateContentConfig(
        temperature=0.35,
        top_p=0.85,
        top_k=40,
        max_output_tokens=4096,
        response_mime_type="application/json",
    )
    return _call_gemini_with_rotation(
        prompt=prompt,
        config=config,
        required_keys=["plan_summary", "schedule"],
        tag="Planner LLM",
        retries=retries
    )


def generate_json_response(
    prompt: str,
    required_keys: list,
    tag: str = "Gemini LLM",
    retries: int = 1,
    max_tokens: int = 4096,
) -> Optional[Dict[str, Any]]:
    """
    Generic Gemini call that returns parsed JSON using key rotation.
    """
    config = types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.85,
        top_k=40,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
    )
    return _call_gemini_with_rotation(
        prompt=prompt,
        config=config,
        required_keys=required_keys,
        tag=tag,
        retries=retries
    )
