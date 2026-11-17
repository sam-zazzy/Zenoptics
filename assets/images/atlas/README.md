# Atlas page images

The Atlas page (`atlas/index.html`) expects these files in this folder.
Until a file is here, the page shows a grey box with the image description, or the company name for a logo.
To add an image, save it here with the exact file name below. No code change is needed.

| File | Where on the page | What it should show |
|---|---|---|
| `atlas-1-catalog-home.webp` | Hero, top of the page | Atlas home screen with report thumbnails showing certification status, owner, and views |
| `atlas-2-search-results.webp` | "Single interface for analytics" | Search results across BI tools, each report with its certification status, owner, and source |
| `atlas-3-governance-dashboard.webp` | "Governance by design" | A view of certified and uncertified reports and dashboards, with ownership and usage |
| `atlas-4-kpi-catalog.webp` | "Analytics catalog and KPI management" | KPI catalog with each KPI's definition, owner, and certification status |
| `atlas-5-lineage-view.webp` | "Usage intelligence and data lineage" | Lineage view tracing a data source to its datasets and downstream reports |
| `illumina-logo.svg` | "Trusted by" row | Illumina logo |

Screenshot size: 1600 px wide, any height, WebP format.
The page shows each screenshot at its own shape: the card is exactly the size of the image, nothing is cropped or padded.
When you replace an image whose height changes, update the `width` and `height` on its `<img>` tag in the page so the layout does not jump while it loads.
