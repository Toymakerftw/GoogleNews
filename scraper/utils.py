import random
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional

def get_random_delay() -> float:
    """Generate a longer random delay between requests to avoid detection."""
    return random.uniform(5, 15)

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Convert relative date strings to YYYY-MM-DD format."""
    if not date_str:
        return None

    date_str = date_str.lower().strip()
    today = datetime.today()

    try:
        if "ago" in date_str:
            date_str = date_str.replace("ago", "").strip()

        if "hour" in date_str or "minute" in date_str or "second" in date_str:
            return today.strftime("%Y-%m-%d")

        if "day" in date_str:
            days = int(date_str.split()[0])
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")

        if "week" in date_str:
            weeks = int(date_str.split()[0])
            return (today - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

        if "month" in date_str:
            months = int(date_str.split()[0])
            return (today - relativedelta(months=months)).strftime("%Y-%m-%d")

        if "year" in date_str:
            years = int(date_str.split()[0])
            return (today - relativedelta(years=years)).strftime("%Y-%m-%d")

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, "%d %B %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

    except Exception as e:
        print(f"Failed to parse date '{date_str}': {e}")

    return None
