import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import html
import re


# ============================================================
# RSS-FEEDS
# ============================================================

FEEDS = [
    {
        "name": "Cash Börse",
        "url": "http://www.cash.ch/rss/450.xml"
    },
    {
        "name": "Cash Top-News",
        "url": "http://www.cash.ch/rss/771.xml"
    },
    {
        "name": "Finanzen.ch News",
        "url": "https://www.finanzen.ch/rss/news"
    },
    {
        "name": "Finanzen.ch Analysen",
        "url": "https://www.finanzen.ch/rss/analysen"
    },
    {
        "name": "Handelsblatt Finanzen",
        "url": "https://www.handelsblatt.com/contentexport/feed/finanzen"
    },
    {
        "name": "Handelsblatt Marktberichte",
        "url": "https://www.handelsblatt.com/contentexport/feed/marktberichte"
    }
]


# ============================================================
# EINSTELLUNGEN
# ============================================================

# Maximale Anzahl Artikel pro RSS-Feed
ARTICLES_PER_FEED = 20

# Maximale Anzahl Artikel auf der fertigen Seite
MAX_ARTICLES = 30

# Maximale Länge der Beschreibung
DESCRIPTION_LENGTH = 180


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def clean_text(text):
    """
    Entfernt HTML-Tags und bereinigt RSS-Texte.
    """

    if not text:
        return ""

    # HTML-Tags entfernen
    text = re.sub(r"<[^>]+>", " ", text)

    # HTML-Entities umwandeln
    text = html.unescape(text)

    # Mehrfache Leerzeichen entfernen
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def shorten(text, length=180):
    """
    Kürzt die Beschreibung auf eine maximale Länge.
    """

    if not text:
        return ""

    if len(text) <= length:
        return text

    shortened = text[:length]

    # Möglichst nicht mitten in einem Wort abschneiden
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]

    return shortened + "..."


def get_date(entry):
    """
    Versucht das Publikationsdatum aus verschiedenen
    RSS-Feldern auszulesen.
    """

    for field in [
        "published",
        "updated",
        "created"
    ]:

        value = entry.get(field)

        if value:

            try:

                date = parsedate_to_datetime(value)

                if date.tzinfo is None:
                    date = date.replace(
                        tzinfo=timezone.utc
                    )

                return date

            except Exception:
                pass

    # Falls kein Datum vorhanden ist
    return datetime.min.replace(
        tzinfo=timezone.utc
    )


# ============================================================
# RSS-FEEDS EINLESEN
# ============================================================

articles = []

for source in FEEDS:

    print(
        f"Lade RSS-Feed: {source['name']}"
    )

    feed = feedparser.parse(
        source["url"]
    )

    if feed.bozo:

        print(
            f"Warnung bei {source['name']}: "
            f"{feed.bozo_exception}"
        )

    print(
        f"{len(feed.entries)} Einträge gefunden."
    )

    for entry in feed.entries[:ARTICLES_PER_FEED]:

        title = clean_text(
            entry.get(
                "title",
                ""
            )
        )

        description = clean_text(
            entry.get(
                "summary",
                entry.get(
                    "description",
                    ""
                )
            )
        )

        link = entry.get(
            "link",
            "#"
        )

        date = get_date(entry)

        # Artikel ohne Titel überspringen
        if not title:
            continue

        articles.append({
            "title": title,
            "description": description,
            "link": link,
            "date": date,
            "source": source["name"]
        })


# ============================================================
# DUPLIKATE ENTFERNEN
# ============================================================

unique_articles = []

seen_links = set()
seen_titles = set()

for article in articles:

    link = article[
        "link"
    ].strip().lower()

    title = article[
        "title"
    ].strip().lower()

    # Bereits vorhandene URL
    if link and link != "#":

        if link in seen_links:
            continue

    # Bereits vorhandener Titel
    if title in seen_titles:
        continue

    if link and link != "#":
        seen_links.add(link)

    seen_titles.add(title)

    unique_articles.append(
        article
    )


articles = unique_articles


# ============================================================
# NACH DATUM SORTIEREN
# ============================================================

articles.sort(
    key=lambda article: article["date"],
    reverse=True
)


# Maximale Anzahl Beiträge
articles = articles[:MAX_ARTICLES]


# ============================================================
# HTML FÜR ARTIKEL ERZEUGEN
# ============================================================

