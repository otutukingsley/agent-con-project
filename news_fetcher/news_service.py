import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any  # Added Dict and Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from newsapi import NewsApiClient
from newspaper import Article, ArticleException
import os

from .config import RESPONSE_SCHEMA
from .core import validate_json_response, simple_summarize

# Custom logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

class Article(BaseModel):
    headline: str = Field(description="The headline of the news article.")
    link: str = Field(description="The URL of the news article.")
    summary: Optional[str] = Field(description="A brief summary of the news article.")
    publisher: str = Field(description="The name of the article's publisher.")

class ArticleContent(BaseModel):
    link: str = Field(description="The URL of the news article.")
    content: Optional[str] = Field(description="The first 5000 characters of the article's content.")

def fetch_articles(
    query: str,
    days_back: int = 7,
    sources: Optional[str] = None,
    max_articles: int = 30,
    language: str = "en"
) -> List[Article]:
    """
    Retrieve news articles based on the provided query and parameters.

    Args:
        query: Topic to search for.
        days_back: Number of past days to include in the search.
        sources: Comma-separated list of domains to search (optional).
        max_articles: Maximum number of articles to return.
        language: Language of the articles (default: 'en').

    Returns:
        List of Article objects containing headline, link, summary, and publisher.
    """
    try:
        news_client = NewsApiClient(api_key=NEWS_API_KEY)
        from_date = datetime.now() - timedelta(days=days_back)
        response = news_client.get_everything(
            q=query,
            from_param=from_date.strftime("%Y-%m-%d"),
            domains=sources,
            language=language,
            sort_by="relevancy",
            page_size=max_articles
        )
        articles = response.get("articles", [])
        logger.info(f"Fetched {len(articles)} articles for query: {query}")
        return [
            Article(
                headline=article.get("title", ""),
                link=article.get("url", ""),
                summary=article.get("description", None),
                publisher=article.get("source", {}).get("name", "Unknown")
            )
            for article in articles
            if article.get("title") and article.get("url")
        ][:max_articles]
    except Exception as e:
        logger.error(f"Error fetching articles for query {query}: {e}")
        return []

def extract_article_content(links: List[str]) -> List[ArticleContent]:
    """
    Extract the main content of articles from a list of URLs.

    Args:
        links: List of URLs to fetch and parse.

    Returns:
        List of ArticleContent objects with the URL and extracted content (or empty string if failed).
    """
    content_list = []
    for link in links:
        try:
            logger.info(f"Processing article: {link}")
            article = Article(link)
            article.download()
            if article.download_state != 2:
                raise ArticleException(f"Download failed for {link}")
            article.parse()
            content = article.text or ""
            logger.info(f"Extracted {len(content)} characters from {link}")
            truncated_content = content[:5000] + ("..." if len(content) > 5000 else "")
            content_list.append(ArticleContent(link=link, content=truncated_content))
        except ArticleException as e:
            logger.warning(f"Failed to process article {link}: {e}")
            content_list.append(ArticleContent(link=link, content=""))
        except Exception as e:
            logger.error(f"Unexpected error for {link}: {e}")
            content_list.append(ArticleContent(link=link, content=""))
    return content_list

def generate_topic_summary(query: str) -> Dict[str, Any]:
    """
    Generate a summary for a topic by fetching and summarizing articles.

    Args:
        query: Topic to summarize.

    Returns:
        JSON response with an 'overview' field containing the summary and source URLs.
    """
    try:
        articles = fetch_articles(query, max_articles=5)
        article_urls = [article.link for article in articles]
        contents = extract_article_content(article_urls)
        summary_text = simple_summarize(
            [{"content": content.content} for content in contents]
        )
        response = {
            "overview": {
                "text": summary_text,
                "sources": article_urls
            }
        }
        return validate_json_response(response)
    except Exception as e:
        logger.error(f"Error generating summary for query {query}: {e}")
        return {}

