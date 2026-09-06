"""Verify branch creation against temporary repositories and a local remote."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "create_branch.py"
BRANCH = "docs/KNK-999-branch-test"


class CreateBranchTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="knk-branch-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.env = {
            **os.environ,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
        }
        self.remote = self.root / "origin"
        self.repo = self.root / "work"
        self.git(self.root, "init", "--initial-branch=dev", str(self.remote))
        (self.remote / "tracked.txt").write_text("initial\n")
        self.git(self.remote, "add", "tracked.txt")
        self.commit(self.remote, "initial")
        self.git(self.root, "clone", "--branch", "dev", str(self.remote), str(self.repo))
        self.initial = self.git(self.repo, "rev-parse", "HEAD")

    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=cwd, env=self.env, text=True,
            capture_output=True, check=True,
        )
        return result.stdout.strip()

    def commit(self, cwd: Path, message: str) -> None:
        self.git(
            cwd, "-c", "user.name=Branch test", "-c",
            "user.email=branch-test@example.invalid", "commit", "--allow-empty",
            "-m", message,
        )

    def run_script(self, *options: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--ticket", "KNK-999", "--tag", "docs",
             "--title", "Branch Test", "--json", *options],
            cwd=self.repo, env=self.env, text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def assert_dirty_rejected(self) -> None:
        status = self.git(self.repo, "status", "--porcelain")
        self.run_script("--create", success=False)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "dev")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), status)
        self.assertEqual(self.git(self.repo, "branch", "--list", BRANCH), "")

    def test_preview_does_not_fetch_or_create_branch(self) -> None:
        self.commit(self.remote, "new remote commit")
        result = json.loads(self.run_script().stdout)
        self.assertFalse(result["created"])
        self.assertFalse(result["checked_out"])
        self.assertEqual(result["branch"], BRANCH)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/dev"), self.initial)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "dev")
        self.assertEqual(self.git(self.repo, "branch", "--list", BRANCH), "")

    def test_default_fetches_remote_dev_without_moving_local_dev(self) -> None:
        self.commit(self.remote, "new remote commit")
        latest = self.git(self.remote, "rev-parse", "dev")
        self.assertNotEqual(latest, self.initial)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/dev"), self.initial)
        result = json.loads(self.run_script("--create").stdout)
        self.assertTrue(result["created"])
        self.assertFalse(result["dirty"])
        self.assertEqual(result["base_ref"], "refs/remotes/origin/dev")
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), BRANCH)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), latest)
        self.assertEqual(self.git(self.repo, "rev-parse", "dev"), self.initial)
        self.assertEqual(
            self.git(self.repo, "for-each-ref", f"refs/heads/{BRANCH}", "--format=%(upstream)"),
            "",
        )

    def test_untracked_file_blocks_creation(self) -> None:
        (self.repo / "untracked.txt").write_text("preserve me\n")
        self.assert_dirty_rejected()

    def test_unstaged_change_blocks_creation(self) -> None:
        (self.repo / "tracked.txt").write_text("unstaged\n")
        self.assert_dirty_rejected()

    def test_staged_change_blocks_creation(self) -> None:
        (self.repo / "tracked.txt").write_text("staged\n")
        self.git(self.repo, "add", "tracked.txt")
        self.assert_dirty_rejected()

    def test_allow_dirty_preserves_index_worktree_and_untracked_file(self) -> None:
        (self.repo / "tracked.txt").write_text("staged\n")
        self.git(self.repo, "add", "tracked.txt")
        (self.repo / "tracked.txt").write_text("unstaged\n")
        (self.repo / "untracked.txt").write_text("untracked\n")
        status = self.git(self.repo, "status", "--porcelain")
        result = json.loads(self.run_script("--create", "--allow-dirty").stdout)
        self.assertTrue(result["dirty"])
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), status)
        self.assertEqual(self.git(self.repo, "show", ":tracked.txt"), "staged")
        self.assertEqual((self.repo / "tracked.txt").read_text(), "unstaged\n")
        self.assertEqual((self.repo / "untracked.txt").read_text(), "untracked\n")

    def test_failed_fetch_does_not_fall_back_to_local_dev(self) -> None:
        self.git(self.repo, "remote", "set-url", "origin", str(self.root / "missing"))
        self.run_script("--create", success=False)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "dev")
        self.assertEqual(self.git(self.repo, "branch", "--list", BRANCH), "")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.initial)

    def test_explicit_local_base_works_without_remote(self) -> None:
        self.git(self.repo, "remote", "remove", "origin")
        self.git(self.repo, "branch", "-m", "main")
        result = json.loads(self.run_script("--create", "--base", "main").stdout)
        self.assertEqual(result["base_ref"], "main")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.initial)

    def test_existing_branch_needs_no_dev_or_remote(self) -> None:
        self.git(self.repo, "branch", "-m", "main")
        self.git(self.repo, "remote", "remove", "origin")
        self.git(self.repo, "branch", BRANCH)
        result = json.loads(self.run_script("--create", "--checkout-existing").stdout)
        self.assertFalse(result["created"])
        self.assertTrue(result["checked_out"])
        self.assertIsNone(result["base_ref"])
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), BRANCH)

    def test_existing_branch_does_not_switch_without_opt_in(self) -> None:
        self.git(self.repo, "branch", BRANCH)
        self.run_script("--create", success=False)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "dev")
        self.assertEqual(self.git(self.repo, "rev-parse", BRANCH), self.initial)


if __name__ == "__main__":
    unittest.main()
