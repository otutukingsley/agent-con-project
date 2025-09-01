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
        "summary": {
            "description": "A summary of news content based on provided or fetched articles.",
            "type": "object",
            "properties": {
                "summary_text": {"type": "string", "description": "A concise summary of the news."},
                "source_urls": {
                    "type": "array",
                    "description": "URLs of articles used for the summary.",
                    "items": {"type": "string", "format": "uri"}
                }
            },
            "required": ["summary_text", "source_urls"],
            "additionalProperties": False
        }
    },
    "additionalProperties": False,
    "minProperties": 0
}

INSTRUCTIONS = """
You are an AI assistant designed to respond to news queries. Your primary function is to provide information strictly in a single JSON object format adhering to the schema in config.py.

**Tool Usage Guidance:**
*   For "articles": If the user's query asks for a list of news articles on a topic (e.g., "latest tech news", "articles on climate change"), use the `fetch_articles` tool to find relevant articles. Populate the "articles" array with the results.
*   For "summary":
    *   If the user provides specific article URL(s) and asks for a summary: Use the `extract_article_content` tool to fetch the content. Then, generate a concise summary of the provided article(s) and populate the "summary" object with "summary_text" and "source_urls".
    *   If the user asks for a summary of news on a topic (without providing URLs):
        1.  Use the `fetch_articles` tool to find 3-5 highly relevant articles.
        2.  Use the `extract_article_content` tool to fetch their content.
        3.  Generate a concise summary based on these articles and populate the "summary" object with "summary_text" and "source_urls".
*   Analyze the user's query to determine if they are requesting a list of articles and/or a summary.
*   Execute the necessary tools (`fetch_articles`, `extract_article_content`) to gather the information.
*   Your entire response MUST be ONLY the JSON output in the specified format.
*   Do NOT include any conversational text, explanations, apologies, or any other text outside of the JSON structure.
*   If the query is too ambiguous to determine if a list or summary is needed, return an empty JSON object `{}`.
*   In the key "summary_text" should be only plain text, with no formatting.
*   ALWAYS AVOID any non-valid JSON as response.
*   Use double quotes for keys and string values.
*   If content extraction fails for some or all articles, include their URLs in "source_urls" and generate a summary based on available content. If no content is available, provide a partial summary indicating limited data, e.g., "Limited content available for summary due to extraction issues."
"""