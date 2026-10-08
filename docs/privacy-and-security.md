# Privacy And Security

- Raw prompts and responses are disabled by design.
- User and private session identifiers never enter public snapshots.
- Public JSON is generated from explicit field allowlists.
- Unexpected files or sensitive-looking values stop publication.
- Runtime manifests cannot dynamically import arbitrary entrypoints.
- Every composed capability node undergoes permission checks.
- GitHub Pages is public and read-only; it is not an administration interface.
- Runtime credentials remain outside Git and are never copied into the publishing worktree.
- The public repository means every branch and commit history is visible; branch isolation prevents accidental deployment but is not a secrecy boundary.
