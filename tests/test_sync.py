from __future__ import annotations

# ruff: noqa: SLF001,S101 (tests intentionally exercise private helpers and use pytest-style asserts)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from x_make_gitignore_sync_x import sync


def _make_repo(root: Path, name: str, *, gitignore: str | None = None) -> Path:
    repo = root / name
    repo.mkdir()
    (repo / ".git").mkdir()
    if gitignore is not None:
        (repo / ".gitignore").write_text(gitignore, encoding="utf-8")
    return repo


def test_sync_creates_missing_gitignore(tmp_path: Path) -> None:
    template = "# example\n__pycache__/\n"
    repo = _make_repo(tmp_path, "sample")

    result = sync._sync_all([repo], template, dry_run=False)

    assert result.created == [repo]
    assert (repo / ".gitignore").read_text(encoding="utf-8") == template


def test_sync_updates_existing_gitignore(tmp_path: Path) -> None:
    template = "# canonical\n"
    repo = _make_repo(tmp_path, "existing", gitignore="# old\n")

    result = sync._sync_all([repo], template, dry_run=False)

    assert result.updated == [repo]
    assert (repo / ".gitignore").read_text(encoding="utf-8") == template


def test_sync_dry_run_does_not_touch_disk(tmp_path: Path) -> None:
    template = "# canonical\n"
    repo = _make_repo(tmp_path, "dry", gitignore="# old\n")

    result = sync._sync_all([repo], template, dry_run=True)

    assert result.updated == [repo]
    assert (repo / ".gitignore").read_text(encoding="utf-8") == "# old\n"


def test_discovery_includes_root_git_repo(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    _make_repo(tmp_path, "child")

    repos = sync._discover_repositories(tmp_path)

    assert tmp_path in repos
    assert tmp_path / "child" in repos
