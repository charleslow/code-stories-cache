# code-stories-cache

A personal cache of AI-generated code stories for public repositories I want to study. Stories are narrative-driven walkthroughs that explain how codebases work, generated using [code-stories](https://github.com/charleslow/code-stories).

## Cached Code Stories

- [Why GoClaw Requires an API Key (No Claude Code CLI Support)](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=goclaw-claude-code)
- [How PicoClaw Runs on Your Claude Code Subscription](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=picoclaw-claude-code)
- [Is PicoClaw Safe on a Remote Instance? A Security Audit Tour](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=picoclaw-security)
- [Picoclaw's Native Telegram Integration](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=picoclaw-telegram)
- [How PicoClaw Learns from User Interactions](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=picoclaw-user-learning)
- [How Strawberry Detects Hallucinations: From EDFL Theory to MCP Tools](https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story=pythea-strawberry-hallucination-detection)

## What is a Code Story?

A code story transforms a natural language question about a codebase into an interactive, chapter-by-chapter tour with real code snippets and prose explanations. Each story is a self-contained JSON file.

## Generating a Story

Stories are generated using the `code-stories` CLI with the `--repo` flag for public GitHub repositories:

```bash
cd /path/to/code-stories-cache
npx code-stories --repo user/repo "How does the authentication flow work?"
```

This creates:
- `stories/{uuid}.json` — the story file
- `stories/manifest.json` — an index of all stories

## Viewing Stories

Stories can be viewed using the deployed viewer at [charleslow.github.io/code-stories](https://charleslow.github.io/code-stories/).

**Using a direct raw URL:**
```
https://charleslow.github.io/code-stories/?url=https://raw.githubusercontent.com/charleslow/code-stories-cache/main/stories/{story-id}.json
```

**Using the repo shorthand:**

```
https://charleslow.github.io/code-stories/?repo=charleslow/code-stories-cache&story={story-id}
```

Note that the `story-id` is the name of the json file.

## Workflow

1. Pick a public repo to study
2. Generate a story: `npx code-stories --repo user/repo "Your question"`
3. Commit and push the story
4. Add a link to the README under Cached Code Stories
4. View it in the browser using the links above
