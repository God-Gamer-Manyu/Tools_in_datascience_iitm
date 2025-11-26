# Reveal.js Presentation (served from `docs/`)

This folder contains the Reveal.js presentation. Files:

- `index.html` — main entry using Reveal.js from CDN
- `slides.md` — slides written in Markdown (includes fragments, code, math, and speaker notes)

How to open locally

1. Open `docs/index.html` in your browser (double-click or use a local server).

Publishing on GitHub Pages using `docs/` folder

1. Commit the `docs/` folder and push to `main`:

```cmd
git add docs
git commit -m "Publish Reveal.js presentation via docs/"
git push origin main
```

2. In your GitHub repo, go to *Settings → Pages*.
3. Under *Source*, choose *Branch: main* and *Folder: /docs*, then Save.
4. Your presentation will be available at:

```
https://<your-username>.github.io/<your-repo>/
```

And the presentation itself will be at:

```
https://<your-username>.github.io/<your-repo>/index.html
```

(You can link directly to `/slides.md` if desired.)

Notes

- Using the `docs/` folder is convenient because GitHub Pages serves it directly from the `main` branch.
- If you want the presentation at the repository root path without `index.html`, keep this `index.html` as the repository root page.
