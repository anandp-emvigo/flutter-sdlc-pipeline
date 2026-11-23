# flutter-sdlc-pipeline

An autonomous SDLC orchestrator plugin for **Flutter and Dart apps**, for Claude Code, Claude Cowork, and Cursor. Three commands — `/pipeline`, `/pipeline-parallel` and `/pipeline-all` — take a feature or bug from raw request to shipped PR through planning, review gauntlets, TDD execution, widget and device testing gates, mobile security review, docs, and ship.

This is the Flutter edition of [sdlc-pipeline](https://github.com/nithinemvigo/sdlc-pipeline), which targets web stacks. The pipeline is the same: an orchestrator that never writes code, specialist agents that each lead one part of the work, independent read-only reviewers that verify it, a hard plan-approval gate, and strict context discipline. What changes is that every agent works in Flutter terms from the start — widgets, providers and blocs, codegen, platform files, devices, stores — instead of web instructions with Flutter notes attached. Repos without a `pubspec.yaml` are refused at preflight.

Built on top of **superpowers**, **gstack**, and **claude-mem** — all three are required and must be installed first (see [Prerequisites](#prerequisites)).

## What's inside

| Component | Count | Purpose |
|---|---|---|
| Commands | 12 | `/pipeline` (features and bugs), `/pipeline-parallel` (parallel task waves), `/pipeline-all` (requirements-first, features only), and the BA requirements analysis: `/ba-run` (all phases) plus `/ba-start-analysis`, `/ba-analyse-gaps`, `/ba-triage-gaps`, `/ba-generate-stories`, `/ba-enrich-stories`, `/ba-sync-stories`, `/ba-generate-report`, and `/verify-acceptance` (checks a finished build against every acceptance criterion in the stories, report-only) |
| Agents | 20 | Specialist sub-agents: requirements-writer, BA analysts (requirement-analyst, gap-analysis-agent, story-generation-agent), distiller, planner, investigator, implementer, reviewers (code, security, eng, design, CEO), perf-tester, unit-tester, qa-tester, acceptance-verifier, adr-writer, doc-writer, ship-pr |
| Skills | 9 | BA analysis skills (requirement decomposition, gap identification/prioritisation/triage, story generation/enrichment, acceptance-criteria design, source discovery, quality validation) |
| Hooks | 2 | Token tracking and per-run token reports |
| Scripts | 12 | `check_plan.py` plan linter; `detect_stack.py` stack profile; `acceptance-checklist.py`; nine BA analysis scripts (state, gap register, story sync, validators, reports) |

The orchestrator never writes production code itself. It classifies your request, dispatches specialist agents, enforces quality gates, and only interrupts you for genuine decisions.

## Prerequisites

### Flutter SDK

The pipeline formats, analyzes, tests, profiles and compiles your app, so `flutter` (and `dart`) must be on `PATH` — or `fvm` when the repo pins a version with `.fvmrc`. `/pipeline` halts at preflight otherwise. Check with `flutter doctor`.

A running emulator, simulator, attached device or desktop target lets the QA gate walk scenarios end to end. Without one, the QA gate reports reduced evidence (`widget-level (no device)` or `NO_DEVICE`) and asks you before ship — never a silent pass.

This plugin also dispatches skills from three other plugins (see [Plugin dependencies](#plugin-dependencies)). All are **required** — `/pipeline` halts at preflight if any is missing. Install them **before** installing flutter-sdlc-pipeline.

### Python 3

The bundled hooks (`guard_context_budget.py`, `check_plan.py`) are Python scripts invoked by Claude at runtime. **Python 3.8+** must be available on your `PATH` before the hooks will run:

```bash
# verify
python3 --version   # should print Python 3.8 or later
```

If `python3` is not found, install it from [python.org/downloads](https://www.python.org/downloads/) or via your package manager:

```bash
# macOS (Homebrew)
brew install python

# Ubuntu / Debian
sudo apt install python3

# Windows (winget)
winget install Python.Python.3
```

> [!IMPORTANT]
> ⚠️ 5-minute prompt cache active. Set `ENABLE_PROMPT_CACHING_1H=1` and restart for ~25% lower cost.

### Plugin dependencies

1. **superpowers** — provides `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, and more.
   ```
   /plugin marketplace add obra/superpowers-marketplace
   /plugin install superpowers@superpowers-marketplace
   ```
2. **gstack** — provides `/office-hours`, `/spec`, and `/ship` used by the planning and ship stages. Installs via git clone + setup script (not a plugin marketplace) — see [garrytan/gstack](https://github.com/garrytan/gstack):
   ```
   git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
   cd ~/.claude/skills/gstack && ./setup
   ```
3. **claude-mem** — persistent memory across sessions; captures session context and injects it back into future runs.
   ```
   /plugin marketplace add thedotmack/claude-mem
   /plugin install claude-mem
   ```

If your team distributes plugins centrally, some may already be pre-installed — check with `/plugin` (and `~/.claude/skills/gstack` for gstack) before adding them.

## Installation

### Claude Code (CLI)

1. Add this repo as a marketplace:
   ```
   /plugin marketplace add ilyasarafathemvigo/flutter-sdlc-pipeline
   ```
2. Install the plugin:
   ```
   /plugin install flutter-sdlc-pipeline@flutter-sdlc-pipeline-dev
   ```
3. Restart Claude Code (or run `/reload-plugins` during development).
4. Verify: type `/` and confirm `/pipeline` appears.

### Claude Cowork / Claude Desktop

1. Open the **Customize** menu in the left sidebar, then the **Plugins** tab.
2. In **Personal plugins**, click **+** → **Add marketplace** → **Add from a repository**.
3. Paste: `https://github.com/ilyasarafathemvigo/flutter-sdlc-pipeline`
4. Once the marketplace syncs, click **Install** on **flutter-sdlc-pipeline**.
5. Start a new conversation for the plugin to take effect.

Note: hooks and sub-agents run in Cowork and Claude Code; in plain chat only skills are available.

### Cursor

1. Open Cursor **Settings** → **Plugins** (or **Rules & Memories → Plugins**, depending on version).
2. Click **Add Plugin** → **From Git repository**.
3. Paste: `https://github.com/ilyasarafathemvigo/flutter-sdlc-pipeline`
4. Cursor reads `.cursor-plugin/plugin.json` and installs the plugin.
5. Reload the Cursor window (`Cmd/Ctrl+Shift+P` → "Reload Window").

Alternatively, clone the repo and copy `agents/` and `commands/` into your project's `.cursor/` directory if your Cursor version doesn't support Git plugin installs.

### Updating

Marketplace installs don't auto-pull new commits. To get the latest version:

- **Claude Code:** `/plugin marketplace update flutter-sdlc-pipeline-dev`
- **Cowork/Desktop:** Customize → Plugins → find the marketplace → ⋯ menu → **Update**, then start a new session.

## Usage

### Example 1 — build a feature

```
/pipeline Add pull-to-refresh and an offline banner to the orders screen
```

What happens, step by step:

1. **Classify** — the orchestrator sizes the request (nano vs full run).
2. **Preferences** — you're asked three plain-language questions: bug or feature? test-first development? dedicated unit-test round?
3. **Plan** — the `planner` agent drafts an executable plan using superpowers `brainstorming`/`writing-plans` and gstack `/office-hours`/`/spec`.
4. **Plan review gauntlet** — `eng-reviewer` (codegen order, platform files, migrations, layering), `design-reviewer` (theme, states, adaptivity, accessibility), and `ceo-reviewer` (scope, store policy) review the plan in parallel.
5. **Your approval** — hard gate. No code is written until you approve the plan.
6. **Execute** — `implementer` agents build each task on a dedicated branch, test-first if you opted in.
7. **Quality gates** — `unit-tester` runs `flutter test --coverage` and fills unit, widget and state-test gaps on changed lines, `qa-tester` walks acceptance scenarios through `integration_test` on a device, then `code-reviewer` and `security-reviewer` (OWASP MASVS + STRIDE) run in parallel.
8. **Docs & ship** — `doc-writer` updates documentation, then `ship-pr` verifies all sign-offs, compiles every declared platform, and ships via gstack `/ship`.

### Example 2 — fix a bug

```
/pipeline Login button does nothing after the app resumes from background on Android
```

Bugs skip the planner: the `investigator` agent does root-cause analysis and produces a mini-plan in `docs/bugs/`, then the pipeline proceeds to execution and the same review gates.

### Example 3 — tiny change (nano tier)

```
/pipeline Fix the typo in the welcome banner
```

Nano changes skip planning and reviews entirely: `implementer` → `code-reviewer` → `ship-pr`. Fast path, still reviewed.

### Example 4 — start from an idea (requirements first)

```
/flutter-sdlc-pipeline:pipeline-all Let drivers scan a parcel barcode and mark it delivered, even offline
```

`/pipeline-all` is for features only. It first turns your idea (text, or a file path such as `docs/ideas/export.md`) into a requirements document based on the plugin's template, and asks you only about major gaps. You approve the document or ask for changes. A QA step runs next, and from the testing questions onward the run is the same as Example 1.

The requirements agent asks you only about major gaps (purpose, users, scope, main flow, security, other systems it connects to), then writes `docs/features/<slug>.requirements.md` from the plugin's template for you to approve or change. A feature that is genuinely too big for one run is split — only after you approve the split — into a few independent parts in `docs/features/<slug>/`, each complete on its own; each run builds one part, and once that PR is merged and deployed you run the next part with the command the run gives you. Next, the BA requirements analysis (Stage Q) breaks the approved requirements into atomic requirements, finds and ranks gaps, asks you about each gap (every Critical and High gap must be answered), and writes development stories with acceptance criteria: lean stories are appended to the requirements file, and the detailed stories (full acceptance criteria, edge cases, test data) go to `ba/<name>/stories/detailed_stories.md`, with an HTML report under `docs/features/.../ba/<name>/report/`. If you pause, run the same command again to resume. The planner then builds from the requirements and the detailed stories. Before the PR, an acceptance gate (Stage 5.85, the `acceptance-verifier` agent) checks that every acceptance criterion in the stories is proven by the build; you can also run it on its own with `/flutter-sdlc-pipeline:verify-acceptance <requirements file>`. BA folders created by an earlier plugin version (BA v0.5.1) are reconciled automatically on the next Stage Q run.

## How Flutter shapes each stage

At preflight, `scripts/detect_stack.py` reads `pubspec.yaml` and the repo layout and writes a **stack profile** to `.pipeline-stack.md` (git-excluded): toolchain (including FVM pins), platforms, flavors, state management, routing, codegen, localisation, storage, test setup, the exact format / analyze / codegen / test commands, and the files that are never parallel-safe. The profile travels by path with every dispatch, and the planner copies it into the plan's Global Constraints, so no agent ever opens `pubspec.yaml` to learn the toolchain. An empty repo gets a `greenfield` profile and a scaffolding Task 1 (`flutter create`).

| Stage | Agent | What it does in a Flutter app |
|---|---|---|
| Preflight | orchestrator | Halts without `flutter`/`dart` (or `fvm`) on `PATH`, or without a `pubspec.yaml` |
| Distil | `distiller` | Contract carries Screens (route, required states) and Platform capabilities tables beside the APIs the app calls |
| Plan | `planner` | Exports in Dart terms (classes, providers/blocs with state types, widget constructors, routes, sealed failures); tests named by level (unit, `testWidgets`, `bloc_test`/`ProviderContainer`, golden, `integration_test`); one task owns `pubspec.yaml`; `codegen: true` tasks; platform files and local-DB migrations explicit |
| Plan lint | `check_plan.py` | Knows drift, sqflite, Hive, Isar, ObjectBox, `shared_preferences` and secure-storage idioms; flags manifest-editing or codegen tasks marked `parallel-safe: true` |
| Plan review | `eng-reviewer` | Traces codegen ordering, platform substrate, schema migrations on existing installs, offline/failure paths, layering |
| | `design-reviewer` | Judges against the app's theme code, Material/Cupertino idiom, loading/empty/error/offline states, small screens, text scaling, `Semantics` |
| | `ceo-reviewer` | Scope plus store policy (permissions, payments, account deletion) and platform coverage |
| Execute | `implementer` | Runs `pub get`, `build_runner` and `gen-l10n` when needed; uses the repo's pump harness; never hand-edits generated files; never runs `--update-goldens` to get green |
| Unit-test gate | `unit-tester` | `flutter test --coverage`, changed lines checked against `lcov.info` |
| QA gate | `qa-tester` | `integration_test` scenarios on a device, emulator or desktop target, plus small-screen, large-text, back-gesture, offline and resume probes; falls back to clearly labelled widget-level checks |
| Code review | `code-reviewer` | Async `BuildContext`, disposal, rebuild cost, layout overflow, error/loading states, theme and l10n discipline |
| Security review | `security-reviewer` | OWASP MASVS + STRIDE: secrets in the binary, insecure storage, cleartext traffic, deep links, WebViews, exported components, permissions |
| Perf gate | `perf-tester` | Profile-mode frame timings, startup trace, `--analyze-size` |
| Acceptance gate | `acceptance-verifier` | Re-runs only the cited tests with the profile's command; an `integration_test` case with no device is `cannot_verify`, never `met` |
| Ship | `ship-pr` | Compile-only build per declared platform before the PR; version stays in `pubspec.yaml`; new permissions and platform-config changes called out in the PR |

Generated Dart files (`*.g.dart`, `*.freezed.dart`, `*.gr.dart`, `*.mocks.dart`, `*.config.dart`, `app_localizations*.dart`) are left out of review diffs. Golden images stay in, so reviewers see visual changes.

## Workflow

```
request
   │
   ▼
Stage 0    Classify (nano fast-path ─────────────────────┐)
Stage 0.5  Your preferences: bug/feature, TDD, unit tests │
   │                                                      │
   ├── FEATURE ──► Stage 1  Plan (planner)                │
   │               Stage 2  Plan reviews ∥ (eng/design/ceo)
   │               Stage 2.5  ★ YOU APPROVE THE PLAN ★    │
   │               Stage 2.7  ADR (if architecture changes)
   │                                                      │
   └── BUG ──────► Stage 1-B  Investigate (root cause)    │
   │                                                      │
   ▼                                                      │
Stage 3    Execute on dedicated branch (TDD if on) ◄──────┘
Stage 4    Unit/widget test gate (if opted in)
Stage 4.5  Device QA gate (if user-facing)
Stage 5    Code review ∥ Security review (OWASP MASVS + STRIDE)
Stage 5.5  Performance gate (only if perf-sensitive; profile mode)
Stage 5.8  Documentation
Stage 6    Compile every platform, ship PR (via gstack /ship)
```

`∥` = stages run in parallel. Token usage is tracked per run by the bundled hooks.

`/pipeline-all` runs a requirements-first version of the feature track:

```
idea (text and/or files)
   │
   ▼
Stage -1   Preflight (dependencies, Flutter SDK, stack profile)
Stage 0    Bug guard (bugs → /pipeline)
Stage R    Requirements (requirements-writer) ── ★ YOU APPROVE THE REQUIREMENTS ★
Stage Q    BA analysis (ba-run): atomic requirements → gaps → triage with you → stories
Stage 0.5  Your preferences: TDD, unit tests
Stage 0.8  Requirements → contract (distil if large, else copy)
Stage 1 →  Same as the FEATURE track above (plan, reviews, ★ plan approval ★, build, gates, docs)
Stage 5.85 Acceptance gate (acceptance-verifier): every story criterion proven, before the PR
Stage 6    Ship PR (via gstack /ship)
```

## Hard rules the pipeline enforces

- No production code before you approve the plan (Stage 2.5 is a hard gate).
- The orchestrator never writes code — only specialist agents do.
- Reviewers are read-only and report-only; they never "fix things while they're in there".
- No device is never a pass: missing device evidence is reported and needs your decision before ship.
- Implementers run one at a time (they share the working tree); reviewers run in parallel.

## License

MIT — free to use, modify, and distribute. See [`LICENSE`](LICENSE).

## Credits

The BA requirements analysis (`/ba-*` commands, the three BA agents, their skills, rules, schemas and scripts) is by the QA/BA team ([akhilvn-crypto/BA-Pipeline](https://github.com/akhilvn-crypto/BA-Pipeline), MIT), copied from v0.8.1 and adapted here to run inside `/pipeline-all` — see [`licenses/ba-requirements-LICENSE`](licenses/ba-requirements-LICENSE).
