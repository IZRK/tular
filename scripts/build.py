"""Render readable, bilingual static pages from the curated content directory.

This build is offline. It does not crawl the old website or rewrite source content.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from seo import page_metadata, structured_data, write_crawl_files

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


NAVIGATION = load_json("content/navigation.json")
PAGES = NAVIGATION["pages"]
TITLES = NAVIGATION["titles"]
HOME = load_json("content/home.json")
REFERENCES = load_json("content/references.json")
ASSETS = load_json("content/assets.json")
PAGE_INTROS = load_json("content/page-intros.json")

COPY = {
    "en": {
        "laboratory": "Cave Laboratory",
        "skip": "Skip to content",
        "menu": "Menu",
        "navigation": "Main navigation",
        "rescue_title": "Found a proteus outside a cave?",
        "rescue_text": "Call the rescue line as soon as possible.",
        "rescue_link": "About the rescue programme",
        "hero_title": "A world without light.",
        "hero_intro": "Researching an extraordinary animal. Protecting the water we share.",
        "hero_body": "Tular Cave Laboratory, Kranj, Slovenia. Research and conservation of proteus since 1960.",
        "meet": "Meet the olm",
        "about": "Inside the laboratory",
        "explore": "Discover Tular",
        "film": "See the world of proteus",
        "watch": "Watch the film",
        "new": "New perspectives",
        "research_intro": "Publications, field observations and new methods for understanding life underground.",
        "media_intro": "Reporting, films and conversations about proteus and its protection.",
        "archive": "Publication archive",
        "search": "Search publications",
        "search_media": "Search the media archive",
        "placeholder": "Title, author or keyword",
        "year": "Year",
        "all_years": "All years",
        "reset": "Clear filters",
        "results": "entries",
        "details": "Affiliations and additional details",
        "publisher": "Read publication",
        "media_publisher": "Open source",
        "pdf": "Open PDF",
        "search_link": "Find this source",
        "archive_link": "Find archived copy",
        "archive_note": "The original link is unavailable. Search for a saved copy in the Internet Archive.",
        "no_results": "No entries match. Try another term or clear the filters.",
        "source_context": "Original project and laboratory records. Dates and historical terminology are retained.",
        "society": "Society for Cave Biology",
        "mission": "Research and conservation of proteus.",
        "contact_intro": "Contact the laboratory, discuss research or report an olm in need of rescue.",
        "related": "Explore this section",
        "related_research": "Recent research and collaborations",
        "copy": "Copy citation",
        "copied": "Citation copied",
        "copy_failed": "Could not copy. Select and copy the citation text below.",
    },
    "sl": {
        "laboratory": "Jamski laboratorij",
        "skip": "Preskoči na vsebino",
        "menu": "Meni",
        "navigation": "Glavna navigacija",
        "rescue_title": "Ste našli človeško ribico izven jame?",
        "rescue_text": "Čim prej pokličite dežurni telefon zatočišča.",
        "rescue_link": "O reševanju človeških ribic",
        "hero_title": "Svet brez svetlobe.",
        "hero_intro": "Raziskujemo izjemno žival. Varujemo vodo, ki si jo delimo.",
        "hero_body": "Jamski laboratorij Tular, Kranj, Slovenija. Raziskovanje in varstvo človeške ribice od leta 1960.",
        "meet": "Spoznajte človeško ribico",
        "about": "V jamskem laboratoriju",
        "explore": "Spoznajte Tular",
        "film": "Oglejte si svet proteusa",
        "watch": "Ogled filma",
        "new": "Novi pogledi",
        "research_intro": "Objave, terenska opazovanja in nove metode za razumevanje življenja v podzemlju.",
        "media_intro": "Prispevki, filmi in pogovori o človeški ribici in njenem varstvu.",
        "archive": "Arhiv objav",
        "search": "Iskanje po objavah",
        "search_media": "Iskanje po medijskem arhivu",
        "placeholder": "Naslov, avtor ali ključna beseda",
        "year": "Leto",
        "all_years": "Vsa leta",
        "reset": "Počisti filtre",
        "results": "objav",
        "details": "Ustanove in dodatni podatki",
        "publisher": "Preberi objavo",
        "media_publisher": "Odpri vir",
        "pdf": "Odpri PDF",
        "search_link": "Poišči vir",
        "archive_link": "Poišči arhivsko kopijo",
        "archive_note": "Izvirna povezava ni na voljo. Poiščite shranjeno kopijo v Internet Archive.",
        "no_results": "Ni zadetkov. Poskusite drug izraz ali počistite filtre.",
        "source_context": "Izvirni zapisi o projektih in laboratoriju. Datumi in zgodovinsko izrazje so ohranjeni.",
        "society": "Društvo za jamsko biologijo",
        "mission": "Raziskovanje in varstvo človeške ribice.",
        "contact_intro": "Pišite laboratoriju, povežite se z raziskovalci ali sporočite najdbo človeške ribice.",
        "related": "Več v tej rubriki",
        "related_research": "Novejše raziskave in sodelovanja",
        "copy": "Kopiraj navedbo",
        "copied": "Navedba je kopirana",
        "copy_failed": "Kopiranje ni uspelo. Označite in kopirajte spodnjo navedbo.",
    },
}


def route(key: str, language: str) -> str:
    prefix = "sl/" if language == "sl" else ""
    return prefix + ("index.html" if key == "home" else key + ".html")


def local_url(target: str, current_page: str) -> str:
    """Resolve logical root paths while preserving external URLs and fragments."""
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return target
    path = parsed.path.lstrip("/")
    directory = path.endswith("/") or path.endswith("index.html") or not path
    if path.endswith("index.html"):
        path = path.removesuffix("index.html")
    relative = os.path.relpath(path or ".", Path(current_page).parent).replace(
        os.sep, "/"
    )
    if directory:
        relative = "./" if relative == "." else relative.rstrip("/") + "/"
    return urlunsplit(("", "", relative, parsed.query, parsed.fragment))


def asset_path(name: str) -> str:
    for source, item in ASSETS.items():
        if item and name in source:
            return item["path"]
    raise ValueError(f"Unknown source asset: {name}")


def render_fragment(key: str, language: str, current_page: str) -> Markup:
    path = ROOT / "content" / "articles" / language / f"{key}.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for index, heading in enumerate(soup.select("article > h2, article > h3"), 1):
        heading["id"] = f"section-{index}"
    for node in soup.select("[href], [src]"):
        attribute = "href" if node.has_attr("href") else "src"
        node[attribute] = local_url(node[attribute], current_page)
    return Markup(str(soup))


def article_toc(key: str, language: str) -> list[dict]:
    path = ROOT / "content" / "articles" / language / f"{key}.html"
    if not path.exists():
        return []
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    return [
        {"id": f"section-{index}", "title": heading.get_text(" ", strip=True)}
        for index, heading in enumerate(soup.select("article > h2, article > h3"), 1)
    ]


def build_page(page: dict, environment: Environment) -> None:
    key = page["key"]
    language = page["language"]
    current_page = page["route"]
    other_language = "en" if language == "sl" else "sl"
    entries = (
        load_json(f"content/{key}-{language}.json")
        if key in ("research", "media")
        else []
    )
    years = sorted({entry["year"] for entry in entries}, reverse=True)
    groups = [
        {"year": year, "entries": [entry for entry in entries if entry["year"] == year]}
        for year in years
    ]
    section = key.split("/")[0]
    related = [
        p
        for p in PAGES
        if p["language"] == language
        and p["key"].startswith(section + "/")
        and p["key"] != key
    ]
    title = TITLES[language][key]
    template = (
        "home.html"
        if key == "home"
        else ("publications.html" if key in ("research", "media") else "article.html")
    )
    context = {
        "key": key,
        "language": language,
        "other_language": other_language,
        "title": title,
        "seo": page_metadata(key, language),
        "structured_data": structured_data(key, language, TITLES[language]),
        "copy": COPY[language],
        "titles": TITLES[language],
        "menu_labels": NAVIGATION["menu_labels"][language],
        "main_navigation": NAVIGATION["main_navigation"],
        "section": section,
        "topics": HOME[language],
        "related": related,
        "groups": groups,
        "entry_count": len(entries),
        "years": years,
        "references": [
            reference
            for reference in REFERENCES
            if reference["section"] == ("research" if key == "research" else "media")
        ],
        "page_intro": PAGE_INTROS.get(key),
        "article_toc": article_toc(key, language),
        "url": lambda target: local_url(target, current_page),
        "page_url": lambda target, lang=language: local_url(
            route(target, lang), current_page
        ),
        "asset": lambda name: local_url(asset_path(name), current_page),
        "fragment": lambda: render_fragment(key, language, current_page),
    }
    output = environment.get_template(template).render(**context)
    destination = ROOT / current_page
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output.strip() + "\n", encoding="utf-8")


def main() -> None:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(("html",)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    for page in PAGES:
        build_page(page, environment)
    write_crawl_files(PAGES)
    print(f"Built {len(PAGES)} static pages from curated local content.")


if __name__ == "__main__":
    main()
