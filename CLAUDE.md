# CLAUDE.md — Godot 4.5.1 multi-profile starter

The source checkout launches native GDScript. The generator's no-flag default remains `web-mobile` for existing callers; explicit profiles are `native-gdscript`, `native-rust` and `web-mobile`. The Web output uses Compatibility, single-threaded export and no Rust. Do not install a native extension descriptor in clean native GDScript or Web projects. Do not claim Rust Web support.

## Commands

- Source checkout `make ci`: Godot import/smoke/fixtures and uv-backed generator tests; no Rust, Docker or Web templates.
- `uv run --no-sync python scripts/generate_starter.py --name "Game Name" --profile native-gdscript /new/absolute/path`: creates an independent game at a new destination. Omit `--profile` for Web. Do not point it at the checkout or an existing game.
- Generated `make ci`: profile-specific commands. Native GDScript needs only Godot; Web needs matching export templates and has `make export-web`/`make serve-web`; Linux x86_64 Rust needs cargo/rustfmt/clippy and mandatory RustSmoke registration. The Rust CI job runs independently on PRs.
- `make dev-ci` and `make ci-local`: optional container/act wrappers, not consumer requirements.

## Ownership

`godot/core/` owns shared typed state and fixtures. Native checkout `godot/scripts/Main.gd` is the minimal tick demo; `profiles/web-mobile/` owns portrait lifecycle scene/project/input tests and Web runtime commands. `godot/adapters/input_adapter.gd` owns keyboard/touch movement and touch release. `profiles/native-rust/` owns the Linux descriptor and runtime commands; the descriptor is copied into the generated Godot tree only after native library build. `scripts/generate_starter.py` alone generates independent consumers with profile/version/base commit/dirty-source provenance. The obsolete Python-project initializer remains retired.

Run generator tests before editing generation and fixture/input tests when altering corresponding gameplay seams. For Web claims, import/export a fresh generated project and inspect the running HTTP-served canvas; headless import and static assets do not prove browser input, visuals or devices. See `docs/verification.md`. Do not add public hosting or device acceptance claims without evidence.

## Plan Persistence

Plans are stored in `.ai/plans/` with the format:
```
.ai/plans/$TIMESTAMP-$description/
  Spec.md           # Requirements and design decisions
  Implementation.md # Concrete file implementations
  Todo.md           # Task checklist with phases
```

### Creating a Plan
When asked to plan a feature, create a timestamped directory:
```bash
mkdir -p .ai/plans/$(date +%Y-%m-%d)-feature-name
```

Then create `Spec.md`, `Implementation.md`, and `Todo.md` with:
- **Spec.md**: Goals, non-goals, design decisions, acceptance criteria
- **Implementation.md**: Concrete code examples and file contents
- **Todo.md**: Phased task checklist

### Resuming Work

When asked to "resume" or continue work:

1. **Check the current branch**: `git branch --show-current`
2. **Review recent commits**: `git log --oneline -5`
3. **Find matching plan**: Look in `.ai/plans/` for plans matching the branch name or recent commit descriptions
4. **Read the plan files**:
   ```bash
   ls .ai/plans/
   cat .ai/plans/$MATCHING_PLAN/Todo.md
   ```
5. **Identify incomplete tasks** from `Todo.md` (items still marked `[ ]`)
6. **Continue implementation** from where it left off

Example resume workflow:
```bash
# 1. Check context
git branch --show-current
git log --oneline -5

# 2. Find plan
ls .ai/plans/

# 3. Read plan status
cat .ai/plans/2026-01-16-gdscript-first-template/Todo.md

# 4. Continue from first incomplete task
```

### Plan Naming Convention

Use descriptive names that match branch names when possible:
- `2026-01-16-gdscript-first-template/` → branch `feat/gdscript-first-template`
- `2026-01-16-dev-environment-validation-loop/` → branch `feat/validation-loop`
