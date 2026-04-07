import pandas as pd
from urllib.parse import urlparse
from collections import defaultdict


CATEGORY_RULES = {
    "Social": ["facebook", "twitter", "instagram", "linkedin", "reddit", "tiktok", "snapchat", "pinterest", "tumblr", "discord", "telegram", "whatsapp", "threads"],
    "Video": ["youtube", "youtu.be", "netflix", "twitch", "vimeo", "dailymotion", "hotstar", "primevideo", "hulu", "disneyplus"],
    "Dev & Code": ["github", "gitlab", "stackoverflow", "leetcode", "codepen", "replit", "vercel", "netlify", "npmjs", "pypi", "docs.python", "developer.mozilla", "w3schools", "geeksforgeeks"],
    "News": ["bbc", "cnn", "reuters", "theguardian", "nytimes", "techcrunch", "theverge", "wired", "ycombinator", "medium", "substack", "thehindu", "ndtv", "timesofindia"],
    "Search": ["google", "bing", "duckduckgo", "yahoo", "baidu", "ecosia", "brave.com/search"],
    "Shopping": ["amazon", "flipkart", "ebay", "etsy", "walmart", "aliexpress", "meesho", "myntra", "ajio"],
    "Education": ["coursera", "udemy", "edx", "khanacademy", "brilliant", "wikipedia", "arxiv", "scholar.google", "researchgate"],
    "AI Tools": ["chat.openai", "claude.ai", "bard.google", "perplexity", "huggingface", "replicate", "midjourney", "gemini"],
    "Email": ["gmail", "outlook", "yahoo.com/mail", "mail.google", "protonmail"],
    "Work / Productivity": ["notion", "trello", "asana", "jira", "confluence", "slack", "zoom", "meet.google", "calendar.google", "drive.google", "docs.google"],
}


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def categorize_domain(domain: str) -> str:
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in domain:
                return category
    return "Other"


def build_stats(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["domain"] = df["url"].apply(extract_domain)
    df["category"] = df["domain"].apply(categorize_domain)
    df["visit_time"] = pd.to_datetime(df["visit_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["visit_time"])
    df["hour"] = df["visit_time"].dt.hour
    df["weekday"] = df["visit_time"].dt.day_name()
    df["date"] = df["visit_time"].dt.date

    # -- Summary --
    total_visits = len(df)
    unique_domains = df["domain"].nunique()
    date_range_start = str(df["visit_time"].min().date())
    date_range_end = str(df["visit_time"].max().date())
    top_site = df["domain"].value_counts().idxmax() if total_visits else ""
    peak_hour_val = df["hour"].value_counts().idxmax() if total_visits else 0
    peak_hour = f"{peak_hour_val:02d}:00"

    # -- Top sites --
    top_sites = (
        df["domain"]
        .value_counts()
        .head(10)
        .reset_index()
        .rename(columns={"domain": "site", "count": "visits"})
        .to_dict(orient="records")
    )

    # -- By hour (0-23) --
    by_hour = [0] * 24
    for hour, count in df["hour"].value_counts().items():
        by_hour[int(hour)] = int(count)

    # -- By weekday --
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = df["weekday"].value_counts().to_dict()
    by_weekday = [int(weekday_counts.get(d, 0)) for d in weekday_order]

    # -- Daily visits over time (last 60 days) --
    daily = df.groupby("date").size().reset_index(name="visits")
    daily["date"] = daily["date"].astype(str)
    daily = daily.sort_values("date").tail(60)
    by_date = daily.to_dict(orient="records")

    # -- Categories --
    cat_counts = df["category"].value_counts().to_dict()
    categories = [{"name": k, "value": int(v)} for k, v in cat_counts.items()]

    # -- Fun facts --
    busiest_day = daily.loc[daily["visits"].idxmax()] if not daily.empty else None
    first_visit_row = df.loc[df["visit_time"].idxmin()]
    last_visit_row = df.loc[df["visit_time"].idxmax()]

    # -- Search history analysis --
    search_df = df[df["domain"].str.contains("google|bing|duckduckgo|yahoo", na=False)]
    search_count = len(search_df)

    return {
        "summary": {
            "total_visits": int(total_visits),
            "unique_domains": int(unique_domains),
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
            "top_site": top_site,
            "peak_hour": peak_hour,
            "search_count": int(search_count),
            "busiest_day": str(busiest_day["date"]) if busiest_day is not None else "",
            "busiest_day_visits": int(busiest_day["visits"]) if busiest_day is not None else 0,
        },
        "first_visit": {
            "url": first_visit_row["url"],
            "title": str(first_visit_row.get("title", "")),
            "time": str(first_visit_row["visit_time"]),
        },
        "last_visit": {
            "url": last_visit_row["url"],
            "title": str(last_visit_row.get("title", "")),
            "time": str(last_visit_row["visit_time"]),
        },
        "top_sites": top_sites,
        "by_hour": by_hour,
        "by_weekday": {"labels": weekday_order, "data": by_weekday},
        "by_date": by_date,
        "categories": categories,
    }


def search_history(df: pd.DataFrame, query: str, limit: int = 50) -> list:
    df = df.copy()
    q = query.lower()
    mask = (
        df["url"].str.lower().str.contains(q, na=False) |
        df["title"].astype(str).str.lower().str.contains(q, na=False)
    )
    results = df[mask].head(limit)
    return results[["url", "title", "visit_time"]].assign(
        visit_time=results["visit_time"].astype(str)
    ).to_dict(orient="records")
