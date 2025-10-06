import pandas as pd
import os

input_path = "data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx"
output_path = "data/Table_10.1_cleaned.xlsx"

# Read first 20 rows to find where "Month" appears
raw = pd.read_excel(input_path, header=None)
header_row = None

for i, row in raw.iterrows():
    if row.astype(str).str.contains("Month", case=False, na=False).any():
        header_row = i
        break

if header_row is None:
    raise ValueError("❌ Could not locate 'Month' header row.")

# Now read with the detected header
df = pd.read_excel(input_path, header=[header_row, header_row + 1])

# Combine multi-line headers into a single clean line
df.columns = (
    df.columns.map(lambda x: " ".join([str(i) for i in x if i and "Unnamed" not in str(i)]).strip())
)
df = df.loc[:, ~df.columns.duplicated()]

# Explicit, shorter renaming
rename_map = {
    "Month": "Month",
    "Wood Energy Production (Trillion Btu)": "Wood Production",
    "Biofuels Production (Trillion Btu)": "Biofuels Production",
    "Total Biomass Energy Production (Trillion Btu)": "Total Biomass Production",
    "Total Renewable Energy Production (Trillion Btu)": "Total Renewable Production",
    "Hydroelectric Power Consumption (Trillion Btu)": "Hydroelectric Consumption",
    "Geothermal Energy Consumption (Trillion Btu)": "Geothermal Consumption",
    "Solar Energy Consumption (Trillion Btu)": "Solar Consumption",
    "Wind Energy Consumption (Trillion Btu)": "Wind Consumption",
    "Wood Energy Consumption (Trillion Btu)": "Wood Consumption",
    "Waste Energy Consumption (Trillion Btu)": "Waste Consumption",
    "Biofuels Consumption (Trillion Btu)": "Biofuels Consumption",
    "Total Biomass Energy Consumption (Trillion Btu)": "Total Biomass Consumption",
    "Total Renewable Energy Consumption (Trillion Btu)": "Total Renewable Consumption"
}

df = df.rename(columns=lambda c: rename_map.get(c, c))

# Replace "Not Available" with NaN
df = df.replace("Not Available", pd.NA)

# Drop empty columns and rows
df = df.dropna(axis=1, how="all")
df = df.dropna(how="all")

# Save cleaned data
os.makedirs("data", exist_ok=True)
df.to_excel(output_path, index=False)
print("✅ Cleaned dataset saved →", output_path)
print("✅ Final columns:")
for col in df.columns:
    print(" -", col)
