# visualizer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load summarized CSV
df = pd.read_csv("output/renewable_summary.csv")

# Convert to numeric
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df["Growth (%)"] = pd.to_numeric(df["Growth (%)"], errors="coerce")

# Average growth per source
avg_growth = df.groupby("Source")["Growth (%)"].mean().sort_values(ascending=False)

# Plot average growth
plt.figure(figsize=(10, 5))
sns.barplot(x=avg_growth.index, y=avg_growth.values, palette="crest")
plt.title("Average Growth Rate by Renewable Source")
plt.ylabel("Growth (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/avg_growth_by_source.png")
plt.close()

# Time trend of key renewables
pivot = df.pivot_table(index="Year", columns="Source", values="Value", aggfunc="mean")
pivot.plot(figsize=(12, 6))
plt.title("Renewable Energy Production Trends (1949–2023)")
plt.ylabel("Production (Trillion Btu)")
plt.grid(True)
plt.tight_layout()
plt.savefig("output/renewable_trends.png")

print("✅ Charts saved: output/avg_growth_by_source.png & output/renewable_trends.png")
