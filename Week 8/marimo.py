import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    # this cell runs first
    # 24f3001383@ds.study.iitm.ac.in
    import marimo as mo
    x = 1

    # Data flow: this cell initializes and returns two values:
    #  - `mo`: the (intended) marimo/mario module alias that downstream cells can use to
    #          create UI widgets and render content.
    #  - `x`: a simple value (here `1`) that is passed as an argument to the next cell.
    # The returned tuple (`mo, x`) is provided as parameters to the subsequent @app.cell
    # functions by the marimo runtime in execution order.

    return mo, x


@app.cell
def _(x):
    # this cell runs second
    X= 2
    print(x)

    # Data flow: this cell receives `x` (the value produced by the first cell).
    # It may perform transformations or side effects (here it prints `x`) and
    # can return values if needed for later cells. In this implementation it
    # does not return anything, so no additional values are forwarded to the
    # next cell; marimo will continue invoking the next cell in sequence.
    return


@app.cell
def _(mo):
    # this cell runs third
    # Add interactive widget
    slider = mo.ui.slider(1, 100)
    # Create dynamic Markdown
    mo.md(f"{slider} {'🟢' * slider.value}")

    # Data flow: this cell receives `mo` (the module returned by the first cell)
    # and uses it to construct UI elements. The `slider` created here is owned by
    # the marimo UI runtime; user interaction with the slider updates UI state
    # within marimo. Any values produced by user interaction are managed inside
    # the marimo framework or can be emitted by callbacks if explicitly wired.
    # Because this cell does not return values, downstream behavior relies on
    # marimo's event/callback system rather than simple positional returns.

    return


if __name__ == "__main__":
    app.run()
