"""Create an independent Godot starter from this checkout without modifying it."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORIES = {
    ".git", ".godot", ".import", ".venv", "__pycache__", ".cache",
    "target", "bin", "addons", "site", "evidence", "build", "dist", "reports",
}
EXCLUDED_NAMES = {
    ".env", ".secrets", "extension_list.cfg", "credentials.json",
    "service-account.json", "id_rsa", "id_ed25519", ".npmrc",
}
EXCLUDED_SUFFIXES = {".so", ".dll", ".dylib", ".pyc", ".uid", ".import", ".pem", ".key", ".p8", ".p12", ".keystore", ".mobileprovision", ".log"}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=SOURCE, text=True).strip()


def ignore_files(_directory, names):
    return {
        name for name in names
        if name in EXCLUDED_DIRECTORIES or name in EXCLUDED_NAMES
        or Path(name).suffix in EXCLUDED_SUFFIXES
        or name.startswith(".env.")
    }


def generate(destination: Path, name: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,79}", name):
        raise ValueError("--name must be 1–80 ASCII letters, digits, spaces, underscores or hyphens, starting with a letter or digit")
    if destination.is_symlink() or destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    destination = destination.resolve()
    if destination == SOURCE or SOURCE in destination.parents or destination in SOURCE.parents:
        raise ValueError("destination must be outside the template source")
    if not destination.parent.is_dir():
        raise ValueError("destination parent must already exist")
    base_commit = git("rev-parse", "HEAD")
    dirty_source = bool(git("status", "--porcelain", "--untracked-files=all"))
    destination.mkdir()
    try:
        for directory in ("godot", "rust"):
            shutil.copytree(SOURCE / directory, destination / directory, ignore=ignore_files, symlinks=True)
        if any(path.is_symlink() for path in destination.rglob("*")):
            raise ValueError("starter source contains a symbolic link; refusing a project with external references")
        shutil.copy2(SOURCE / "runtime.mk", destination / "Makefile")
        shutil.copy2(SOURCE / ".gitignore", destination / ".gitignore")
        project = destination / "godot" / "project.godot"
        text = project.read_text()
        marker = 'config/name="Godot Starter Pack"'
        if text.count(marker) != 1:
            raise ValueError("expected exactly one Godot project name")
        project.write_text(text.replace(marker, f"config/name={json.dumps(name)}"))
        provenance = {"base_commit": base_commit, "dirty_source": dirty_source}
        (destination / "source-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
        (destination / "README.md").write_text(
            f"# {name}\n\nIndependent Godot 4.5.1 GDScript starter. Open `godot/project.godot` "
            "in Godot or run `make ci` (requires Godot and matching Web export templates). "
            "Run `make export-web` then `make serve-web` for the local browser build. "
            "Keyboard: WASD/arrows to move, Enter/Space to start, P/Escape to pause, R to restart; "
            "touch: joystick and on-screen buttons. Rust is optional: `make native-smoke` needs a "
            "local Rust toolchain and Linux native library; it is not a Web feature.\n\n"
            f"Source base commit: {base_commit}. dirty_source: {str(dirty_source).lower()}. "
            "A dirty source includes uncommitted changes; the base commit alone does not reproduce this candidate. "
            "See `source-provenance.json`.\n"
        )
    except Exception:
        shutil.rmtree(destination)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Godot project display name")
    parser.add_argument("destination", type=Path, help="new destination directory; existing paths are refused")
    args = parser.parse_args()
    try:
        generate(args.destination, args.name)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Generated {args.name} at {args.destination.resolve()}")


if __name__ == "__main__":
    main()
