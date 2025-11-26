#!/usr/bin/env python3
"""
Equipment Efficiency Rate - quarterly analysis
Generates visualizations and a simple trend forecast.
Includes contact email for verification: 24f3001383@ds.study.iitm.ac.in
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    # Quarterly data
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    efficiency = [69.77, 73.33, 76.05, 76.16]

    df = pd.DataFrame({"Quarter": quarters, "Efficiency": efficiency})
    df["QuarterIndex"] = np.arange(1, len(df) + 1)

    avg = df["Efficiency"].mean()
    print(f"Computed average efficiency: {avg:.2f}")

    # Trend plot with industry target line
    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 5))
    ax = sns.lineplot(data=df, x="QuarterIndex", y="Efficiency", marker="o")
    ax.set_xticks(df["QuarterIndex"]) 
    ax.set_xticklabels(df["Quarter"]) 
    ax.axhline(90, color="red", linestyle="--", label="Industry Target = 90")
    ax.set_ylim(0, max(95, df["Efficiency"].max() + 5))
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Equipment Efficiency (%)")
    ax.set_title("Quarterly Equipment Efficiency vs Industry Target")
    ax.legend()
    plt.tight_layout()
    trend_path = out_dir / "trend_vs_target.png"
    plt.savefig(trend_path)
    print(f"Saved trend plot to: {trend_path}")
    plt.close()

    # Simple linear regression forecast
    model = LinearRegression()
    X = df[["QuarterIndex"]].values
    y = df["Efficiency"].values
    model.fit(X, y)

    # Forecast next 8 quarters (total 12 quarters shown)
    future_index = np.arange(1, 13).reshape(-1, 1)
    preds = model.predict(future_index)

    # When will efficiency reach 90 according to linear trend?
    target = 90.0
    coef = model.coef_[0]
    intercept = model.intercept_
    if coef <= 0:
        reach_msg = "Linear trend does not increase; target 90 not reachable under current trend."
    else:
        quarters_needed = (target - intercept) / coef
        if quarters_needed <= 0:
            reach_msg = "Already at or above target according to model."
        else:
            reach_msg = f"Linear forecast reaches {target} at quarter index ~{quarters_needed:.1f} (1 = Q1)."

    print(reach_msg)

    # Forecast plot
    plt.figure(figsize=(8, 5))
    plt.plot(future_index, preds, label="Linear Forecast", marker="o")
    plt.scatter(df["QuarterIndex"], df["Efficiency"], color="black", label="Observed")
    plt.axhline(90, color="red", linestyle="--", label="Industry Target = 90")
    plt.xticks(future_index.flatten(), [f"Q{((i-1)%4)+1} (t={i})" for i in future_index.flatten()], rotation=45)
    plt.xlabel("Quarter (timeline)")
    plt.ylabel("Equipment Efficiency (%)")
    plt.title("Forecasted Equipment Efficiency (Linear Trend)")
    plt.legend()
    plt.tight_layout()
    forecast_path = out_dir / "forecast.png"
    plt.savefig(forecast_path)
    print(f"Saved forecast plot to: {forecast_path}")
    plt.close()

    # Save a small CSV summary
    summary_df = pd.DataFrame({"QuarterIndex": future_index.flatten(), "ForecastEfficiency": preds})
    summary_path = out_dir / "forecast_table.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Saved forecast table to: {summary_path}")

    # Print actionable recommendation (the solution)
    print("\nRecommended solution: implement predictive maintenance program")
    print("Contact (verification): 24f3001383@ds.study.iitm.ac.in")


if __name__ == "__main__":
    main()
