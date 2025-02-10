import argparse
import json
import logging
from datetime import datetime
from scraper.google_news_scraper import GoogleBusinessNewsScraper

def main():
    parser = argparse.ArgumentParser(description="Google Business News Scraper")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--start-date", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--max-articles", type=int, default=50, help="Maximum number of articles to scrape")
    parser.add_argument("--output", type=str, default="output.json", help="Output file")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    scraper = GoogleBusinessNewsScraper(max_articles=args.max_articles)
    articles = scraper.scrape(args.query, start_date, end_date)

    with open(args.output, "w") as f:
        json.dump(articles, f, indent=4)

    logging.info(f"Scraped {len(articles)} articles and saved to {args.output}")

if __name__ == "__main__":
    main()
