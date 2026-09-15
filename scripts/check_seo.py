"""Check published metadata, language pairs and crawl-file coverage."""

import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    settings = json.loads((ROOT / "content/seo.json").read_text())
    pages = json.loads((ROOT / "content/navigation.json").read_text())["pages"]
    base = settings["base_url"].rstrip("/")
    failures, titles, descriptions, canonicals = [], [], [], []
    for page in pages:
        route = page["route"]
        soup = BeautifulSoup((ROOT / route).read_text(), "html.parser")
        expected = (
            base + "/" + route.removesuffix("index.html")
            if route.endswith("index.html")
            else base + "/" + route
        )
        canonical = soup.select('link[rel="canonical"]')
        if len(canonical) != 1 or canonical[0]["href"] != expected:
            failures.append(f"{route}: wrong canonical URL")
        canonicals.append(expected)
        metadata = {
            node.get("property", node.get("name")): node.get("content")
            for node in soup.select("head meta")
        }
        title = soup.title.get_text()
        description = metadata.get("description")
        titles.append(title)
        descriptions.append(description)
        for name, value in {
            "og:title": title,
            "twitter:title": title,
            "og:description": description,
            "twitter:description": description,
            "og:url": expected,
            "twitter:card": "summary_large_image",
        }.items():
            if not value or metadata.get(name) != value:
                failures.append(f"{route}: missing or inconsistent {name}")
        image_url = metadata.get("og:image", "")
        if (
            not image_url.startswith(base + "/assets/")
            or metadata.get("twitter:image") != image_url
        ):
            failures.append(f"{route}: invalid preview image URL")
        elif not (ROOT / image_url.removeprefix(base + "/")).is_file():
            failures.append(f"{route}: preview image missing")
        if not metadata.get("og:image:alt") or not metadata.get("twitter:image:alt"):
            failures.append(f"{route}: missing preview image description")
        alternatives = {n["hreflang"]: n["href"] for n in soup.select("link[hreflang]")}
        suffix = "" if page["key"] == "home" else page["key"] + ".html"
        wanted = {
            "en": base + "/" + suffix,
            "sl": base + "/sl/" + suffix,
            "x-default": base + "/" + suffix,
        }
        if alternatives != wanted:
            failures.append(f"{route}: inconsistent language alternatives")
        try:
            graph = json.loads(
                soup.select_one('script[type="application/ld+json"]').string
            )["@graph"]
            webpage = next(
                node
                for node in graph
                if node.get("url") == expected
                and node["@type"] in ["WebPage", "ContactPage", "AboutPage"]
            )
            if (
                webpage["inLanguage"] != page["language"]
                or webpage["description"] != description
            ):
                failures.append(f"{route}: inconsistent structured data")
        except (TypeError, ValueError, KeyError, StopIteration):
            failures.append(f"{route}: invalid structured data")
    if len(set(titles)) != len(pages) or len(set(descriptions)) != len(pages):
        failures.append("Page titles and descriptions must be unique")
    sitemap = ET.parse(ROOT / "sitemap.xml")
    locations = [
        n.text
        for n in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    ]
    if sorted(locations) != sorted(canonicals):
        failures.append("Sitemap does not match canonical pages")
    if f"Sitemap: {base}/sitemap.xml" not in (ROOT / "robots.txt").read_text():
        failures.append("Missing sitemap declaration in robots.txt")
    report = {"pages": len(pages), "sitemap_urls": len(locations), "failures": failures}
    (ROOT / "reports/seo-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
