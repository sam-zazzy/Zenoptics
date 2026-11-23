# ZenOptics website: notes for the developer

Prepared 17 November 2026. This folder is the static site served at zenoptics.com (GitHub Pages, see `CNAME`). Plain HTML, Tailwind CSS v4 and one shared script. No framework.

## Pages

| Page | File | Status |
|------|------|--------|
| Home | `index.html` | Existing page, not changed in this round |
| Atlas | `atlas/index.html` | New. Copy approved by the client, with their change document applied |
| Nexus | `nexus/index.html` | New. Copy approved by the client, with their change document applied |
| Maestro | `maestro/index.html` | New. Copy approved by the client, with their change document applied |
| Blog listing | `blog/index.html` | 115 posts. Not launched yet (see Blog) |
| Blog posts | `blog/<slug>/index.html` | Generated, see Blog |
| Thank you | `thankyou/index.html` | After a form is sent. noindex. Built by `tools/build-pages.py` |
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

## Blog (not launched yet)

- 115 posts, listing newest first (`blog/index.html`, latest post on top, "Show more posts" in batches of 12). The old sample cards and picsum photos are gone.
- All blog pages carry `<meta name="robots" content="noindex">` and the top menu shows "Blog" on blog pages only. Remove both when the blog launches.
- **2026 posts (56, 23 Apr – 9 Nov 2026)** are built from the Word documents in `Blog Content Archive/` (kept out of git on purpose; ask the team for the folder) by `tools/build-blog-archive.py`:
  `python3 tools/build-blog-archive.py && python3 tools/build-pages.py && python3 tools/seo.py && npm run build`
  (needs `pip install python-docx openpyxl`, and `playwright-core` + Google Chrome for the covers). Edit the document and run it again; do not edit those post pages by hand.
  - Documents flagged NOT PUBLISHED, CANCELLED, UNCONFIRMED or ZAZZY DRAFT are skipped; the PUBLISHED TEXT version wins where two exist.
  - 16 posts use the real banner (from inside the document, or `Blog Images/`). 40 have a generated title cover until the real banner is found (list: `Blog Content Archive/GENERATED_COVERS.txt`). To swap one: add the file to `COVERS` in the script and rerun.
  - Demo links (Calendly, /request-demo/) point to `/schedule-a-demo/`. Links to posts that were never published are removed (the script prints them).
  - FAQ sections also go out as FAQPage structured data.
- **Posts from Nov 2020 – Dec 2025 (59)** came from the old WordPress dev copy on Pantheon (`dev-zenoptics-new-2024.pantheonsite.io`). Images are in `assets/images/blog/<slug>/`. 4 in-post images no longer exist anywhere; those figures carry the class `hidden`. Links inside them to old pages (`/analytics-catalog/`, `/contact/`, `/platform/`, old PDFs) still point to www.zenoptics.com and will 404 until those pages exist.
- **Not moved yet: 15 posts from 8 Jan – 14 Apr 2026.** There is no document for them in the archive and they were not on the dev copy; a WordPress export of the old site is the only full source.

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
