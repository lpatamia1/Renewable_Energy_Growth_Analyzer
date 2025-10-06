import pandas as pd

input_path = "data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx"
output_path = "data/Table_10.1_cleaned.xlsx"

# Read the file with header rows at 10 and 11 (0-indexed)
df = pd.read_excel(input_path, header=[10, 11])

# Merge multi-level column headers and clean them up
df.columns = [
    " ".join([str(a), str(b)]).replace("nan", "").strip()
    for a, b in df.columns
]

# Drop any unnamed or empty columns
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.loc[:, ~df.columns.duplicated()]

# Rename the first column to 'Month'
df.rename(columns={df.columns[0]: "Month"}, inplace=True)

# Remove rows where Month is NaN
df = df.dropna(subset=["Month"])

# Replace 'Not Available' with NaN
df = df.replace("Not Available", pd.NA)

# Convert numeric columns
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Save cleaned version
df.to_excel(output_path, index=False)

print("✅ Cleaned dataset saved →", output_path)
print("✅ Columns:", df.columns.tolist())
print("✅ Rows:", len(df))
