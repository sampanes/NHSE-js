# Themed Island → Flat Island Item Dump: Gameplan

## Goal
Create an easy, mostly guided workflow to:
1. Build or select a themed item set.
2. Prepare a flat “pickup island” layout.
3. Spawn/place many theme items in organized dump zones.
4. Grab items with an offline friend account.

---

## Scope (Phase 0)
This pass turns planning into implementation-ready defaults based on your answers.

### Deliverables for this phase
- Locked product defaults (platform, stacking, overwrite, backup behavior).
- A draft data format for themes (Markdown-first, with migration path).
- A concrete UX flow for one-click/low-click dumping.
- A shortlist of unresolved items that still need decisions.

### Technical foundations to establish now
- Add a dedicated feature folder in the solution (proposal: `NHSE.Core/Editing/Themes` + `NHSE.WinForms/Subforms/ThemedDump`).
- Define clear boundaries:
  - `Core`: parsing, validation, planning, placement engine, backup service.
  - `WinForms`: UI flow and visualization only.
- Define base interfaces early to avoid lock-in:
  - `IThemeRepository`
  - `IItemAssetCatalog`
  - `IDumpPlanner`
  - `IBackupService`
- Add lightweight architecture decision records (ADRs) for key choices.

### LLM maintenance note (living plan)
- At each implementation PR, append a short “Plan Delta” note: what changed, why, and what assumptions were invalidated.
- Ask LLM to update this plan after each milestone with:
  - chosen libraries,
  - final data contracts,
  - technical debt list,
  - migration notes.

---

## Product Decisions (Locked from Owner Input)

### Platform
- **Primary target:** Windows desktop (WinForms) first.
- **Secondary target:** Keep architecture open for CLI/bot reuse later (“more the merrier”), but do not block WinForms delivery.

### Community model
- **Theme contributions:** Allow community PRs, but assume low contribution traffic.
- Keep maintainer-friendly tooling simple (easy lint/check for theme files).

### Images & assets
- No preferred source yet; we will prioritize a community dataset with broad item coverage by name/id.
- **Default strategy:** support cached images locally for convenience.
- Keep a **manifest of source URLs** so asset origin is traceable and replaceable later if needed.

### Placement behavior defaults
- **Default layout:** dense placement with optional traffic lanes.
- **Stacking default:** max stack for stackable items.
- **Overwrite default:** ask user at execute time via clear toggle:
  - Off = skip occupied tiles.
  - On = overwrite all in target area.

### Safety/backup behavior
- Add a lightweight rotating backup directory.
- Keep most recent backups only (small retention), replacing oldest automatically.
- Target user story: “oh no rollback” is possible for recent operations, not long history.

---

## Phase 1 — UX/GUI Redesign (Guided Workflow)
Build a simple wizard-like interface in NHSE for non-technical users.

### Proposed UI flow
1. **Theme Selection**
   - Search/select theme (e.g., Cottagecore, City, Japanese Garden).
   - Preview included items and quantities.
2. **Island Target Setup**
   - Select area(s) for dumping (e.g., bottom-left corner, rectangle brush).
   - Auto-validate tile capacity.
3. **Dump Strategy**
   - Choose layout mode:
     - Dense Grid (default)
     - Dense Grid + Traffic Lanes
     - Rows by category
   - Stack mode default: **Max Stack**.
   - Overwrite mode default: **Ask each run**.
4. **Execute + Safety**
   - Dry run preview (highlight affected tiles).
   - Show backup destination + retention count.
   - Apply edits.

### UX quality bars
- Beginner-friendly labels.
- “Why this failed” errors (no opaque exceptions).
- One-click repeat of last successful job.

### Technical implementation details
- UI architecture:
  - Use presenter/controller classes so planner logic is testable outside WinForms.
  - Keep form code-behind minimal (event wiring only).
- State model proposal:
  - `DumpSessionState` object passed between wizard steps.
  - Immutable snapshots for undo/redo within wizard.
- Rendering/performance:
  - Virtualized list for item previews.
  - Background thumbnail loading with cancellation tokens.
- Error design:
  - Convert exceptions to user-facing `ValidationIssue` entries (severity + action hint).

### LLM maintenance note
- Have LLM update this section with final control names, event flow diagrams, and any new UX constraints discovered during user testing.

