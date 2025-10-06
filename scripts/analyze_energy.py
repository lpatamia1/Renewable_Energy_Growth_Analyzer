import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Setup ===
input_path = "data/Table_10.1_cleaned.xlsx"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# === 1️⃣ Load raw Excel and detect the "Month" header row ===
raw = pd.read_excel(input_path, header=None)
header_idx = None

for i, row in raw.iterrows():
    if "Month" in str(row.values):
        header_idx = i
        break

if header_idx is None:
    raise ValueError("❌ Could not find a header row containing 'Month'.")

# Re-read clean data
df = pd.read_excel(input_path, skiprows=header_idx)

# Drop fully empty columns
df = df.dropna(axis=1, how="all")

# Rename first column to "Month"
df.rename(columns={df.columns[0]: "Month"}, inplace=True)

# === 2️⃣ Clean data ===
df = df.replace(["Not Available", "—"], pd.NA)

# Convert numeric columns
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Extract clean numeric Year
df["Year"] = (
    df["Month"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .apply(lambda x: int(x) if str(x).isdigit() else None)
)

# Drop invalid or missing years
df = df[df["Year"].notna()].copy()
df["Year"] = df["Year"].astype(int)

# Drop rows that are mostly empty
df = df.dropna(thresh=3)

# === 3️⃣ Transform for visualization ===
df_long = df.melt(id_vars=["Year"], var_name="Source", value_name="Value")
df_long = df_long.dropna(subset=["Value"])
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

# Save cleaned dataset
df_long.to_csv(os.path.join(output_dir, "energy_long.csv"), index=False)
print("✅ Cleaned data saved → output/energy_long.csv")

# === 4️⃣ Visualizations ===

## (a) Trend line
df_long["Source"] = df_long["Source"].str.replace(r"\s*\(Trillion Btu\)", "", regex=True)
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_long, x="Year", y="Value", hue="Source", linewidth=2)
plt.title("Renewable Energy Trends by Source (Trillion Btu)")
plt.xlabel("Year")
plt.ylabel("Energy (Trillion Btu)")
plt.legend(bbox_to_anchor=(1.05, 1), title="Energy Source", loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "renewable_trends.png"))
plt.close()

## (b) Average growth rate
df_long["Growth (%)"] = df_long.groupby("Source")["Value"].pct_change() * 100
avg_growth = df_long.groupby("Source")["Growth (%)"].mean().dropna().sort_values(ascending=False)

plt.figure(figsize=(8, 6))
sns.barplot(x=avg_growth.values, y=avg_growth.index, palette="crest")
plt.title("Average Annual Growth Rate by Energy Source (Unit: %)", fontsize = 12)
plt.xlabel("Average Growth Rate (%)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_growth_by_source.png"))
plt.close()

## (c) Pie chart for latest year
latest_year = df_long["Year"].max()
mix = (
    df_long[df_long["Year"] == latest_year]
    .groupby("Source")["Value"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    mix,
    labels=None,  # remove text labels from the pie
    autopct="%1.1f%%",
    startangle=90,
    colors=sns.color_palette("pastel"),
)

# Add a clear, concise title
plt.title(
    f"Renewable Energy Mix by Source – {latest_year}\n(Unit: Trillion Btu)",
    fontsize=13,
    weight="bold"
)

# Add a legend (key) to the right
plt.legend(
    mix.index,
    title="Energy Source",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=9,
)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "energy_mix_pie.png"), bbox_inches="tight")
plt.close()


## (d) Correlation heatmap
numeric_cols = df.select_dtypes(include="number").drop(columns=["Year"], errors="ignore")
numeric_cols = numeric_cols.rename(columns=lambda c: c.replace(" (Trillion Btu)", ""))

corr = numeric_cols.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Between Renewable Energy Sources\n(Unit: Trillion Btu)", fontsize=13, weight="bold")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
plt.close()

## (e) Stacked Area Chart: Total Renewable Energy Consumption ---
df_area = df.set_index("Year").select_dtypes(include="number")

# Clean column names (remove "(Trillion Btu)")
cleaned_cols = [col.replace(" (Trillion Btu)", "") for col in df_area.columns]
df_area.columns = cleaned_cols

plt.figure(figsize=(10, 6))
df_area.plot(kind="area", stacked=True, alpha=0.85, colormap="Set2")
plt.title("Stacked Area Chart – Renewable Energy Consumption by Source\n(Unit: Trillion Btu)", fontsize=12)
plt.ylabel("Trillion Btu")
plt.xlabel("Year")
plt.legend(title="Energy Source", fontsize=8, bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "stacked_renewables.png"))
plt.close()

print("✅ Updated stacked area chart saved with cleaner legend titles.")

print("✅ All visuals successfully generated in /output/")
