"""Synchronise a canonical .gitignore across every repository in the workspace."""

from __future__ import annotations

import argparse
import sys
from collections import abc
from dataclasses import dataclass
from pathlib import Path

_TEMPLATE_FILENAME = "resources/gitignore-template.txt"


@dataclass(slots=True)
class SyncResult:
    created: list[Path]
    updated: list[Path]
    unchanged: list[Path]

    def log(self) -> None:
        """Emit a concise summary of the sync operation."""

        if self.created:
            print("[gitignore-sync] created:")
            for path in self.created:
                print(f"  - {path}")
        if self.updated:
            print("[gitignore-sync] updated:")
            for path in self.updated:
                print(f"  - {path}")
        if not self.created and not self.updated:
            print("[gitignore-sync] all repositories already match template")


def _discover_repositories(root: Path) -> list[Path]:
    """Return workspace directories that contain a git repository."""

    repos: list[Path] = []
    if (root / ".git").exists():
        repos.append(root)
    for candidate in root.iterdir():
        if not candidate.is_dir():
            continue
        if candidate.name.startswith("."):
            continue
        if (candidate / ".git").exists():
            repos.append(candidate)
    return sorted(repos)


def _load_template(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        msg = f"template file not found: {path}"
        raise FileNotFoundError(msg) from exc


def _sync_repo(repo: Path, template: str, *, dry_run: bool) -> str | None:
    """Apply the template to a single repository.

    Returns "created", "updated", or None if unchanged.
    """

    target = repo / ".gitignore"
    if not target.exists():
        if dry_run:
            return "created"
        target.write_text(template, encoding="utf-8")
        return "created"

    current = target.read_text(encoding="utf-8")
    if current == template:
        return None

    if dry_run:
        return "updated"

    target.write_text(template, encoding="utf-8")
    return "updated"


def _sync_all(
    repos: abc.Iterable[Path],
    template: str,
    *,
    dry_run: bool,
) -> SyncResult:
    created: list[Path] = []
    updated: list[Path] = []
    unchanged: list[Path] = []

    for repo in repos:
        outcome = _sync_repo(repo, template, dry_run=dry_run)
        if outcome == "created":
            created.append(repo)
        elif outcome == "updated":
            updated.append(repo)
        else:
            unchanged.append(repo)

    return SyncResult(created=created, updated=updated, unchanged=unchanged)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1].parent
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help=f"Workspace root containing repositories (default: {default_root})",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent / _TEMPLATE_FILENAME,
        help="Path to the canonical .gitignore template",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the repositories that would change without writing files",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary output (errors still propagate)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    template_path = args.template.resolve()

    template = _load_template(template_path)
    repos = _discover_repositories(root)
    result = _sync_all(repos, template, dry_run=args.dry_run)

    if not args.quiet:
        result.log()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