items_html = ""


for article in articles:

    title = html.escape(
        article["title"]
    )

    description = html.escape(
        shorten(
            article["description"],
            DESCRIPTION_LENGTH
        )
    )

    link = html.escape(
        article["link"],
        quote=True
    )

    source = html.escape(
        article["source"]
    )


    # Datum formatieren

    if article["date"].year > 1900:

        date_text = article[
            "date"
        ].strftime(
            "%d.%m.%Y"
        )

    else:

        date_text = ""


    # Datum + Quelle

    meta_parts = []

    if date_text:
        meta_parts.append(
            date_text
        )

    if source:
        meta_parts.append(
            source
        )

    meta_text = " · ".join(
        meta_parts
    )


    # Einzelnen Artikel erzeugen

    items_html += f"""
    <article class="singleCard">

        <a
            class="primaryText"
            href="{link}"
            target="_blank"
            rel="noopener noreferrer"
        >
            {title}
        </a>

        <div class="secondaryText">
            {description}
        </div>

        <div class="dateText">
            {meta_text}
        </div>

    </article>
    """


# ============================================================
# FALLS KEINE ARTIKEL GEFUNDEN WURDEN
# ============================================================

if not articles:

    items_html = """
    <div class="noArticles">
        Aktuell sind keine Meldungen verfügbar.
    </div>
    """


# ============================================================
# KOMPLETTE HTML-SEITE
# ============================================================

page = f"""<!DOCTYPE html>

<html lang="de">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Finanz-News</title>


<style>


    /* ==========================================
       BASIS
       ========================================== */

    * {{
        box-sizing: border-box;
    }}


    html {{
        margin: 0;
        padding: 0;

        background: transparent;
    }}


    body {{

        margin: 0;
        padding: 0;

        background: transparent;

        font-family:
            "Segoe UI",
            "Segoe UI Web (West European)",
            -apple-system,
            BlinkMacSystemFont,
            Roboto,
            "Helvetica Neue",
            Arial,
            sans-serif;

        color: #242424;

    }}


    /* ==========================================
       HAUPTBEREICH
       ========================================== */

    .template_root {{

        width: 100%;

        margin: 0;
        padding: 0;

        font-family: inherit;

        color: #242424;

    }}


    /* ==========================================
       EINZELNER ARTIKEL
       ========================================== */

    .singleCard {{

        display: block;

        margin:
            0
            0
            20px
            0;

        padding: 0;

        background: transparent;

        border: none;

        box-shadow: none;

    }}


    /* ==========================================
       ARTIKELTITEL
       ========================================== */

    .primaryText {{

        display: block;

        margin:
            0
            0
            6px
            0;

        padding: 0;

        font-family: inherit;

        font-size: 14px;

        line-height: 20px;

        font-weight: 600;

        color: #242424;

        text-decoration: none;

        overflow-wrap: anywhere;

    }}


    .primaryText:link,
    .primaryText:visited {{

        color: #242424;

        text-decoration: none;

    }}


    .primaryText:hover {{

        color: #242424;

        text-decoration: underline;

    }}


    /* ==========================================
       BESCHREIBUNG
       ========================================== */

    .secondaryText {{

        display: block;

        margin:
            0
            0
            6px
            0;

        padding: 0;

        font-family: inherit;

        font-size: 14px;

        line-height: 20px;

        font-weight: 400;

        color: #242424;

        overflow-wrap: anywhere;

    }}


    /* ==========================================
       DATUM + QUELLE
       ========================================== */

    .dateText {{

        display: block;

        margin: 0;

        padding: 0;

        font-family: inherit;

        font-size: 12px;

        line-height: 16px;

        font-weight: 400;

        color: #605e5c;

    }}


    /* ==========================================
       KEINE ARTIKEL
       ========================================== */

    .noArticles {{

        font-family: inherit;

        font-size: 14px;

        line-height: 20px;

        color: #605e5c;

    }}


</style>

</head>


<body>


<div class="template_root">

    {items_html}

</div>


</body>

</html>
"""


# ============================================================
# INDEX.HTML SPEICHERN
# ============================================================

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(page)


# ============================================================
# STATUS
# ============================================================

print()
print(
    f"Fertig: {len(articles)} Artikel veröffentlicht."
)
print(
    f"Verwendete RSS-Feeds: {len(FEEDS)}"
)