---
name: write-diagrams
description: Create or update documentation diagrams as code (PlantUML, Mermaid, WaveDrom) following the project's diagrams-as-code standard, and render/verify them.
---

# Write diagrams as code

1. Read `docs/standards/diagrams.md` and pick the tool per purpose (PlantUML architecture/sequence/state, Mermaid flow, WaveDrom timing).
2. A diagram shows facts that exist in requirements, architecture text or code. Do not invent interfaces, pins, timings or values; ask.
3. Put source in `docs/diagrams/<tool>/` named `<area>-<topic>-<type>`; label architecture elements with `ARCH-nnn`.
4. Run `scripts/build_diagrams.sh`; commit source and generated SVG together. Never edit generated files.
5. Embed with alt text and caption; run `scripts/build_diagrams.sh --check`.
6. Report which renderers actually ran (Mermaid and WaveDrom need `npm ci --prefix scripts/diagrams`).
