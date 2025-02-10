import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs
from math import ceil
from typing import List, Dict, Optional
import logging
from .config import Config
from .utils import get_random_delay, parse_date
from datetime import datetime
import time
import random

class GoogleBusinessNewsScraper:
    def __init__(self, max_articles: int = 50, max_retries: int = 3):
        self.config = Config()
        self.article_per_pages = 100
        self.max_pages = ceil(max_articles / self.article_per_pages)
        self.max_articles = max_articles
        self.max_retries = max_retries
        self.proxies = [{"http": proxy} for proxy in self.config.PROXIES if proxy]

    def construct_url(self, query: str, start_date: datetime, end_date: datetime, page: int = 0, hl: str = "en", lr: str = "lang_en", num: int = None, sort_by_date: bool = False) -> str:
        if num is None:
            num = self.article_per_pages

        date_filter = f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
        tbs_parts = [date_filter]

        if sort_by_date:
            tbs_parts.append("sbd:1")

        params = {
            "q": quote(query + " " + " OR ".join([f'site:{x}' for x in self.config.FINANCIAL_BUSINESS_NEWS_DOMAINS])),
            "tbm": "nws",
            "tbs": ",".join(tbs_parts),
            "start": page * num,
            "hl": hl,
            "lr": lr,
            "num": str(num),
        }

        return f"{self.config.BASE_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.config.USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def is_captcha_page(self, html: str) -> bool:
        return "Our systems have detected unusual traffic" in html

    def extract_articles(self, html: str) -> List[Dict[str, Optional[str]]]:
        soup = BeautifulSoup(html, "lxml")
        articles = []

        for container in soup.find_all("div", class_="SoaBEf"):
            article = {
                "title": self._safe_extract(container, self.config.SELECTORS["title"], "text"),
                "url": self._clean_url(self._safe_extract(container, self.config.SELECTORS["url"], "href")),
                "source": self._safe_extract(container, self.config.SELECTORS["source"], "text"),
                "date": parse_date(self._safe_extract(container, self.config.SELECTORS["date"], "text")),
                "description": self._safe_extract(container, self.config.SELECTORS["description"], "text"),
            }

            if article["url"]:
                articles.append(article)

        return articles

    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        if url and url.startswith("/url?"):
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            return qs.get("q", [url])[0]
        return url

    def _safe_extract(self, parent, selector: str, attr: str) -> Optional[str]:
        try:
            element = parent.select_one(selector)
            if not element:
                return None
            if attr == "text":
                return element.get_text().strip()
            return element.get(attr, "")
        except Exception as e:
            logging.error(f"Failed to extract {selector}: {e}")
            return None

    def scrape(self, query: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Optional[str]]]:
        all_articles = []

        for page in range(self.max_pages):
            if len(all_articles) >= self.max_articles:
                logging.info(f"Reached article limit ({self.max_articles}). Stopping.")
                break

            time.sleep(get_random_delay())
            url = self.construct_url(query, start_date, end_date, page)

            retries = 0
            while retries < self.max_retries:
                try:
                    logging.info(f"Fetching page {page + 1}: {url}")
                    response = requests.get(
                        url,
                        headers=self.get_headers(),
                        proxies=random.choice(self.proxies) if self.proxies else None,
                        timeout=30,
                    )
                    response.raise_for_status()

                    if self.is_captcha_page(response.text):
                        logging.error("CAPTCHA detected. Stopping scraping.")
                        return all_articles

                    articles = self.extract_articles(response.text)
                    if not articles:
                        logging.info("No more articles found. Stopping.")
                        return all_articles

                    all_articles.extend(articles)
                    logging.info(f"Page {page + 1}: Added {self.max_articles - (page * self.article_per_pages) if page == self.max_pages - 1 else self.article_per_pages} articles")
                    break

                except requests.exceptions.RequestException as e:
                    retries += 1
                    logging.error(f"Request failed (attempt {retries}/{self.max_retries}): {e}")
                    if retries < self.max_retries:
                        time.sleep(2 ** retries)
                    else:
                        logging.error("Max retries reached. Stopping.")
                        return all_articles

        return all_articles[:self.max_articles]
