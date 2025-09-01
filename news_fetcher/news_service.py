import logging
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from newsapi import NewsApiClient
import newspaper 
from newspaper import Article as NewspaperArticle, ArticleException
import os
import requests
from bs4 import BeautifulSoup

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
    days_back: int,
    sources: Optional[str],
    max_articles: int,
    language: str
) -> List[Article]:
    """
    Retrieve news articles based on the provided query and parameters.

    Args:
        query: Topic to search for.
        days_back: Number of past days to include in the search.
        sources: Comma-separated list of domains to search (optional).
        max_articles: Maximum number of articles to return.
        language: Language of the articles.

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for link in links:
        try:
            logger.info(f"Processing article with newspaper: {link}")
            article = NewspaperArticle(url=link, config=newspaper.Config())
            article.download()
            if article.download_state != 2:
                raise ArticleException(f"Download failed for {link}")
            article.parse()
            content = article.text or ""
            logger.info(f"Extracted {len(content)} characters from {link} with newspaper")
            truncated_content = content[:5000] + ("..." if len(content) > 5000 else "")
            content_list.append(ArticleContent(link=link, content=truncated_content))
        except (ArticleException, Exception) as e:
            logger.warning(f"Newspaper failed for {link}: {e}, trying BeautifulSoup fallback")
            try:
                response = requests.get(link, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                content = " ".join(p.get_text(strip=True) for p in paragraphs)
                logger.info(f"Extracted {len(content)} characters from {link} with BeautifulSoup")
                truncated_content = content[:5000] + ("..." if len(content) > 5000 else "")
                content_list.append(ArticleContent(link=link, content=truncated_content))
            except Exception as e2:
                logger.error(f"BeautifulSoup failed for {link}: {e2}")
                content_list.append(ArticleContent(link=link, content=""))
    return content_list