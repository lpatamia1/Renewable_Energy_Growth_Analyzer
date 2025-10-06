import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
input_path = "data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# --- Load Excel safely ---
df = pd.read_excel(input_path, header=None)

# Find where "Month" appears to locate the real header row
header_row = df[df.astype(str).apply(lambda x: x.str.contains("Month", case=False, na=False)).any(axis=1)].index[0]

# Reload with correct header
df = pd.read_excel(input_path, skiprows=header_row)

# Drop unnamed and duplicate columns
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.loc[:, ~df.columns.duplicated()]

# Clean up column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace("\n", " ", regex=True)
    .str.replace(r"\(Trillion Btu\)", "", regex=True)
    .str.replace("Production", "", regex=False)
    .str.replace("Consumption", "", regex=False)
    .str.replace("Total", "", regex=False)
    .str.strip()
)

# Rename first col to "Month"
df.rename(columns={df.columns[0]: "Month"}, inplace=True)

# Drop rows with no useful data
df = df[df["Month"].notna()]

# Convert all numeric cols safely
for col in df.columns[1:]:
    if isinstance(df[col], pd.Series):
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Extract year
df["Year"] = df["Month"].astype(str).str.extract(r"(\d{4})").astype(float)
df = df[df["Year"].notna()]

print("✅ Data loaded successfully. Columns:", df.columns.tolist())
