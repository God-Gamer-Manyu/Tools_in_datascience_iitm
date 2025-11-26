# Reveal.js Presentation (Week 8)

This folder contains a Reveal.js presentation. Files:

- `index.html` — main entry using Reveal.js from CDN
- `slides.md` — slides written in Markdown (includes fragments, code, math, and speaker notes)

How to open locally

1. Open `Week 8/index.html` in your browser (double-click or use a local server).

Publishing on GitHub Pages

Option A — Serve from the repository root (recommended):

1. Commit the files under `Week 8` and push to `main`:

```cmd
git add "Week 8"
git commit -m "Add Reveal.js presentation for Week 8"
git push origin main
```

2. In your GitHub repo, go to *Settings → Pages*.
3. Under *Source*, choose *Branch: main* and *Folder: / (root)*, then Save.
4. Your presentation will be available at:

```
https://<your-username>.github.io/<your-repo>/Week%208/index.html
```

Note: The space in folder name `Week 8` is URL-encoded as `%20` (or use `Week%208`).

Option B — Use `gh-pages` branch (alternative):

1. Create a `gh-pages` branch and copy the `Week 8` folder to the root of that branch, or set up a build step to publish just this folder.
2. In GitHub *Settings → Pages*, set source to `gh-pages` branch and root.
3. Visit `https://<your-username>.github.io/<your-repo>/Week%208/index.html`.

Tips

- If your repository uses a different default branch name, choose that branch as the Pages source.
- If you prefer a clean URL without `Week%208`, consider moving `index.html` and `slides.md` into a `docs/` folder or to the site root.