---

## Phase 2 — Asset Image Pipeline
Collect and map item images so themes and picker UI are visual.

### Data pipeline proposal
- Source metadata + image URLs from one or more community/public datasets.
- Normalize into local cache with stable IDs.
- Generate an item index:
  - internal item ID
  - display name(s)
  - icon path
  - tags/categories
  - source attribution (where available)
- Keep a refresh script for periodic updates.

### Caching strategy
- Store image files in a versioned local asset folder.
- Store a manifest JSON with checksum + source URL.
- Lazy load in UI; preload thumbnails only.

### Risks to manage
- Redistribution/copyright uncertainty across sources.
- Mirror availability and broken links.
- Localization consistency across languages.

### Technical implementation details
- Proposed file contracts:
  - `assets/items/index.json`
  - `assets/items/images/<item_id>.png`
  - `assets/items/sources.json`
- Refresh tool behavior:
  - Diff remote index vs local manifest.
  - Download only changed/new assets.
  - Generate cache integrity report.
- Library options to evaluate:
  - `System.Text.Json` for metadata.
  - `HttpClient` with retry/backoff for sync.
  - Optional image processing via `ImageSharp` if resize needed.
- Fallback behavior:
  - If icon missing, use placeholder + item name, never hard-fail loading screen.

### LLM maintenance note
- Ask LLM to continuously revise “approved source list”, mirror reliability ranking, and exact legal/safe distribution posture as community data sources evolve.

---

## Phase 3 — Theme System (Markdown-First)
Start with Markdown for easy editing, then optionally compile/convert to JSON.

### Proposed `themes/*.md` schema
Each theme file includes:
- Theme name + short intent.
- Visual mood tags.
- Item list (with quantity ranges or fixed qty).
- Optional alternatives/substitutions.
- Suggested placement contexts.
- Optional notes for creative use.

#### Example skeleton
```md
# Theme: Visual Demo - Cozy Market Street

## Description
Colorful storefront + props for a high-visibility first demo.

## Tags
market, city, visual, demo

## Items
- item_id: 1234 | name: Stall            | qty: 6   | priority: high
- item_id: 5678 | name: Plain Party-Lights Arch | qty: 2 | priority: high
- item_id: 9012 | name: Barrel           | qty: 8-12 | priority: medium

## Substitutions
- If Stall unavailable: Covered Counter

## Placement Notes
- Keep one traffic lane every 3 tiles.
- Place visual anchor objects at each corner first.
```

### Evolution path
- v1: Markdown parsed at runtime.
- v2: Build step converts Markdown → normalized JSON.
- v3: Optional in-app theme editor.

### Technical implementation details
- Model proposal:
  - `ThemeDefinition`
  - `ThemeItemEntry`
  - `ThemeSubstitution`
  - `ThemePlacementHint`
- Validation rules:
  - Required: `Theme`, `Items`.
  - Reject unknown item IDs (or downgrade to warning if “strict mode off”).
  - Ensure quantity ranges are sane (`min <= max`, no negatives).
- Parser strategy:
  - Start with deterministic line parser for controlled schema.
  - Evaluate markdown AST parser only if schema complexity grows.
- Contribution safety:
  - Add schema lint command (can run in CI).
  - Add example templates for easier PR contributions.

### LLM maintenance note
- Ask LLM to update this section with finalized grammar, schema versioning (`schema_version`), and backward compatibility policy once parser reaches stable release.

---

## Phase 4 — Dump Automation (Button Presses / Macro-like Flow)
Implement safe, repeatable automation for placing items rapidly.

### Automation modes
1. **Direct save edit placement** (preferred):
   - Programmatically set ground items in chosen coordinates.
   - Fast, deterministic, low manual input.
2. **Controller-like macro fallback**:
   - Simulate repetitive placement interactions where needed.
   - Use only if direct save operations cannot cover the use case.

### Placement algorithm concept
- Input: item pool + target dump rectangle(s).
- Process:
  1. Validate target area capacity.
  2. Apply overwrite/skip policy.
  3. Order items by priority/category.
  4. Fill coordinates with selected lane spacing rule.
  5. Stack stackables at max by default.
  6. Report summary (placed/skipped/overwritten).

