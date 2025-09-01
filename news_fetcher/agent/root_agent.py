from google.adk.agents import Agent
from ..news_service import fetch_articles, extract_article_content
from ..config import INSTRUCTIONS

# Agent configuration
NEWS_MODEL = "gemini-2.5-flash-preview-05-20"
root_agent = Agent(
    model=NEWS_MODEL,
    name="root_agent",
    description="Fetches and summarizes news articles based on user queries.",
    instruction=INSTRUCTIONS,
    tools=[fetch_articles, extract_article_content]
)
