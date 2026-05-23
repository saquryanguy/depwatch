"""Reads and parses dependency files to extract package name and version ranges."""

import re
from pathlib import Path
from typing import Optional


def parse_requirements_line(line: str) -> Optional[tuple[str, str, str]]:
    """Parse a single requirements.txt line.

    Returns a tuple of (package_name, old_version, new_version) or None if unparseable.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # Match patterns like: requests==2.28.0, requests>=2.0,<3.0, requests~=2.28
    match = re.match(
        r"^([A-Za-z0-9_\-\.]+)\s*([=!<>~]+)\s*([A-Za-z0-9\.\*]+)",
        line,
    )
    if not match:
        return None

    name, operator, version = match.group(1), match.group(2), match.group(3)
    return name.lower().replace("-", "_"), operator, version


def read_requirements(path: str) -> dict[str, str]:
    """Read a requirements.txt file and return {package: version} mapping."""
    deps: dict[str, str] = {}
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Requirements file not found: {path}")

    for line in file_path.read_text().splitlines():
        result = parse_requirements_line(line)
        if result:
            name, _op, version = result
            deps[name] = version

    return deps


def diff_dependencies(
    old_deps: dict[str, str], new_deps: dict[str, str]
) -> list[dict[str, str]]:
    """Compare two dependency dicts and return list of changed packages.

    Each entry has keys: name, old_version, new_version, change_type.
    """
    changes = []

    all_packages = set(old_deps) | set(new_deps)
    for pkg in sorted(all_packages):
        old_ver = old_deps.get(pkg)
        new_ver = new_deps.get(pkg)

        if old_ver == new_ver:
            continue

        if old_ver is None:
            change_type = "added"
        elif new_ver is None:
            change_type = "removed"
        else:
            change_type = "updated"

        changes.append(
            {
                "name": pkg,
                "old_version": old_ver or "",
                "new_version": new_ver or "",
                "change_type": change_type,
            }
        )

    return changes
