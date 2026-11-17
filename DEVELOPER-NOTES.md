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
- The posts from the previous site (about 50) still have to be moved, each to its exact old address `/blog/<slug>/`. How they are moved and published is still to be decided.

## Before launch

- ZenOptics Product has to confirm some product claims listed in the client's change documents.
- The connector list on the Atlas page is not verified yet.
