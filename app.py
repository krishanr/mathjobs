from pathlib import Path

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import pandas as pd

project_dir = Path(__file__).resolve().parents[0]

sec_result =  pd.read_csv((project_dir / "data/processed/archive/arxiv-metadata-influential.csv"),dtype={'id': object})
df_preprint_count = pd.read_csv(project_dir / "data/processed/archive/arxiv-metadata-preprint-count.csv")
_df = pd.read_csv( (project_dir / "data/processed/archive/arxiv-group-count.csv") )

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def get_preprint_count(group_name, human_group_name):
    df = df_preprint_count[df_preprint_count['group_name'].isin(group_name) ].groupby(["year","month"]).agg({"id":'sum'}).reset_index()
    df["Count"] = df["id"].cumsum()
    df = df.query("year > 1990 and ( year != 2020 or month < 8)")
    df["Month"] =  df["year"].astype(str) + "-" + df["month"].astype(str)  

    return px.line(df, x="Month", y="Count", title = f"Preprint counts in {human_group_name}")


def df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}

def get_influential_heatmap (group_name, cits):
    cits['titleSmal'] = cits['title'].str[:30] + " ..."
    hm_cits = cits.pivot(index="titleSmal", columns="year",values="references")
    hm_cits = hm_cits.fillna(0)

    heatmap_data = df_to_plotly(hm_cits)
    titles = cits.groupby('title').first().reset_index()['title'].to_list()
    hovertext = list()
    for yi, yy in enumerate(titles):
        hovertext.append(list())
        for xi, xx in enumerate(heatmap_data['x']):
            hovertext[-1].append('Year: {}<br />Title: {}<br />Count: {}'.format(xx, yy, heatmap_data['z'][yi][xi]))

    # Setting grid lines: https://community.plotly.com/t/grid-lines-placement-in-heatmap/2628/3
    heatmap = go.Heatmap(**heatmap_data, type = 'heatmap',colorscale=[[0, "#caf3ff"], [1, "#2c82ff"]], hoverinfo='text', text=hovertext)

    return heatmap

@app.callback(
    [
        Output("preprint_by_year", "figure"),
        Output("top_influential_papers", "figure")
    ],
    [
        Input("graph_count", "selectedData"),
    ],
)
def update_plots(selected_radio):
    group_name = [ point_dict['y'] for point_dict in selected_radio['points']] if selected_radio else ""
    if not group_name:
        group_name = ['Physics', 'Mathematics', 'Computer Science',
       'Quantitative Biology', 'Statistics', 'Quantitative Finance',
       'Economics', 'Electrical Engineering and Systems Science']
    print(group_name)

    cits = sec_result[sec_result['group_name'].isin(group_name) ].groupby(['year', 'id']).agg({"references":'sum', "title" : 'first'}).reset_index() #top_k_influential(group_name, top_k=3, threshold=10)
    heatmap = get_influential_heatmap (group_name, cits)

    data = [heatmap]
    fig = go.Figure(data=data)

    # Make human readable group name
    human_group_name = ""
    if len(group_name) == 1:
        human_group_name = group_name[0]
    elif len(group_name) == 8:
        human_group_name = "arXiv"
    else:
        human_group_name = group_name[0]
        for name in group_name[1:-1]:
            human_group_name += ", " + name

        human_group_name += ", and " + group_name[-1]

    preprint_by_year_fig = get_preprint_count(group_name, human_group_name)

    fig.update_layout(
        title=f"Top influential preprints in {human_group_name}",
        font=dict(family="Open Sans"),
        #yaxis_nticks=16,
        #xaxis_nticks=24,
        xaxis=dict(
                ticks="",
                ticklen=2,
                tickfont=dict(family="sans-serif"),
                tickcolor="#ffffff",
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" "
        ),)
        #hovermode='y')

    return [preprint_by_year_fig, fig]

group_count_fig = px.bar(_df, x='id', y='group_name')
group_count_fig.update_layout(
    yaxis_title="Group",
    xaxis_title="Count"
)
#group_count_fig.update_layout(width=500,  height=500,)
group_count = dcc.Graph(
        id='graph_count',
        figure=group_count_fig
)

# bootstrap layout: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
#preprint_by_year_fig.update_layout(width=500,  height=500,)
preprint_by_year = dcc.Graph(
        id='preprint_by_year',
)
top_influential_papers = dcc.Graph(
    id='top_influential_papers',
)
# setup the header
header = html.H2(children="arXiv Influential Preprints")
footer = html.Div(children=["* This dashboard builds on work from ",html.A(
    href="https://www.kaggle.com/steubk/arxiv-taxonomy-e-top-influential-papers",
    children="this"
), " Kaggle notebook."], style={'font-size': '12px'} )
# setup & apply the layout
layout = html.Div(
    [
        dbc.Row(dbc.Col(header)),
        dbc.Row(
            [
                dbc.Col(group_count,width=6),
                dbc.Col(preprint_by_year,width=6),
            ]
        ),
        dbc.Row(dbc.Col(top_influential_papers, width=12)),
        dbc.Row(dbc.Col(footer)),
    ]
)

app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)