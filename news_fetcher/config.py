# Configuration for the news fetcher, including the response schema and instructions.

RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "News Fetcher Response",
    "description": "Defines the structure for responses from the news fetcher, including article lists or summaries.",
    "type": "object",
    "properties": {
        "articles": {
            "description": "List of news articles matching the query.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "headline": {"type": "string", "description": "The headline of the article."},
                    "link": {"type": "string", "format": "uri", "description": "The article's URL."},
                    "summary": {"type": "string", "description": "A short summary of the article (optional)."},
                    "publisher": {"type": "string", "description": "The name of the article's publisher."}
                },
                "required": ["headline", "link", "publisher"],
                "additionalProperties": False
            }
        },
        "overview": {
            "description": "A summary of news content based on provided or fetched articles.",
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "A concise summary of the news."},
                "sources": {
                    "type": "array",
                    "description": "URLs of articles used for the summary.",
                    "items": {"type": "string", "format": "uri"}
                }
            },
            "required": ["text", "sources"],
            "additionalProperties": False
        }
    },
    "additionalProperties": False,
    "minProperties": 0
}

INSTRUCTIONS = """
You are a news retrieval assistant tasked with providing news-related information in a structured JSON format. Your response must always be a single JSON object adhering to the defined schema.

**How to Process Queries:**
- If the user requests a list of news articles (e.g., 'recent AI news' or 'climate change articles'), use the `fetch_articles` tool to retrieve relevant articles and populate the 'articles' field.
- If the user asks for a summary:
  - For specific URLs provided by the user, use the `extract_article_content` tool to fetch content and generate a summary for the 'overview' field.
  - For a topic-based summary without URLs, use `fetch_articles` to get 3-5 relevant articles, then use `extract_article_content` to retrieve their content and generate a summary for the 'overview' field.
- If the query is unclear or doesn't specify a list or summary, return an empty JSON object `{}`.
- Ensure all responses are valid JSON, use double quotes for keys and strings, and include only plain text in the 'text' field of the 'overview' object.
"""