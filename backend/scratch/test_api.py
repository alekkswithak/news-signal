import asyncio
from app.services.news_service import search_articles
from app.services.ai_service import analyze_article
from app.config import settings

async def main():
    print("Testing GNews search for 'renewable energy'...")
    try:
        articles = await search_articles("renewable energy", max_results=3)
        print(f"GNews returned {len(articles)} articles:")
        for idx, article in enumerate(articles):
            print(f"{idx + 1}. {article.title} ({article.url})")
            print(f"   Description: {article.description}")
        
        if articles:
            test_article = articles[0]
            print("\nTesting OpenAI article analysis...")
            analysis = await analyze_article(test_article.title, test_article.description)
            print("Analysis result:")
            print(analysis)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
