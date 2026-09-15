# Tular Cave Laboratory

A bilingual static website for Tular, with original photographs, laboratory and project material, a curated bibliography, and a prominent SOS Proteus rescue banner.

## Preview

```sh
python3 -m http.server 8000
```

- English: <http://localhost:8000/>
- Slovenian: <http://localhost:8000/sl/>

Use the local HTTP server so directory links resolve to their index pages. Google Fonts requires an internet connection; ordinary sans-serif fallbacks are supplied. The published site needs no Python, Node or backend.

## Project layout

```text
assets/
  documents/          Original PDFs
  images/             Original photos, logos and document previews
  scripts/site.js     Navigation and publication filters
  styles/site.css     Readable, unminified styles
content/
  articles/en/        Editable English article fragments
  articles/sl/        Editable Slovenian article fragments
  research-*.json     Structured bibliography
  media-*.json        Structured media archive
  home.json           Homepage topics
  references.json     Added references and bilingual summaries
  navigation.json     Pages, labels and source URLs
  assets.json         Asset provenance and checksums
  link-map.json       Original links and their replacements
  url-map.json        Legacy routes and new destinations
templates/            Shared Jinja HTML templates
scripts/              Build, validation and packaging tools
docs/                 Product, design and content-audit notes
reports/              Content and link audit evidence
*.html, sl/, …        Generated, formatted static pages
```

The one-time crawler and raw Joomla snapshots have been removed from the project. A backup of the original import is retained outside the project at `/tmp/tular-original-import-2026-09-15.tar.gz` in this workspace environment. It is not required to rebuild or publish the website.

## Edit and rebuild

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
```

Edit content in `content/`, shared markup in `templates/`, and styles or behaviour in `assets/`. The build renders the 28 pages, then formats the source and output with Prettier. **There is no minification step.** Editing a generated page directly works for a quick preview, but rebuilding replaces that edit.

The build is offline: it reads curated local files and makes no requests to the old website. Fonts are linked from Google Fonts in the shared base template; no fonts are stored locally.

## Validate

With the Python environment activated:

```sh
npm run check
npm run format:check
npx playwright install chromium
```

With the preview server running in another terminal:

```sh
npm run check:browser
```

Validation covers all 28 pages at desktop and mobile widths, local links and fragments, image loading, HTML structure, matching language routes, publication counts, filters, reset, expandable details, mobile navigation, and reading without JavaScript. Representative page types also receive Axe accessibility checks. Browser screenshots are kept in ignored `reports/screenshots/`.

The external link audit is documented in [docs/CONTENT-AUDIT.md](docs/CONTENT-AUDIT.md). Publisher access restrictions and Internet Archive availability cannot be guaranteed by local tests.

## Publish

```sh
npm run package
```

Upload the contents of `dist/` to a static host. The package contains only generated pages, images, documents, styles, JavaScript and a Netlify-style `_redirects` file. Other hosts can apply the original-to-new paths in `content/url-map.json` using their own redirect configuration. No deployment has been made.

## Content and credits

The original content was retrieved from [tular.si](https://tular.si/) on 15 September 2026. The 47 successful source URLs include aliases and consolidate into 13 pages in each language. Original English and Slovenian collections are retained, with formatting, link and citation corrections recorded in the audit.

Research includes 50 original bibliography entries per language and one newly added, explicitly identified related paper from 2026. The media archives retain 117 English and 84 Slovenian entries, with additional linked features. New summaries and interface labels are bilingual; publication titles remain in their published language.

Text, photographs and documents retain the rights of Društvo za jamsko biologijo / Society for Cave Biology and their named authors. Asset source URLs and checksums are recorded in `content/assets.json`. Manrope and Source Sans 3 are loaded through Google Fonts.

Git is initialized on `main`. Dependencies, environments, IDE files, credentials, generated release packages and browser screenshots are ignored.

## Search and social metadata

Edit `content/seo.json` for the production URL, per-page English and Slovenian titles and descriptions, and original photographs used in link previews. The default production address is `https://tular.si`. Rebuild after changing it.

Every generated page has an absolute canonical URL, reciprocal English/Slovenian language alternatives and an English `x-default`, Open Graph metadata, a Twitter large-image card, and JSON-LD describing the organization, website and page. Interior pages also include breadcrumb structured data. The build generates `sitemap.xml` and `robots.txt`; packaging includes both. Homepages use `/` and `/sl/` as their canonical addresses.

`npm run check` validates metadata uniqueness, canonical/language consistency, preview-image files, structured data and sitemap coverage. Preview crawlers require the new site and images to be deployed at the configured production address; these changes are local until deployment. No search ranking or live social-preview result is implied by local validation.

Implementation references: [Google’s localized-page guidance](https://developers.google.com/search/docs/specialty/international/localized-versions) and the [Open Graph protocol](https://ogp.me/).

The SOS Proteus Info Centre pages use visitor information from Visit Kranj and direct, language-specific booking links. Main-menu order is explicit in `content/navigation.json`. Internal homepage links use directory URLs; generated filenames remain `index.html`.
