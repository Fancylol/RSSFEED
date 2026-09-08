import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
import html

FEEDS = [
    {
        "name": "Quelle 1",
        "url": "http://www.cash.ch/rss/450.xml"
    },
    {
        "name": "Quelle 2",
        "url": "http://www.cash.ch/rss/771.xml"
    },
    {
        "name": "Quelle 3",
        "url": "https://www.handelsblatt.com/contentexport/feed/finanzen"
    },
    {
        "name": "Quelle 4",
        "url": "https://www.handelsblatt.com/contentexport/feed/marktberichte"
    }
]

articles = []

for source in FEEDS:
    feed = feedparser.parse(source["url"])

    for entry in feed.entries[:15]:

        date = None

        if hasattr(entry, "published"):
            try:
                date = parsedate_to_datetime(entry.published)
            except:
                pass

        if date is None:
            date = datetime.min

        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", "#"),
            "description": entry.get("summary", ""),
            "source": source["name"],
            "date": date
        })

articles.sort(
    key=lambda x: x["date"],
    reverse=True
)

articles = articles[:30]

cards = ""

for article in articles:

    date_text = ""

    if article["date"] != datetime.min:
        date_text = article["date"].strftime("%d.%m.%Y %H:%M")

    description = article["description"]

    # Beschreibung etwas begrenzen
    if len(description) > 400:
        description = description[:400] + "..."

    cards += f"""
    <article class="news-card">

        <div class="meta">
            {html.escape(article["source"])}
            <span>·</span>
            {date_text}
        </div>

        <h2>
            <a href="{html.escape(article["link"])}"
               target="_blank"
               rel="noopener">
                {html.escape(article["title"])}
            </a>
        </h2>

        <div class="description">
            {description}
        </div>

        <a class="more"
           href="{html.escape(article["link"])}"
           target="_blank"
           rel="noopener">
            Artikel öffnen →
        </a>

    </article>
    """

page = f"""
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>News</title>

<style>

body {{
    margin: 0;
    padding: 20px;
    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    background: #ffffff;
    color: #242424;
}}

.feed {{
    max-width: 1000px;
    margin: 0 auto;
}}

.news-card {{
    padding: 20px 0;
    border-bottom: 1px solid #e1e1e1;
}}

.news-card:first-child {{
    padding-top: 0;
}}

.meta {{
    font-size: 13px;
    color: #616161;
    margin-bottom: 6px;
}}

.meta span {{
    margin: 0 5px;
}}

h2 {{
    font-size: 20px;
    line-height: 1.3;
    margin: 0 0 10px 0;
    font-weight: 600;
}}

h2 a {{
    color: #242424;
    text-decoration: none;
}}

h2 a:hover {{
    text-decoration: underline;
}}

.description {{
    font-size: 15px;
    line-height: 1.5;
    color: #424242;
}}

.more {{
    display: inline-block;
    margin-top: 10px;
    color: #0067b8;
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
}}

.more:hover {{
    text-decoration: underline;
}}

</style>

</head>

<body>

<div class="feed">

{cards}

</div>

</body>

</html>
"""

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(page)

print(
    f"{len(articles)} Artikel verarbeitet."
)