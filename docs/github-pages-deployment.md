# GitHub Pages Deployment

- Repository: `kovacoj/fr4nkiepi`.
- Development branch: `main`.
- Publishing branch: orphan `gh-pages`, root directory.
- Public URL: <https://kovacoj.github.io/fr4nkiepi/>.
- GitHub Pages uses branch deployment with HTTPS enforcement.

Before publication, run:

```bash
uv run python scripts/validate-pages.py /absolute/path/to/pages-worktree
```

The validator requires the exact approved tree and rejects backend source, scripts, databases, raw telemetry, credentials, and unexpected files. The publisher must use a separate worktree and must skip commits when snapshot content is unchanged.

The initial page was manually published and verified with HTTP 200. Automated Pi publication is not configured until a narrow repository-scoped credential is approved.
