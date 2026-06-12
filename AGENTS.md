## Repository Knowledge Map

Treat this `AGENTS.md` as a compact map for agents, not as a project encyclopedia. Keep durable project knowledge in `../llm-wiki` and keep this file focused on where to look first.

### Source of Record

- `../llm-wiki/` is the LLM-maintained project knowledge repository.
- `../llm-wiki/index.md` is the entry point for finding relevant wiki pages.
- The wiki stores durable knowledge: architecture, features, APIs, screens, components, domain rules, decisions, open questions, and team conventions.

### When to Open the Wiki

Before non-trivial project work, read `../llm-wiki/index.md`, then open only the pages relevant to the task.

Reference the wiki first when the task involves:

- understanding existing architecture or feature behavior
- implementing or modifying a feature
- changing API usage, data fetching, auth, routing, forms, state management, or shared components
- fixing a bug where product behavior or domain rules matter
- refactoring code that may affect feature behavior
- answering questions about how the project works
- writing documentation, PR summaries, implementation plans, or technical explanations
- making decisions that should be remembered later

For simple mechanical edits, such as typo fixes, formatting-only changes, dependency cleanup, or isolated lint fixes, the wiki does not need to be checked unless the user asks.

### How to Use the Wiki

When wiki context is needed:

1. Read `../llm-wiki/index.md`.
2. Open the smallest set of relevant wiki pages.
3. Use the wiki to understand project context before editing code or writing project-facing documentation.
4. Verify behavior against the code when implementation details matter.
5. If the wiki conflicts with the code, mention the conflict instead of silently choosing one source.

## Shared Skills

- Shared team skills live in this harness repository under `.agents/skills/`.
