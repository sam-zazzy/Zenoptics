# Maestro page images

The Maestro page (`maestro/index.html`) expects these files in this folder.
Until a file is here, the page shows a grey box with the image description.
To add an image, save it here with the exact file name below. No code change is needed.

| File | Where on the page | What it should show |
|---|---|---|
| `maestro-1-workflow.webp` | Hero, top of the page | A month-end close workflow in Maestro, with its steps and owners |
| `maestro-2-library.webp` | "Start from a template or draft a workflow with ZIVA" | The workflow library, browsed by business function |
| `maestro-3-step-settings.webp` | "Set review and approval requirements where they matter" | Step settings with the step owner, reviewer, and linked analytics |
| `maestro-4-agent-step.webp` | "Review agent work before approving the next step" | An AI agent's output on a cash flow forecasting step, shown with the linked analytics for review |
| `maestro-5-run-history.webp` | "See what informed a decision" | A workflow record with the analytics, actions, and approvals captured during a run |

Screenshot size: 1600 px wide, any height, WebP format.
The page shows each screenshot at its own shape: the card is exactly the size of the image, nothing is cropped or padded.
When you replace an image whose height changes, update the `width` and `height` on its `<img>` tag in the page so the layout does not jump while it loads.
Do not show the internal "ZenMaestro" label, a customer's name, or a real person's name in a screenshot.
Until Product confirms them, do not show Process Chains, Focus Mode, report filter presets, a live action log or a specific sign-off button.
