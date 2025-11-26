# 24f3001383@ds.study.iitm.ac.in
"""
Marimo demo script
- Uses `import marimo as mo` per your request
- Demonstrates variable dependencies between cells (sections), an interactive slider widget,
  dynamic markdown output, and comments documenting data flow.

Notes about marimo API:
- This file assumes a simple, component-style API on `marimo` (e.g., `App`, `Slider`, `Markdown`).
- If your local `marimo` package exposes different names, adapt the widget/registration calls accordingly.
"""

import numpy as np
import marimo as mo

# -------------------------
# Cell / Section 1 — base data
# -------------------------
# Data flow: create the base array here. Downstream sections (widgets and views)
# read this `base` variable and create derived data from it (e.g., `scaled`).
# This models the notebook-style dependency: base -> scaled -> summary.
base = np.array([12, 15, 13, 20, 18, 17, 22, 19, 16, 14])
# Example interpretation: inventory levels or supplier lead time samples.

# -------------------------
# Cell / Section 2 — UI & interactivity
# -------------------------
# Data flow: this section reads `base` and produces a derived variable `scaled` when the slider changes.
# The slider's callback updates the `scaled` state and then updates the displayed markdown.

# Create a Marimo application (container for widgets/views)
app = mo.App(title='Marimo — Supply Chain Demo')

# Create a Markdown view that will be updated dynamically
md = mo.Markdown('Use the slider to change the multiplier and see live stats.')

# Initialize scaled so other sections can use it before any interaction
scaled = base * 1

# Slider callback updates `scaled` and the markdown view
def on_multiplier_change(value):
    global scaled
    # Update derived data
    scaled = base * value
    # Build dynamic markdown content
    text = (
        f"**Multiplier:** {value}\n\n"
        f"**Mean of scaled data:** {scaled.mean():.2f}\n\n"
        f"**Min / Max:** {int(scaled.min())} / {int(scaled.max())}\n\n"
        f"**First three values:** {list(scaled[:3])}"
    )
    # Update the Markdown view in the app
    md.set_text(text)

# Create a slider (min 1, max 10) and attach the callback
slider = mo.Slider(min=1, max=10, value=1, description='Multiplier')
slider.on_change(on_multiplier_change)

# Register widgets/views with the app
app.add(slider)
app.add(md)

# -------------------------
# Cell / Section 3 — downstream summary / analysis
# -------------------------
# Data flow: reads the latest `scaled` variable (updated by the slider callback above)
# and provides a small summary view. This demonstrates that downstream code can
# use the variable mutated by the interactive callback.
summary_md = mo.Markdown('Summary will appear here after interaction.')

def update_summary_view():
    try:
        m = float(scaled.mean())
        s = float(scaled.std())
        cnt = int(len(scaled))
        text = (
            "### Current scaled summary\n\n"
            f"- Mean: {m:.2f}\n"
            f"- Std dev: {s:.2f}\n"
            f"- Count: {cnt}\n\n"
            "_This summary reads the global variable `scaled` that is updated by the slider._"
        )
    except NameError:
        text = 'The variable `scaled` is not defined. Please interact with the slider.'
    summary_md.set_text(text)

# Hook the summary updater to slider changes so it refreshes automatically
slider.on_change(lambda v: (on_multiplier_change(v), update_summary_view()))

# Also add the summary to the app layout
app.add(summary_md)

# -------------------------
# Run the app
# -------------------------
if __name__ == '__main__':
    # Initialize views with defaults
    on_multiplier_change(slider.value)
    update_summary_view()

    # Start the Marimo app server / UI
    # The exact call may depend on your `marimo` runtime; `run()` is typical.
    try:
        app.run()
    except AttributeError:
        print('Started marimo app (placeholder). If `marimo.App.run()` is different, adapt this call.')
