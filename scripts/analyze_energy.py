import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Setup ===
input_path = "data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx"
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
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_long, x="Year", y="Value", hue="Source", linewidth=2)
plt.title("Renewable Energy Trends by Source (Trillion Btu)")
plt.xlabel("Year")
plt.ylabel("Energy (Trillion Btu)")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "renewable_trends.png"))
plt.close()

## (b) Average growth rate
df_long["Growth (%)"] = df_long.groupby("Source")["Value"].pct_change() * 100
avg_growth = df_long.groupby("Source")["Growth (%)"].mean().dropna().sort_values(ascending=False)

plt.figure(figsize=(8, 6))
sns.barplot(x=avg_growth.values, y=avg_growth.index, palette="crest")
plt.title("Average Annual Growth Rate by Energy Source (%)")
plt.xlabel("Average Growth Rate (%)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_growth_by_source.png"))
plt.close()

## (c) Pie chart for latest year
latest_year = df_long["Year"].max()
mix = df_long[df_long["Year"] == latest_year].groupby("Source")["Value"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 8))
plt.pie(mix, labels=mix.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
plt.title(f"Renewable Energy Mix by Source ({latest_year})")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "energy_mix_pie.png"))
plt.close()

## (d) Correlation heatmap
numeric_df = df.select_dtypes("number").drop(columns=["Year"], errors="ignore")
if not numeric_df.empty:
    corr = numeric_df.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Between Renewable Energy Sources")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
    plt.close()

## (e) Stacked area chart
df_area = df.set_index("Year").select_dtypes("number")
df_area.plot(kind="area", stacked=True, figsize=(10, 6), alpha=0.85, colormap="Set2")
plt.title("Stacked Area Chart – Renewable Energy Consumption by Source")
plt.ylabel("Trillion Btu")
plt.xlabel("Year")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "stacked_renewables.png"))
plt.close()

print("✅ All visuals successfully generated in /output/")
