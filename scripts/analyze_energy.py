import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
input_path = "data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Load Excel
df = pd.read_excel(input_path, skiprows=2)  # skip metadata rows if needed

# Clean up column names
df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
df = df.rename(columns={df.columns[0]: "Year"})

# Drop NA and "Not Available"
df = df.replace("Not Available", pd.NA).dropna()

# Convert numeric columns
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Melt into long format
df_long = df.melt(id_vars=["Year"], var_name="Source", value_name="Value")
df_long = df_long.dropna()

# Calculate year-over-year growth per source
df_long["Growth (%)"] = df_long.groupby("Source")["Value"].pct_change() * 100

# Save to CSV for visualization
df_long.to_csv(os.path.join(output_dir, "energy_long.csv"), index=False)
print("✅ Data reshaped and saved to output/energy_long.csv")

# --- Visualization Section ---
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_long, x="Year", y="Value", hue="Source")
plt.title("Renewable Energy Consumption by Source (Trillion Btu)")
plt.xlabel("Year")
plt.ylabel("Consumption (Trillion Btu)")
plt.legend(title="Source")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "renewable_trends.png"))
plt.close()

# Average growth by source
avg_growth = (
    df_long.groupby("Source")["Growth (%)"].mean().dropna().sort_values(ascending=False)
)
plt.figure(figsize=(8, 5))
sns.barplot(x=avg_growth.values, y=avg_growth.index, palette="viridis")
plt.title("Average Annual Growth Rate by Energy Source (%)")
plt.xlabel("Average Growth Rate (%)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_growth_by_source.png"))
plt.close()

print("✅ Charts saved in output/: renewable_trends.png & avg_growth_by_source.png")

# --- Pie chart: Energy Mix for Latest Year ---
latest_year = df_long["Year"].max()
df_latest = df_long[df_long["Year"] == latest_year]

mix = df_latest.groupby("Source")["Value"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 8))
plt.pie(mix, labels=mix.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
plt.title(f"Renewable Energy Mix by Source ({latest_year.year if hasattr(latest_year, 'year') else int(latest_year)})")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "energy_mix_pie.png"))
plt.close()

print("✅ Added: energy_mix_pie.png")

# --- Correlation Heatmap ---
df_corr = df[df.columns[1:]].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Between Renewable Energy Sources (2010–2023)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
plt.close()

print("✅ Added: correlation_heatmap.png")

# --- Area chart: total renewable contribution over time ---
df_area = df.set_index("Year")
df_area.plot(kind="area", stacked=True, figsize=(10, 6), alpha=0.8, colormap="Set2")
plt.title("Stacked Area Chart – Renewable Energy Consumption by Source")
plt.ylabel("Trillion Btu")
plt.xlabel("Year")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "stacked_renewables.png"))
plt.close()

print("✅ Added: stacked_renewables.png")
