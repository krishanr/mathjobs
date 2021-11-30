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

df_versions =  pd.read_csv(project_dir / "data/processed/archive/arxiv-metadata-ext-version.zip",dtype={'id': object})
df_taxonomy = pd.read_csv(project_dir / "data/processed/archive/arxiv-metadata-ext-taxonomy.csv")
df_categories = pd.read_csv(project_dir / "data/processed/archive/arxiv-metadata-ext-category.zip",dtype={'id': object})
sec_result =  pd.read_csv((project_dir / "data/processed/archive/arxiv-metadata-influential.csv"),dtype={'id': object})
_df = pd.read_csv( (project_dir / "data/processed/archive/arxiv-group-count.csv") )

# TODO: why does this duplicate occur?
# Drop row with id 'astro-ph/0302207', because it gives rise to duplicates.
df_categories = df_categories.drop(index=df_categories[df_categories['id'] == 'astro-ph/0302207'].index[0])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
    if group_name:
        ids = df_categories.merge(df_taxonomy, on="category_id").query("group_name.isin(@group_name)", engine="python")["id"].values
    else:
        ids = df_categories.merge(df_taxonomy, on="category_id")["id"].values
    df = df_versions.query("id.isin(@ids)", engine="python").query("version == 'v1'").groupby(["year","month"]).agg({"id":'count'}).reset_index()

    df["tot"] = df["id"].cumsum()

    df = df.query("year > 1990 and ( year != 2020 or month < 8)")
    df["month"] =  df["year"].astype(str) + "-" + df["month"].astype(str)  

    cits = sec_result[sec_result['group_name'].isin(group_name) ].groupby(['year', 'id']).agg({"references":'sum', "title" : 'first'}).reset_index() #top_k_influential(group_name, top_k=3, threshold=10)
    heatmap = get_influential_heatmap (group_name, cits)

    data = [heatmap]
    fig = go.Figure(data=data)

    fig.update_layout(
        title=f"Top influential papers in {group_name}",
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
    fig.show()

    return [px.line(df, x="month", y="tot", title ="Arxiv preprint counts"), fig]

group_count_fig = px.bar(_df, x='id', y='group_name')
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
header = html.H2(children="arXiv Analysis")
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
        dbc.Row(dbc.Col(top_influential_papers, width=12))
    ]
)

app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)