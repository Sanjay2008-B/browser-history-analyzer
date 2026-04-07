# 🗂 Browser History Analyzer

Analyze your Chrome, Edge, or Firefox browsing history locally.
**No data leaves your machine.**

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
cd backend
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## How to get your history file

### Chrome / Edge
- **Windows:** `C:\Users\<you>\AppData\Local\Google\Chrome\User Data\Default\History`
- **macOS:** `~/Library/Application Support/Google/Chrome/Default/History`
- **Linux:** `~/.config/google-chrome/Default/History`

> ⚠️ Close Chrome/Edge before copying the file (it will be locked while open)

### Firefox
- **Windows:** `C:\Users\<you>\AppData\Roaming\Mozilla\Firefox\Profiles\<profile>\places.sqlite`
- **macOS:** `~/Library/Application Support/Firefox/Profiles/<profile>/places.sqlite`
- **Linux:** `~/.mozilla/firefox/<profile>/places.sqlite`

---

## Features

- **Overview** — summary stats: total visits, unique sites, peak hour, top site
- **Charts** — visits by hour, weekday, and daily timeline
- **Top Sites** — ranked list of most visited domains
- **Search** — full-text search through your history
- **Fun Facts** — first visit, busiest day, history span, and more

---

## Tech Stack

| Layer     | Tech                         |
|-----------|------------------------------|
| Backend   | Python + Flask               |
| Parsing   | sqlite3 (built-in)           |
| Analysis  | pandas                       |
| Frontend  | HTML + CSS + JavaScript      |
| Charts    | Chart.js                     |