### Safety mechanisms
- Auto-create a rolling backup before write.
- Support optional protected-tile exclusion later.
- Dry-run overlay and change count.
- Roll back quickly to latest backup(s).

### Technical implementation details
- Planner/engine split:
  - `DumpPlanGenerator`: pure function from inputs → `DumpPlan`.
  - `DumpPlanExecutor`: applies plan to save data.
- Coordinate generation:
  - deterministic traversal modes (`row-major`, `serpentine`, `rings`).
  - reserve periodic lane coordinates based on step interval.
- Overwrite policy enum:
  - `SkipOccupied`
  - `OverwriteAll`
  - future: `OverwriteOnlyDroppedItems`
- Observability:
  - structured operation log (timestamp, items placed, skipped, overwritten).
  - exportable “run report” for bug reports.

### LLM maintenance note
- Ask LLM to propose algorithm refinements using real save samples (e.g., clustering by theme categories, route-optimized pickup lanes) and keep complexity bounded to maintain predictable runtime.

---

## Phase 5 — Quality & Reliability
- Unit tests for:
  - Theme parsing
  - Placement coordinate generation
  - Stack rules
  - Overwrite/skip behavior
- Integration tests for:
  - Read save → place items → write save → verify expected tiles
- Performance checks:
  - Large theme dump on full rectangle
- Usability testing:
  - New user completes dump in <5 min

### Technical implementation details
- Test organization:
  - parser tests in `NHSE.Tests` with fixture themes.
  - planner property-like tests for coordinate uniqueness and capacity limits.
- Reliability guardrails:
  - file write atomicity (write temp file then move/replace).
  - checksum comparison before/after for backup validation.
- Performance targets (initial guess):
  - Theme parse: <50 ms typical.
  - Plan generation: <100 ms for medium/large dumps.
  - Save apply + write: <2 seconds on typical hardware.

### LLM maintenance note
- Ask LLM to keep this section current with benchmark numbers, flaky test list, and prioritized reliability debt after each release candidate.

---

## Creative Expansion Paths (Make NHSE More Useful + Fun)
1. **Theme Remix Generator**
   - Blend two themes (e.g., “Zen + Neon Market”) with weighted ratios.
2. **Season/Event Presets**
   - Halloween, Cherry Blossom, Winter Market one-click packs.
3. **“Island Storyboard” Mode**
   - Place themed clusters in sequence (entrance → plaza → beach) instead of one rectangle.
4. **Smart Duplicate Finder**
   - Detect overrepresented items and suggest substitutions for variety.
5. **Friend Pickup Optimizer**
   - Arrange drops by pocket-efficient pickup order (stackables first, high-value grouping).
6. **Challenge Modes**
   - “Budget build”, “Tiny footprint”, or “No duplicate furniture” auto-generated constraints.
7. **Shareable Blueprint Export**
   - Export theme + layout recipe so others can replicate designs quickly.

### LLM ideation loop
- At the end of each milestone, ask LLM for:
  - 3 low-risk improvements,
  - 2 high-impact experiments,
  - 1 idea to delete (to fight feature bloat).

---

## Milestone Proposal
- **M1:** Theme Markdown format + parser + 3 demo themes.
- **M2:** Basic visual picker (name + image thumbnail + tags).
- **M3:** Dump planner + dry run overlay + overwrite toggle.
- **M4:** One-click execute with rolling backup/quick rollback.
- **M5:** Polish, docs, and community contribution guide.

### Milestone hardening checklist (apply each milestone)
- Update decisions made vs deferred.
- Record chosen libraries and rejected alternatives.
- Confirm data contract version changes.
- Add/refresh migration notes.
- Confirm benchmark + reliability status.

---

## Remaining Open Decisions
1. **Demo theme pack:** pick first 3 themes (recommend visual-first):
   - Cozy Market Street
   - Japanese Garden
   - Beach Resort Boardwalk
2. **Backup retention default:** keep last 3, 5, or 10 snapshots?
3. **Traffic lane preset:** every 3 tiles (default) or configurable first release?
4. **Asset source shortlist:** choose initial dataset(s) for implementation.

---

## Next Implementation Step
Create the first concrete artifacts:
1. `themes/` folder with 3 demo markdown files,
2. parser contract (`ThemeDefinition` model), and
3. WinForms wireframe flow mapped to existing NHSE screens.
