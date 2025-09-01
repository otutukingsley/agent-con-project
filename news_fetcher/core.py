import logging
from typing import List, Dict, Any
import re
from .config import RESPONSE_SCHEMA

# Configure logging
logger = logging.getLogger(__name__)

def validate_json_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the response adheres to the RESPONSE_SCHEMA.

    Args:
        response: The JSON response to validate.

    Returns:
        A validated JSON response, or a fallback with empty summary if invalid.
    """
    try:
        if not isinstance(response, dict):
            logger.error("Response is not a dictionary")
            return {"summary": {"summary_text": "Invalid response format.", "source_urls": []}}
        
        valid_keys = RESPONSE_SCHEMA["properties"].keys()
        if not all(key in valid_keys for key in response):
            logger.error(f"Invalid keys in response: {response.keys()}")
            return {"summary": {"summary_text": "Invalid response keys.", "source_urls": []}}
        
        if "articles" in response:
            for article in response["articles"]:
                required = RESPONSE_SCHEMA["properties"]["articles"]["items"]["required"]
                if not all(key in article for key in required):
                    logger.error(f"Invalid article format: {article}")
                    return {"summary": {"summary_text": "Invalid article format.", "source_urls": []}}
        
        if "summary" in response:
            required = RESPONSE_SCHEMA["properties"]["summary"]["required"]
            if not all(key in response["summary"] for key in required):
                logger.warning(f"Missing required fields in summary, preserving source_urls: {response['summary']}")
                response["summary"]["source_urls"] = response["summary"].get("source_urls", [])
                response["summary"]["summary_text"] = response["summary"].get("summary_text", "Partial summary due to missing content.")
        
        return response
    except Exception as e:
        logger.error(f"Error validating JSON response: {e}")
        return {"summary": {"summary_text": "Failed to process response.", "source_urls": []}}