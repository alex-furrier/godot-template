# CLAUDE.md — Godot 4.5.1 Web starter

The default project is GDScript-first, Compatibility-rendered, extension-free and single-threaded for Web. Rust in `rust/` is **optional native-only** code. Do not install `godot/addons/my_ext/my_ext.gdextension` in the Web source tree: Godot may attempt to load it during import. Do not claim Rust Web support.

## Commands

- `make ci`: generator Python tests, Godot import, smoke, fixtures, input tests and Web export. Requires Godot 4.5.1, matching Web export templates and uv; not Rust or Docker.
- `make gdscript-ci`: Godot import, smoke, fixtures and input tests without export templates.
- `make export-web`: exports `build/web/index.html`; `make serve-web`: serves it locally on port 8000.
- `make native-smoke`: **opt-in Linux** Rust build, installs the GDExtension and tests RustSmoke. A tree with an installed native extension is not the clean default Web tree; use a fresh copy for Web checks.
- `uv run --no-sync python scripts/generate_starter.py --name "Game Name" /new/absolute/path`: creates an independent game only if the destination does not exist. Do not point it at the template checkout.
- `make dev-ci` and `make ci-local`: optional container/act wrappers; never required to run the default on a local Godot installation.

## Ownership

`godot/scripts/Main.gd` owns demo start/pause/restart, responsive drawing and 60 Hz `_physics_process` updates. `godot/adapters/input_adapter.gd` owns keyboard/touch movement and touch release. `godot/core/` retains typed state and deterministic fixture logic. Consumer game rules are not added to the template's generic `GameState`. `godot/export_presets.cfg` owns the Web export settings. `scripts/generate_starter.py` is the sole generator; old Python-project initialization is retired. Generated games are independent of this checkout and record base commit plus dirty-source truth.

Run generator tests before modifying generation and fixture/input tests when altering the corresponding gameplay seams. For actual Web claims, import/export a fresh generated project and inspect the running HTTP-served canvas; headless import and static assets alone cannot prove browser input, visuals or real-device behavior. See `docs/verification.md` for candidate evidence and gaps. Do not add public hosting or device acceptance claims without evidence.

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
