import os

class Config:
    BASE_URL = "https://www.google.com/search"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36"
    ]
    FINANCIAL_BUSINESS_NEWS_DOMAINS = [
        "economictimes.indiatimes.com", "business-standard.com", "financialexpress.com",
        "livemint.com", "thehindubusinessline.com", "moneycontrol.com", "bloombergquint.com",
        "cnbctv18.com", "businesstoday.in", "forbesindia.com", "reuters.com", "bloomberg.com",
        "ft.com", "wsj.com", "cnbc.com", "marketwatch.com", "investing.com", "finance.yahoo.com",
        "seekingalpha.com", "businessinsider.com"
    ]
    SELECTORS = {
        "title": "div.n0jPhd",
        "url": "a.WlydOe",
        "description": "div.GI74Re",
        "date": "div.rbYSKb",
        "source": "div.NUnG9d"
    }
    PROXIES = os.getenv("PROXIES", "").split(",")
