# Screenshots

Interactive, always-up-to-date render of the shipped screens (landing + dashboard):

**▶ https://claude.ai/code/artifact/ed784541-7dda-4ba5-965c-0fde2f5b7456**

## Capture your own (2 minutes)

```bash
# 1. Run the app in Demo Mode (no backend needed)
cd frontend
NEXT_PUBLIC_USE_MOCK=true npm run dev      # → http://localhost:3000
```

Then capture these frames (⌘⇧4 / Win+Shift+S), saving into this folder:

| File | Screen | How |
| --- | --- | --- |
| `01-landing.png` | Landing hero | Open `/` |
| `02-dashboard.png` | Full dashboard mid-stream | Open `/dashboard`, send *"I have acne, what should I wear?"* with a selfie + garment |
| `03-aura-score.png` | Aura Score card | Scroll the Results panel to the top |
| `04-tryon.png` | Before/after try-on | Drag the slider; open fullscreen |
| `05-onboarding.png` | Walkthrough | Settings → *Replay walkthrough* |
| `demo.gif` | 15s full turn | Record the send → timeline → results sequence |

Tip: use a 1280×800 desktop viewport and the mobile (375×812) viewport for a
responsive pair.

## Diagrams

Vector sources live one level up: [`../architecture.svg`](../architecture.svg) and
[`../workflow.svg`](../workflow.svg). Export to PNG with any of:

```bash
# with rsvg-convert (librsvg)
rsvg-convert -w 1920 ../architecture.svg -o architecture.png
rsvg-convert -w 1920 ../workflow.svg     -o workflow.png

# or with Inkscape
inkscape ../architecture.svg --export-filename=architecture.png -w 1920
```

Or open the `.svg` in a browser and export/print to PNG.
