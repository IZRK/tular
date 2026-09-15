# Tular design

## Visual identity

A photography-led site with deep teal, pale stone surfaces, a restrained peach accent and a prominent red SOS Proteus banner. A split photograph and introduction anchor the homepage. Interior pages use photographic mastheads, section navigation and captioned image groups. Article text and galleries share the same column edges; contact details align to the main page grid and the contact poster keeps its original aspect ratio.

## Tokens

- Background: `#f9faf7`; surface: `#eaf0ec`.
- Ink: `#173d3d`; muted text: `#536765`; rules: `#d8e1dc`.
- Links: `#175e63`; emergency banner: `#bf3424` with white text.
- Headings: Manrope 500–800. Body: Source Sans 3 400–700.
- Fonts load from Google Fonts. No local font files.
- Maximum width: 1280px; desktop gutters: 48px; mobile gutters: 20px.
- Main headline: 48–78px; section heading: 28–40px; body: 18px / 1.65.
- Gently rounded photographs, thin separators and consistent alignment.

## Rescue banner

SOS Proteus appears below the navigation on every page. It includes a clear found-an-olm message, a large callable telephone number and a link to rescue information. It remains visible without JavaScript and cannot be dismissed.

## Publications

Individual semantic articles grouped by year. Each record separates title, authors, citation, DOI and source actions. Affiliations use native expandable details. Search and year filters operate on individual entries, show a live result count and offer a clear reset. All entries remain readable without JavaScript.

## Content and code

Bilingual pages preserve the original collection; newly added summaries are translated. Recovered publisher links and unresolved archive searches have different labels. Jinja templates and curated JSON/HTML are editable source files. Prettier formats all generated HTML, CSS, JavaScript and content; there is no minification stage.

## Films

YouTube and Vimeo films are embedded in responsive players, with descriptive titles and source links. The homepage film is embedded in both languages. Provider-owned player accessibility issues are recorded separately in the browser report; local checks do not establish accessibility of third-party interfaces.
