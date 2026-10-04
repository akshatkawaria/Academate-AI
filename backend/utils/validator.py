import json
import logging
from typing import Optional, Any, Dict, List

logger = logging.getLogger(__name__)

def validate_json_response(text: str) -> Optional[Any]:
    """
    Safely parses JSON and strips any markdown or extra text.
    Returns parsed dict/list or None if malformed.
    """
    if not text:
        return None
        
    text = text.strip()
    
    # Strip markdown blocks
    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
    if text.endswith("```"):
        # Replace the last occurrence
        text = text[::-1].replace("```", "", 1)[::-1]
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Validator: JSON Parsing failed: {e}. Raw text: {text}")
        return None
