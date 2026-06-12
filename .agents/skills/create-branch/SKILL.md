---
name: create-branch
description: Create a Git branch from a Jira ticket using this repository's KNK branch naming convention. Use when the user asks to create, checkout, start, or prepare a branch for a Jira issue or ticket key such as "KNK-123", "create branch for KNK-123", "KNK-123 브랜치 만들어줘", or "start work on this Jira ticket". Prefer Atlassian MCP to verify the Jira issue and obtain its summary; fall back to a user-provided title when Jira is unavailable.
---

# Create Branch

## Purpose

Create one working branch from `dev` using the team convention:

```text
{tag}/{JIRA_KEY}-{title-slug}
```

Example:

```text
feat/KNK-12-add-google-login-button-ui
```

## Team Rules

- Branch from `dev` by default.
- Never push directly to `main` or `dev`.
- Use one of these tags: `feat`, `fix`, `docs`, `design`, `cicd`, `refactor`, `chore`.
- Keep the Jira key uppercase, for example `KNK-123`.
- Use kebab-case for the title slug.
- Prefer an English title slug. If the Jira summary is Korean and the meaning is clear, translate it concisely. If the meaning is unclear, ask the user for a short English branch title.

## Workflow

1. Extract the Jira key from the request. If there is no Jira key, ask for it.
2. Determine the branch tag.
   - Use the user's explicit tag when provided.
   - Otherwise infer from Jira issue type or summary: bug -> `fix`, documentation -> `docs`, UI/style -> `design`, CI/CD/deploy -> `cicd`, refactor -> `refactor`, dependency/config/maintenance -> `chore`, otherwise `feat`.
3. Verify the Jira issue when an Atlassian MCP/Jira tool is available.
   - Look up the issue by key.
   - Capture the issue summary, status, type, and assignee when available.
   - If the issue does not exist, do not create a branch; report that and ask the user to confirm the key.
   - If Jira access is unavailable, say so briefly and continue only when the user supplied enough title context, or ask for a title.
4. Generate the branch name with `scripts/create_branch.py`.
5. Check `git status --short` before creating the branch.
   - If the worktree has uncommitted changes, do not stash, reset, or discard them.
   - Create the branch with dirty changes only when the user explicitly wants to carry those changes over; pass `--allow-dirty` in that case.
6. Create the branch from `dev` with the script.
7. Report the created branch name and any Jira fallback or dirty-worktree caveat.

## Script Usage

Preview the branch name:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI"
```

Create the branch from `dev`:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create
```

If the branch already exists and the user wants to use it:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create \
  --checkout-existing
```

Only use `--allow-dirty` after the user confirms that existing uncommitted changes should move with the checkout.
