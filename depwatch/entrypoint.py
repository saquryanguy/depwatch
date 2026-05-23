"""Main entrypoint for the depwatch GitHub Action.

Orchestrates: reading deps -> fetching changelogs -> analyzing -> posting comment.
"""

import os
import sys

from depwatch.dependency_reader import read_requirements, diff_dependencies
from depwatch.changelog_fetcher import get_changelog
from depwatch.version_parser import extract_sections_between
from depwatch.diff_analyzer import summarize_breaking_changes
from depwatch.pr_comment import build_comment_body, post_pr_comment


def run(
    old_requirements: str,
    new_requirements: str,
    repo: str,
    pr_number: int,
) -> None:
    """Run depwatch analysis and post a PR comment."""
    print(f"[depwatch] Reading dependency changes between {old_requirements} and {new_requirements}")

    old_deps = read_requirements(old_requirements)
    new_deps = read_requirements(new_requirements)
    changes = diff_dependencies(old_deps, new_deps)

    updated = [c for c in changes if c["change_type"] == "updated"]
    if not updated:
        print("[depwatch] No updated dependencies found. Nothing to report.")
        return

    results = []
    for change in updated:
        pkg = change["name"]
        old_ver = change["old_version"]
        new_ver = change["new_version"]

        print(f"[depwatch] Fetching changelog for {pkg} ({old_ver} -> {new_ver})")
        changelog = get_changelog(pkg)
        if not changelog:
            print(f"[depwatch] No changelog found for {pkg}, skipping.")
            continue

        sections = extract_sections_between(changelog, old_ver, new_ver)
        summary = summarize_breaking_changes(pkg, sections)
        results.append((pkg, old_ver, new_ver, summary))

    if not results:
        print("[depwatch] No changelog data available for updated packages.")
        return

    comment = build_comment_body(results)
    post_pr_comment(repo, pr_number, comment)
    print("[depwatch] Comment posted successfully.")


def main() -> None:
    """Entry point reading configuration from environment variables."""
    old_req = os.environ.get("DEPWATCH_OLD_REQUIREMENTS", "requirements.old.txt")
    new_req = os.environ.get("DEPWATCH_NEW_REQUIREMENTS", "requirements.txt")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    pr_number_str = os.environ.get("DEPWATCH_PR_NUMBER", "")

    if not repo:
        print("[depwatch] ERROR: GITHUB_REPOSITORY env var is required.", file=sys.stderr)
        sys.exit(1)

    if not pr_number_str.isdigit():
        print("[depwatch] ERROR: DEPWATCH_PR_NUMBER must be a valid integer.", file=sys.stderr)
        sys.exit(1)

    run(old_req, new_req, repo, int(pr_number_str))


if __name__ == "__main__":
    main()
