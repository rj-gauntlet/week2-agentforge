# Branching: MVP approval vs continued development

**Goal:** Keep the live MVP unchanged for approval while building Day 2+ features (e.g. LangSmith) on a separate branch.

---

## Branches

| Branch    | Purpose |
|----------|---------|
| **main** | Production / MVP approval. Deployed to Railway (API) and custom Web UI. **Do not push to `main` until MVP is approved.** |
| **develop** | Day 2+ work: LangSmith, observability, voice assistant, etc. Merge into `main` after approval. |

---

## Workflow

### Right now (Day 2 start)
1. You are on **develop** (created from current `main`).
2. Push the new branch once (if not already on GitHub):
   ```powershell
   git push -u origin develop
   ```
3. Do all new work on **develop**: LangSmith, tests, docs. Commit and push to `develop` only.

### When MVP is approved
1. Merge **develop** into **main**:
   ```powershell
   git checkout main
   git merge develop
   git push origin main
   ```
2. Railway (and your Web UI deploy) will redeploy from `main` with the new features.

### If you need a hotfix on the live MVP (before approval)
1. Create a short-lived branch from **main**, fix, merge back to **main**, push.
2. Optionally merge **main** into **develop** so develop stays in sync.

---

## Summary
- **LangSmith and all Day 2 work:** do it on **develop**.
- **After MVP approval:** merge **develop** → **main** and push; production updates in one go.
