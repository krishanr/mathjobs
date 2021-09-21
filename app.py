from pathlib import Path

import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd

project_dir = Path(__file__).resolve().parents[0]
df = pd.read_csv(project_dir / "data/processed/jobs.csv")

app = dash.Dash(__name__)

fig = px.line(df, x="year", y="jobCount",
                    color="name", title ="Math job counts")

app.layout = html.Div([
     dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)