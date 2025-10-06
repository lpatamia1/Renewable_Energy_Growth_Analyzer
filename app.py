from flask import Flask, render_template, send_from_directory
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    # Load processed data
    csv_path = os.path.join('output', 'energy_long.csv')
    if not os.path.exists(csv_path):
        return "⚠️ Data file not found. Please run analyze_energy.py first."

    df = pd.read_csv(csv_path)

    # Ensure expected columns
    for col in ["Year", "Source", "Value"]:
        if col not in df.columns:
            return f"⚠️ Missing column '{col}' in output/energy_long.csv"

    latest_year = df['Year'].max()

    # Summarize energy by source for latest year
    top_sources = (
        df[df['Year'] == latest_year]
        .groupby('Source', as_index=True)['Value']
        .sum()
        .sort_values(ascending=False)
        .head(8)
    )

    # Derived stats
    total_latest = float(df[df['Year'] == latest_year]['Value'].sum())

    # Average of per-source YoY growth, across sources
    growth_series = df.sort_values(["Source", "Year"]).groupby('Source')['Value'].pct_change()
    avg_growth = float(growth_series.mean(skipna=True) * 100)
    if np.isnan(avg_growth):
        avg_growth = 0.0  # fallback if not computable

    insights = [
        "Solar and wind energy continue to lead renewable growth.",
        "Hydropower remains stable due to infrastructure limits.",
        "Biomass and biofuels show steady expansion.",
        "U.S. renewables have roughly doubled since the early 2000s."
    ]

    return render_template(
        'index.html',
        charts=[
            'renewable_trends.png',
            'avg_growth_by_source.png',
            'energy_mix_pie.png',
            'correlation_heatmap.png',
            'stacked_renewables.png',
            'forecast_trend.png'
        ],
        latest_year=int(latest_year),
        top_sources=top_sources.to_dict(),
        total_latest=total_latest,
        growth_rate=avg_growth,   # <<< pass as growth_rate (template uses this)
        insights=insights
    )

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
