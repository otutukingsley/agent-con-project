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
        A validated JSON response, or an empty dict if invalid.
    """
    try:
        # Basic validation: ensure response is a dict with valid keys
        if not isinstance(response, dict):
            logger.error("Response is not a dictionary")
            return {}

        valid_keys = RESPONSE_SCHEMA["properties"].keys()
        if not all(key in valid_keys for key in response):
            logger.error(f"Invalid keys in response: {response.keys()}")
            return {}

        # Validate articles if present
        if "articles" in response:
            for article in response["articles"]:
                required = RESPONSE_SCHEMA["properties"]["articles"]["items"]["required"]
                if not all(key in article for key in required):
                    logger.error(f"Invalid article format: {article}")
                    return {}

        # Validate overview if present
        if "overview" in response:
            required = RESPONSE_SCHEMA["properties"]["overview"]["required"]
            if not all(key in response["overview"] for key in required):
                logger.error(f"Invalid overview format: {response['overview']}")
                return {}

        return response
    except Exception as e:
        logger.error(f"Error validating JSON response: {e}")
        return {}

def simple_summarize(articles: List[Dict[str, str]], max_length: int = 200) -> str:
    """
    Generate a simple summary by extracting key sentences from article content.

    Args:
        articles: List of articles with 'content' field.
        max_length: Maximum length of the summary in characters.

    Returns:
        A plain text summary.
    """
    try:
        combined_text = " ".join(article.get("content", "") for article in articles if article.get("content"))
        if not combined_text:
            return "No content available for summary."

        # Simple sentence extraction: take first few sentences
        sentences = re.split(r"(?<=[.!?])\s+", combined_text.strip())
        summary = " ".join(sentences[:3]).strip()[:max_length]
        return summary + ("..." if len(summary) == max_length else "")
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Failed to generate summary."