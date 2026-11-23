# ZenOptics website: notes for the developer

Prepared 17 November 2026. This folder is the static site served at zenoptics.com (GitHub Pages, see `CNAME`). Plain HTML, Tailwind CSS v4 and one shared script. No framework.

## Pages

| Page | File | Status |
|------|------|--------|
| Home | `index.html` | Existing page, not changed in this round |
| Atlas | `atlas/index.html` | New. Copy approved by the client, with their change document applied |
| Nexus | `nexus/index.html` | New. Copy approved by the client, with their change document applied |
| Maestro | `maestro/index.html` | New. Copy approved by the client, with their change document applied |
| Blog listing | `blog/index.html` | New template with sample content. Not ready to launch (see Blog) |
| Blog post | `blog/insight-to-governed-execution/index.html` | New template, one sample post. Not ready to launch |
| Privacy policy | `privacy-policy/index.html` | Existing |
| Not found | `404.html` | Existing |

Please do not change any page wording without approval from Jay. The product page copy went through client review.

## Running and building

- `npm install` once, then `npm run serve` and open http://localhost:8000/
- Styles: edit `src/input.css`, never `style.css`. Rebuild with `npm run build` (or `npm run dev` to watch).
- Brand colours, the font (Rubik) and the shared components (`.btn`, `.container-x`, `.img-slot`) are defined in `src/input.css`.
- `script.js` runs the demo and contact pop-ups (HubSpot forms), the tabs on the Atlas connectors section, grey placeholders for missing images, the footer year, and "Show more posts" on the blog listing.

## Header and footer

The header, footer and the two pop-ups are repeated in every page, so a change to them has to be made on every page.

- Each product page has its own demo button label ("Request an Atlas demo", "Request a Nexus demo", "Request a Maestro demo"). The footer link stays "Get a Demo" on every page.
- The footer "Blog" link is hidden (class `hidden`) on every page except the blog pages, until the blog goes live. The top menu shows "Blog" on the blog pages only.

## Images still to supply

Product screenshots are not in the folder yet. Each product folder has a guide with the file names, sizes and what each image must show:
`assets/images/atlas/README.md`, `assets/images/nexus/README.md`, `assets/images/maestro/README.md`.
Until a file is added, the page shows a grey placeholder in its place.

## Blog (sample content, not ready to launch)

- The listing shows 25 real post titles and dates. The excerpts are placeholder text and the photos are sample photos loaded from picsum.photos.
- Only one post page exists. The other 24 cards link to `/blog/<slug>/` pages that do not exist yet.
- Both blog pages carry `<meta name="robots" content="noindex">`. Remove it when the real posts are in.
- 59 posts from the previous site (published Nov 2020 – Dec 2025) are moved, each at its old address `/blog/<slug>/`. Text, covers and in-post images came from the old WordPress dev copy on Pantheon (`dev-zenoptics-new-2024.pantheonsite.io`), which stopped updating in Dec 2025. Images are in `assets/images/blog/<slug>/`. Their cards are listed after the sample cards in `blog/index.html`, between the `MOVED POSTS` comments.
- 4 in-post images no longer exist anywhere; those figures carry the class `hidden`.
- Links inside the moved posts that point to old pages not on the new site (`/analytics-catalog/`, `/contact/`, `/platform/`, old PDFs and others) still point to www.zenoptics.com and will 404 until those pages exist or the links are changed.
- The 35 posts published in 2026 are not moved yet: their text is only in the Wayback Machine and their covers are not archived anywhere.

## Before launch

- ZenOptics Product has to confirm some product claims listed in the client's change documents.
- The connector list on the Atlas page is not verified yet.

## Before every push to main (responsive + SEO)

1. Check every page on phone and tablet widths (320 to 1180 px): no sideways scroll, nothing cut off, menu and forms usable.
2. Run `python3 tools/seo.py` from the repo root. It:
   - sets the title, meta description, canonical, Open Graph and Twitter tags of the main pages (edit the `PAGES` list in the script to change them; titles ~50–60 characters, descriptions ~140–160);
   - writes `sitemap.xml` (indexable pages only), `robots.txt` (search engines and AI crawlers allowed) and `llms.txt` (plain summary of the site for AI assistants);
   - prints an audit of every page. Indexable pages must come out clean.
3. A new page that should be indexed: add it to `PAGES` (and to `LLMS_ORDER` if it belongs in llms.txt), then run the script.
4. Pages with `<meta name="robots" content="noindex">` stay out of the sitemap and llms.txt. Today that is the blog, BI Estate Assessment and Trusted AI.
5. The staging copy must not be indexed: its build replaces `robots.txt` with `Disallow: /` and adds `noindex` to every page.

Default share image: `assets/images/og-zenoptics.jpg` (1200×630).

## Resources, Schedule a Demo and /demo pages

These three pages are generated: `python3 tools/build-pages.py && python3 tools/seo.py && npm run build`.
Resources has tabs (All, Blogs, Guides, Webinars, White papers; script.js `data-res-tabs`). All shows 6 cards per section with "View all"; a single tab shows 9 cards and "See more" adds 6. The tab is kept in the URL hash (`#blog`, `#guides`, `#webinars`, `#whitepapers`). Blog cards come from the moved posts; guides, webinars and white papers are listed in `tools/build-pages.py`.
