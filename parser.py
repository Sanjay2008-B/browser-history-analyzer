import sqlite3
import pandas as pd
import shutil
import os
from datetime import datetime, timezone


def detect_browser(filepath: str) -> str:
    """Detect browser type from SQLite schema."""
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    if "urls" in tables and "visits" in tables:
        return "chrome"
    elif "moz_places" in tables and "moz_historyvisits" in tables:
        return "firefox"
    else:
        raise ValueError("Unrecognized browser history format")


def parse_chrome(filepath: str) -> pd.DataFrame:
    """Parse Chrome/Edge history SQLite file."""
    # Copy to avoid lock issues if file is in use
    tmp = filepath + ".tmp"
    shutil.copy2(filepath, tmp)
    try:
        conn = sqlite3.connect(tmp)
        query = """
            SELECT
                u.url,
                u.title,
                u.visit_count,
                datetime(
                    (v.visit_time / 1000000) - 11644473600,
                    'unixepoch'
                ) AS visit_time
            FROM urls u
            JOIN visits v ON u.id = v.url
            ORDER BY v.visit_time DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
    finally:
        os.remove(tmp)

    df["visit_time"] = pd.to_datetime(df["visit_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["visit_time"])
    return df


def parse_firefox(filepath: str) -> pd.DataFrame:
    """Parse Firefox places.sqlite history file."""
    tmp = filepath + ".tmp"
    shutil.copy2(filepath, tmp)
    try:
        conn = sqlite3.connect(tmp)
        query = """
            SELECT
                p.url,
                p.title,
                p.visit_count,
                datetime(h.visit_date / 1000000, 'unixepoch') AS visit_time
            FROM moz_places p
            JOIN moz_historyvisits h ON p.id = h.place_id
            ORDER BY h.visit_date DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
    finally:
        os.remove(tmp)

    df["visit_time"] = pd.to_datetime(df["visit_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["visit_time"])
    return df


def parse_history(filepath: str) -> tuple[pd.DataFrame, str]:
    """Auto-detect and parse browser history. Returns (dataframe, browser_name)."""
    browser = detect_browser(filepath)
    if browser == "chrome":
        df = parse_chrome(filepath)
    elif browser == "firefox":
        df = parse_firefox(filepath)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    return df, browser
