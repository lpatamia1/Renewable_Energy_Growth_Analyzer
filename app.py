from flask import Flask, render_template, send_from_directory
import os
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Load summary data
    summary_path = os.path.join('output', 'energy_long.csv')
    df = pd.read_csv(summary_path)
    latest_year = df['Year'].max()
    top_sources = df[df['Year'] == latest_year].groupby('Source')['Value'].sum().sort_values(ascending=False)
    
    return render_template('index.html', 
                           charts=[
                               'renewable_trends.png',
                               'avg_growth_by_source.png',
                               'energy_mix_pie.png',
                               'correlation_heatmap.png',
                               'stacked_renewables.png'
                           ],
                           latest_year=latest_year,
                           top_sources=top_sources.to_dict())

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
