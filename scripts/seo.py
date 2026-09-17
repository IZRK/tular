"""SEO metadata and crawl files for the bilingual static site."""

import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "content/seo.json").read_text(encoding="utf-8"))
BASE_URL = SETTINGS["base_url"].rstrip("/")


def absolute_url(path: str) -> str:
    return BASE_URL + "/" + path.lstrip("/")


def canonical_url(key: str, language: str) -> str:
    prefix = "sl/" if language == "sl" else ""
    return absolute_url(prefix + ("" if key == "home" else key + ".html"))


def page_metadata(key: str, language: str) -> dict:
    page = SETTINGS["pages"][key]
    metadata = dict(page[language])
    metadata.update(
        canonical=canonical_url(key, language),
        site_name=SETTINGS["site_name"][language],
        locale="sl_SI" if language == "sl" else "en_GB",
        alternate_locale="en_GB" if language == "sl" else "sl_SI",
        alternates={lang: canonical_url(key, lang) for lang in ("en", "sl")},
        image={**page["image"], "url": absolute_url(page["image"]["path"])},
    )
    return metadata


def structured_data(key: str, language: str, titles: dict) -> dict:
    meta = page_metadata(key, language)
    organization_id = absolute_url("#organization")
    website_id = absolute_url("#website")
    page_id = meta["canonical"] + "#webpage"
    organization = {
        "@type": "Organization",
        "@id": organization_id,
        "name": "Jamski laboratorij Tular",
        "alternateName": "Tular Cave Laboratory",
        "url": absolute_url(""),
        "logo": absolute_url("assets/images/tular-logo.png"),
        "email": "info@tular.si",
        "telephone": "+38631804163",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Oldhamska c. 8a",
            "postalCode": "4000",
            "addressLocality": "Kranj",
            "addressCountry": "SI",
        },
        "sameAs": [
            "https://www.facebook.com/TularCaveLaboratory",
        ],
    }
    page_type = (
        "ContactPage"
        if key == "contact"
        else ("AboutPage" if key == "tular" else "WebPage")
    )
    webpage = {
        "@type": page_type,
        "@id": page_id,
        "url": meta["canonical"],
        "name": meta["title"],
        "description": meta["description"],
        "inLanguage": language,
        "isPartOf": {"@id": website_id},
        "about": {"@id": organization_id},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "contentUrl": meta["image"]["url"],
            "width": meta["image"]["width"],
            "height": meta["image"]["height"],
            "caption": meta["image_alt"],
        },
    }
    graph = [
        organization,
        {
            "@type": "WebSite",
            "@id": website_id,
            "url": absolute_url(""),
            "name": "Tular Cave Laboratory",
            "alternateName": "Jamski laboratorij Tular",
            "inLanguage": ["en", "sl"],
            "publisher": {"@id": organization_id},
        },
        webpage,
    ]
    if key != "home":
        breadcrumb_id = meta["canonical"] + "#breadcrumb"
        webpage["breadcrumb"] = {"@id": breadcrumb_id}
        graph.append(
            {
                "@type": "BreadcrumbList",
                "@id": breadcrumb_id,
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": titles["home"],
                        "item": canonical_url("home", language),
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": titles[key],
                        "item": meta["canonical"],
                    },
                ],
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def write_crawl_files(pages: list[dict]) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    sitemap = ET.Element(f"{{{namespace}}}urlset")
    for page in pages:
        entry = ET.SubElement(sitemap, f"{{{namespace}}}url")
        ET.SubElement(entry, f"{{{namespace}}}loc").text = canonical_url(
            page["key"], page["language"]
        )
    ET.indent(sitemap, space="  ")
    ET.ElementTree(sitemap).write(
        ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True
    )
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + absolute_url("sitemap.xml") + "\n",
        encoding="utf-8",
    )
