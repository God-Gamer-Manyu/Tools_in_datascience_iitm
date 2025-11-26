import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    # this cell runs first
    # 24f3001383@ds.study.iitm.ac.in
    import mario as mo
    x = 1


    return mo, x


@app.cell
def _(x):
    # this cell runs second
    X= 2
    print(x)
    return


@app.cell
def _(mo):
    # this cell runs third
    # Add interactive widget
    slider = mo.ui.slider(1, 100)
    # Create dynamic Markdown
    mo.md(f"{slider} {'🟢' * slider.value}")
    return


if __name__ == "__main__":
    app.run()
