@app.route('/')
def index():
    summary_path = os.path.join('output', 'energy_long.csv')
    df = pd.read_csv(summary_path)
    latest_year = df['Year'].max()
    top_sources = df[df['Year'] == latest_year].groupby('Source')['Value'].sum().sort_values(ascending=False)

    # KPI Metrics
    total_latest = df[df['Year'] == latest_year]['Value'].sum()
    prev_year = latest_year - 1
    total_prev = df[df['Year'] == prev_year]['Value'].sum()
    growth_rate = ((total_latest - total_prev) / total_prev * 100) if total_prev > 0 else 0

    return render_template(
        'index.html',
        charts=[
            'renewable_trends.png',
            'avg_growth_by_source.png',
            'energy_mix_pie.png',
            'correlation_heatmap.png',
            'stacked_renewables.png'
        ],
        interactive_chart='interactive_trends.html',
        latest_year=latest_year,
        top_sources=top_sources.to_dict(),
        total_latest=total_latest,
        growth_rate=growth_rate
    )
