import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Reproducible results
np.random.seed(42)

# Generate realistic synthetic data for support efficiency analysis
teams = ['Team A', 'Team B', 'Team C', 'Team D']
priorities = ['Low', 'Medium', 'High']
rows = []

# Simulate resolution times in minutes with sensible differences across teams/priorities
for team in teams:
    for priority in priorities:
        # base scale differs per team to reflect varying efficiency
        base = {
            'Team A': 30,
            'Team B': 45,
            'Team C': 25,
            'Team D': 60
        }[team]
        # priority multiplier (High priority resolved faster on average)
        pm = {'Low': 1.3, 'Medium': 1.0, 'High': 0.7}[priority]
        # produce 120 samples per (team, priority)
        mu = np.log(base * pm)
        sigma = 0.4 + 0.05 * (teams.index(team))
        samples = np.random.lognormal(mean=np.log(base * pm), sigma=sigma, size=120)
        for s in samples:
            rows.append({'Team': team, 'Priority': priority, 'ResolutionTime': max(1.0, s)})

# Build DataFrame
df = pd.DataFrame(rows)

# Styling
sns.set_style('whitegrid')
sns.set_context('talk', font_scale=0.9)
palette = sns.color_palette('Set2')

# Create figure with explicit DPI so figsize * dpi = exact pixels (8in * 64dpi = 512px)
fig, ax = plt.subplots(figsize=(8, 8), dpi=64)
fig.patch.set_facecolor('white')

# Draw violinplot on the explicit axes
sns.violinplot(
    data=df,
    x='Team',
    y='ResolutionTime',
    hue='Priority',
    palette=palette,
    cut=0,
    inner='quartile',
    bw=.2,
    dodge=True,
    ax=ax
)

# Improve y-axis scale for interpretability
ax.set_yscale('log')
ax.set_ylabel('Resolution Time (minutes, log scale)')
ax.set_xlabel('Support Team')
ax.set_title('Support Resolution Time Distribution by Team and Priority')

# Tidy up legend
ax.legend(title='Priority')

# Add a horizontal line for a target SLA (e.g., 60 minutes) and annotate using axes coordinates
ax.axhline(60, color='gray', linestyle='--', linewidth=1)
ax.text(0.02, 0.97, 'SLA = 60 min', color='gray', fontsize=10, transform=ax.transAxes, va='top')

plt.tight_layout()

# Save with exact pixels: fig size (inches) * dpi => pixels. Avoid bbox_inches='tight' which crops padding.
fig.savefig('chart.png', dpi=64)
plt.close(fig)

print('chart.png generated (exact 512x512 pixels expected).')