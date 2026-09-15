"""Validate the generated static site against its curated source content."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
import html5lib

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    pages = load_json("content/navigation.json")["pages"]
    failures = []
    documents = {
        page["route"]: BeautifulSoup(
            (ROOT / page["route"]).read_text(encoding="utf-8"), "html.parser"
        )
        for page in pages
    }
    local_links = 0

    for page in pages:
        route = page["route"]
        soup = documents[route]
        parser = html5lib.HTMLParser()
        parser.parse((ROOT / route).read_text(encoding="utf-8"))
        if parser.errors:
            failures.append(f"{route}: HTML parse errors: {parser.errors}")
        if len(soup.select("h1")) != 1:
            failures.append(f"{route}: expected one h1")
        if soup.html.get("lang") != page["language"]:
            failures.append(f"{route}: wrong language")
        if soup.select("[style], table, font"):
            failures.append(f"{route}: legacy formatting remains")
        if not soup.select_one('.rescue-banner a[href="tel:+38631804163"]'):
            failures.append(f"{route}: missing SOS call action")
        if not any(
            "fonts.googleapis.com/css2" in tag.get("href", "")
            for tag in soup.select("link")
        ):
            failures.append(f"{route}: missing Google Fonts stylesheet")

        for tag, attribute in (
            ("a", "href"),
            ("img", "src"),
            ("script", "src"),
            ("link", "href"),
        ):
            for node in soup.select(f"{tag}[{attribute}]"):
                target = node[attribute]
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                local_links += 1
                destination = (
                    (ROOT / route).parent / unquote(parsed.path)
                    if parsed.path
                    else ROOT / route
                )
                if not destination.exists():
                    failures.append(f"{route}: missing {target}")
                elif parsed.fragment and destination.suffix == ".html":
                    fragment_soup = BeautifulSoup(
                        destination.read_text(), "html.parser"
                    )
                    if not fragment_soup.find(id=unquote(parsed.fragment)):
                        failures.append(f"{route}: missing fragment {target}")

        for frame in soup.select("iframe"):
            if not frame.get("title") or not frame.get("src", "").startswith(
                (
                    "https://www.youtube-nocookie.com/embed/",
                    "https://player.vimeo.com/video/",
                )
            ):
                failures.append(f"{route}: invalid or unlabelled video embed")
        for heading in soup.select("h1,h2,h3"):
            text = heading.get_text(" ", strip=True)
            if text and text[0].islower() and not text.startswith("eDNA"):
                failures.append(f"{route}: lowercase heading: {text}")
        if page["key"] == "home" and not soup.select_one('iframe[src*="tePqvqWYOxA"]'):
            failures.append(f"{route}: missing homepage film embed")
        for image in soup.select("img"):
            if not image.has_attr("alt"):
                failures.append(f"{route}: image has no alt attribute")

        if page["key"] in ("research", "media"):
            records = load_json(f"content/{page['key']}-{page['language']}.json")
            if len(soup.select(".publication")) != len(records):
                failures.append(f"{route}: publication count differs from content")
            for entry in records:
                rendered = soup.find(id="publication-" + entry["id"])
                if not rendered:
                    failures.append(f"{route}: missing publication {entry['id']}")

    if list((ROOT / "assets").rglob("*.ttf")) or list(
        (ROOT / "assets").rglob("*.woff*")
    ):
        failures.append("Local font files remain")

    report = {
        "pages": len(pages),
        "local_links_checked": local_links,
        "failures": failures,
    }
    (ROOT / "reports/content-check.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
