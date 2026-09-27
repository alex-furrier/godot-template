# Optional container checks

The current Godot Web starter does not need a container. For the template checkout, `make dev-ci` runs CI through `docker/docker-compose.yml`; `make ci-local` is an optional Docker/act wrapper around `.github/workflows/ci.yml`. These commands are not installed by the generator in a consumer game. Neither command is required for a local Godot 4.5.1 installation.

This page previously described a Python-project `make init` and automatic Podman selection. That initializer was retired; there is no `make init` or `make container-info` target. Create an independent Godot game with the generator in [getting started](getting-started.md). The generated Makefile contains only the shared runtime commands.

Container checks were not run for the Web starter verification. Use [tooling](tooling.md) for the tested local commands and [verification](verification.md) for remaining browser/device gaps.
