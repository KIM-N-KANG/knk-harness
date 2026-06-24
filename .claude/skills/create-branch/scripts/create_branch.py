#!/usr/bin/env python3
"""Create or preview a team-standard Jira branch name."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass


TAGS = ("feat", "fix", "docs", "design", "cicd", "refactor", "chore")
TICKET_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


@dataclass
class Result:
    branch: str
    created: bool
    checked_out: bool
    base_ref: str | None
    dirty: bool


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=check,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_output(args: list[str]) -> str:
    return run_git(args).stdout.strip()


def normalize_ticket(ticket: str) -> str:
    value = ticket.strip().upper()
    if not TICKET_RE.fullmatch(value):
        raise ValueError(f"Invalid Jira key: {ticket!r}. Expected a key like KNK-123.")
    return value


def slugify(title: str, max_length: int) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_title.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if max_length > 0 and len(slug) > max_length:
        slug = slug[:max_length].strip("-")
    if not slug:
        raise ValueError(
            "Title slug is empty after ASCII normalization. Provide a short English title."
        )
    return slug


def branch_exists(branch: str) -> bool:
    proc = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False)
    return proc.returncode == 0


def resolve_base(base: str) -> str:
    local = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{base}"], check=False)
    if local.returncode == 0:
        return base

    remote = run_git(
        ["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{base}"],
        check=False,
    )
    if remote.returncode == 0:
        return f"origin/{base}"

    raise ValueError(f"Base branch {base!r} was not found locally or at origin/{base}.")


def is_dirty() -> bool:
    return bool(git_output(["status", "--porcelain", "-uno"]))


def build_branch(ticket: str, tag: str, title: str, max_slug_length: int) -> str:
    key = normalize_ticket(ticket)
    if tag not in TAGS:
        raise ValueError(f"Invalid tag: {tag!r}. Expected one of: {', '.join(TAGS)}.")
    return f"{tag}/{key}-{slugify(title, max_slug_length)}"


def create_branch(
    branch: str,
    base: str,
    allow_dirty: bool,
    checkout_existing: bool,
) -> Result:
    git_output(["rev-parse", "--show-toplevel"])
    dirty = is_dirty()
    base_ref = resolve_base(base)

    if dirty and not allow_dirty:
        raise ValueError(
            "Worktree has uncommitted changes. Re-run with --allow-dirty only if the "
            "user wants those changes to move with the checkout."
        )

    if branch_exists(branch):
        if checkout_existing:
            run_git(["checkout", branch])
            return Result(branch, created=False, checked_out=True, base_ref=base_ref, dirty=dirty)
        raise ValueError(f"Branch already exists: {branch}")

    run_git(["checkout", "-b", branch, base_ref])
    return Result(branch, created=True, checked_out=True, base_ref=base_ref, dirty=dirty)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or preview a Git branch name from a Jira ticket."
    )
    parser.add_argument("--ticket", required=True, help="Jira issue key, for example KNK-123.")
    parser.add_argument("--tag", required=True, choices=TAGS, help="Branch tag.")
    parser.add_argument(
        "--title",
        required=True,
        help="Short branch title. Prefer English; Jira summaries may be shortened.",
    )
    parser.add_argument("--base", default="dev", help="Base branch to create from. Default: dev.")
    parser.add_argument(
        "--max-slug-length",
        type=int,
        default=60,
        help="Maximum title slug length. Use 0 for no limit.",
    )
    parser.add_argument("--create", action="store_true", help="Create and checkout the branch.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow branch creation when the worktree has uncommitted changes.",
    )
    parser.add_argument(
        "--checkout-existing",
        action="store_true",
        help="Checkout the branch if it already exists.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def print_result(result: Result, as_json: bool) -> None:
    data = {
        "branch": result.branch,
        "created": result.created,
        "checked_out": result.checked_out,
        "base_ref": result.base_ref,
        "dirty": result.dirty,
    }
    if as_json:
        print(json.dumps(data, ensure_ascii=False, sort_keys=True))
        return

    print(f"branch={result.branch}")
    print(f"created={str(result.created).lower()}")
    print(f"checked_out={str(result.checked_out).lower()}")
    if result.base_ref:
        print(f"base_ref={result.base_ref}")
    print(f"dirty={str(result.dirty).lower()}")


def main() -> int:
    args = parse_args()
    try:
        branch = build_branch(args.ticket, args.tag, args.title, args.max_slug_length)
        if args.create:
            result = create_branch(
                branch,
                base=args.base,
                allow_dirty=args.allow_dirty,
                checkout_existing=args.checkout_existing,
            )
        else:
            result = Result(
                branch=branch,
                created=False,
                checked_out=False,
                base_ref=None,
                dirty=False,
            )
        print_result(result, args.json)
        return 0
    except (subprocess.CalledProcessError, ValueError) as exc:
        message = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print(f"error={message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
