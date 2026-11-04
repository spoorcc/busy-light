# Diagrams-as-Code Standard

- **Status:** Draft

Every diagram and graphic in the documentation is generated from text source that is reviewed, versioned and diffable.
No hand-drawn or GUI-exported images (draw.io/Visio/PNG paste) -- except real photographs and screenshots, which need a
caption stating what product revision and software version they show.

## 1. Tool per purpose
| Need | Tool | Source location |
|------|------|-----------------|
| Architecture (C4 context/container/component), sequence, state machine, class, deployment | **PlantUML** | `docs/diagrams/plantuml/*.puml` |
| Flowcharts, process/lifecycle, simple state/Gantt/ER, small inline diagrams | **Mermaid** | inline ` ```mermaid ` block, or `docs/diagrams/mermaid/*.mmd` |
| Digital timing, bus protocols (I2C/SPI/UART/PWM), register bit-fields, LED blink patterns | **WaveDrom** | `docs/diagrams/wavedrom/*.json` |
| Schematics, PCB views, 3D renders | **KiCad** via `kicad-cli sch/pcb export ...` | generated from `hw/kicad/` into the release package |
| Enclosure views, exploded views, drawings | **FreeCAD** headless export scripts (`mech/` scripts) | generated into `mech/exports/<rev>/` |
| Plots/measurements (simulation, test data) | Python (matplotlib) scripts | script + data stored next to the report |

Choose one tool per diagram type; do not mix styles for the same concept. Need something else (e.g. block diagrams with
precise layout)? Write an ADR first; the replacement must also be text-based.

## 2. Rules
1. **Source is the artefact.** Rendered SVGs live in `docs/diagrams/generated/` (marked generated in `.gitattributes`) and are
   **never edited by hand**. Inline Mermaid renders natively on GitHub.
2. **Reproducible and pinned.** PlantUML version is recorded in the build log; Mermaid and WaveDrom CLIs are pinned in
   `scripts/diagrams/package.json`. Build: `scripts/build_diagrams.sh`. CI runs `scripts/build_diagrams.sh --check` and fails if
   committed outputs are stale or a source does not render. The check compares structure, labels and colours, not coordinates, because text widths depend on the machine's font metrics (`scripts/svg_normalize.py`). CI pins PlantUML 1.2026.8 and Noto Sans; regenerate with the same versions.
3. **Name by area, topic, type:** `arch-system-context.puml`, `sw-led-driver-sequence.puml`, `hw-i2c-timing.json`.
4. **Traceable.** Architecture elements carry their `ARCH-nnn` ID in the label; the diagram is referenced from the document that
   defines those IDs. Interfaces drawn must exist in the requirements or interface spec -- a diagram never introduces a design fact.
5. **One message per diagram**, readable at A4 width, <= ~15 elements; split with C4 levels otherwise. Legend if symbols are not obvious.
6. **Accessible:** every embedded diagram has a caption, alt text that states the message, and the surrounding text does not depend on the picture alone.
   Do not rely on colour alone; use shape/line style too; use a colour-blind-safe palette and sufficient contrast.
7. **Style:** consistent theme in `docs/diagrams/plantuml/_style.iuml` (to be created once the first architecture diagram exists), same terms as the glossary.
8. **Embedding:** `![Alt text stating the message](../diagrams/generated/plantuml/name.svg)` followed by an italic caption
   and a link to the source. In user documentation, follow `docs/standards/writing.md`.
9. **Review:** reviewers read the source diff and the rendered output; a diagram that contradicts the text is a finding.

## 3. Tooling setup
```sh
sudo pacman -S plantuml graphviz          # or your package manager
npm ci --prefix scripts/diagrams          # mermaid-cli + wavedrom-cli (pinned)
scripts/build_diagrams.sh                 # render
scripts/build_diagrams.sh --check         # CI freshness check
```
