"""Helpers for resolving the source checkout used by ``hermes update``.

When a developer keeps a second local checkout next to the current repo, we
prefer that checkout over GitHub so updates can come from a local ``main``
branch rather than the fork's remote.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _looks_like_git_checkout(path: Path) -> bool:
    """Return True when ``path`` appears to be a git checkout root."""
    return (path / ".git").exists()


def resolve_local_update_source_repo(project_root: Path | None = None) -> Optional[Path]:
    """Return a local repo to use as the update source, if available.

    Resolution order:
    1. ``HERMES_UPDATE_SOURCE_REPO`` when it points at a git checkout.
    2. A sibling checkout whose name matches the current repo minus a
       trailing ``-update`` suffix.
    3. A sibling ``hermes-agent`` checkout.
    4. The user's canonical development checkout under
       ``~/dev/-github/hermes-agent``.

    The helper is intentionally conservative: if no local checkout can be
    verified, callers should fall back to their normal remote-based update
    flow.
    """
    root = (project_root or Path(__file__).resolve().parent.parent).resolve()
    candidates: list[Path] = []

    env_value = os.getenv("HERMES_UPDATE_SOURCE_REPO", "").strip()
    if env_value:
        candidates.append(Path(env_value).expanduser())

    if root.name.endswith("-update"):
        candidates.append(root.with_name(root.name.removesuffix("-update")))

    candidates.append(root.with_name("hermes-agent"))
    candidates.append(Path.home() / "dev" / "-github" / "hermes-agent")

    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        if resolved == root or resolved in seen:
            continue
        seen.add(resolved)
        if _looks_like_git_checkout(resolved):
            return resolved

    return None
