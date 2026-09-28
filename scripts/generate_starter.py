"""Create an independent Godot starter from this checkout without modifying it."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
PROFILES = ("native-gdscript", "native-rust", "web-mobile")
GODOT_VERSION = "4.5.1"
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


def generate(destination: Path, name: str, profile: str = "web-mobile") -> None:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}; choose from {', '.join(PROFILES)}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,79}", name):
        raise ValueError("--name must be 1–80 ASCII letters, digits, spaces, underscores or hyphens, starting with a letter or digit")
    if destination.is_symlink() or destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    destination = destination.resolve()
    if destination == SOURCE or SOURCE in destination.parents or destination in SOURCE.parents:
        raise ValueError("destination must be outside the template source")
    if not destination.parent.is_dir():
        raise ValueError("destination parent must already exist")
    profile_files = {
        "web-mobile": [SOURCE / "profiles/web-mobile" / name for name in
                       ("project.godot", "Main.tscn", "Main.gd", "run_input_tests.gd", "Makefile")],
        "native-rust": [SOURCE / "profiles/native-rust" / name for name in
                        ("my_ext.gdextension", "Makefile")],
        "native-gdscript": [SOURCE / "runtime.mk"],
    }[profile]
    if any(path.is_symlink() or path.parent.is_symlink() for path in profile_files):
        raise ValueError("profile source contains a symbolic link")
    base_commit = git("rev-parse", "HEAD")
    dirty_source = bool(git("status", "--porcelain", "--untracked-files=all"))
    destination.mkdir()
    try:
        shutil.copytree(SOURCE / "godot", destination / "godot", ignore=ignore_files, symlinks=True)
        if profile == "web-mobile":
            overlay = SOURCE / "profiles" / "web-mobile"
            for source, target in (("project.godot", "project.godot"), ("Main.tscn", "scenes/Main.tscn"), ("Main.gd", "scripts/Main.gd"), ("run_input_tests.gd", "scripts/run_input_tests.gd")):
                shutil.copy2(overlay / source, destination / "godot" / target)
            shutil.copy2(overlay / "Makefile", destination / "Makefile")
        else:
            (destination / "godot" / "export_presets.cfg").unlink()
            (destination / "godot" / "scripts" / "run_input_tests.gd").unlink(missing_ok=True)
            if profile == "native-rust":
                shutil.copytree(SOURCE / "rust", destination / "rust", ignore=ignore_files, symlinks=True)
                shutil.copy2(SOURCE / "profiles" / "native-rust" / "my_ext.gdextension", destination / "rust" / "my_ext.gdextension")
                shutil.copy2(SOURCE / "profiles" / "native-rust" / "Makefile", destination / "Makefile")
            else:
                shutil.copy2(SOURCE / "runtime.mk", destination / "Makefile")
                (destination / "godot" / "scripts" / "native_smoke_test.gd").unlink()
        if profile == "web-mobile":
            (destination / "godot" / "scripts" / "native_smoke_test.gd").unlink()
        if any(path.is_symlink() for path in destination.rglob("*")):
            raise ValueError("starter source contains a symbolic link; refusing a project with external references")
        shutil.copy2(SOURCE / ".gitignore", destination / ".gitignore")
        project = destination / "godot" / "project.godot"
        text = project.read_text()
        marker = 'config/name="Godot Starter Pack"'
        if text.count(marker) != 1:
            raise ValueError("expected exactly one Godot project name")
        project.write_text(text.replace(marker, f"config/name={json.dumps(name)}"))
        provenance = {"base_commit": base_commit, "dirty_source": dirty_source, "profile": profile, "godot_version": GODOT_VERSION}
        (destination / "source-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
        commands = {
            "web-mobile": "Run `make ci` (Godot 4.5.1 and matching Web export templates), then `make serve-web` for the local browser build. WASD/arrows or touch move; Enter/Space starts, P/Escape pauses, R restarts. This profile is extension-free and single-threaded.",
            "native-gdscript": "Run `make ci` with Godot 4.5.1 only (no Rust, Web export templates or Docker). Hold D or Right to advance the tick in the native scene.",
            "native-rust": "On Linux, run `make ci` with Godot 4.5.1 and Rust (cargo, rustfmt and clippy). This builds and installs the native extension before the mandatory RustSmoke probe. `make native-negative` must fail its internal missing-extension probe on a fresh output. Do not use this profile for Web export.",
        }
        (destination / "README.md").write_text(
            f"# {name}\n\nIndependent Godot {GODOT_VERSION} {profile} starter. Open `godot/project.godot` in Godot. "
            + commands[profile] + "\n\n"
            + f"Source base commit: {base_commit}. dirty_source: {str(dirty_source).lower()}. "
            "A dirty source includes uncommitted changes; the base commit alone does not reproduce this candidate. "
            "See `source-provenance.json`.\n"
        )
    except Exception:
        shutil.rmtree(destination)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Godot project display name")
    parser.add_argument("--profile", choices=PROFILES, default="web-mobile", help="runtime profile (default: web-mobile for existing callers)")
    parser.add_argument("destination", type=Path, help="new destination directory; existing paths are refused")
    args = parser.parse_args()
    try:
        generate(args.destination, args.name, args.profile)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Generated {args.name} ({args.profile}) at {args.destination.resolve()}")


if __name__ == "__main__":
    main()
