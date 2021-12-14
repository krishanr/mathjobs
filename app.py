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
cits_full = pd.read_csv((project_dir / "data/web/arxiv-metadata-influential.csv"),dtype={'id': object})
_df = pd.read_csv( (project_dir / "data/web/arxiv-group-count.csv") )
cits = None

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

def get_influential_heatmap (cits):
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
        Output("top_influential_papers", "figure")
    ],
    [
        Input("category_map", "clickData"),
    ],
)
def update_plots(selected_item):
    global cits 
    print(selected_item)

    path = None
    if selected_item:
        path = selected_item['points'][0]['id'].split("/")

    if (not selected_item) or  len(path) < 2:
        group_name = ['Physics', 'Mathematics', 'Computer Science',
        'Quantitative Biology', 'Statistics', 'Quantitative Finance',
        'Economics', 'Electrical Engineering and Systems Science']

        cits = sec_result[sec_result['group_name'].isin(group_name) ].groupby(['year', 'id']).agg({"references":'sum', "title" : 'first'}).reset_index() #top_k_influential(group_name, top_k=3, threshold=10)
        heatmap = get_influential_heatmap ( cits)

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
    elif len(path) == 2:
        cits = cits_full[cits_full['group_name'] == path[1]]

        # Added this line to remove duplicate ids within a year.
        cits = cits.groupby(['year', 'id']).first().reset_index()

        # Collect the influential publications within this group.
        top_k, threshold = 3, 10 #TODO: centralize these variables.
        cits = cits.loc[cits.groupby(['year'])['references'].nlargest(top_k).reset_index()['level_1']]
        cits = cits.query ( "references > @threshold" )

        heatmap = get_influential_heatmap (cits)

        data = [heatmap]
        fig = go.Figure(data=data)

        # Make human readable group name
        human_group_name = path[1]

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

    elif len(path) == 3:
        # Specify the group_name and category_name, since the 'Numerical Analysis' category appears in
        # mathematics and computer science.
        cits = cits_full[(cits_full['group_name'] == path[1]) & (cits_full['category_name'] == path[2])]
        heatmap = get_influential_heatmap (cits)

        data = [heatmap]
        fig = go.Figure(data=data)

        # Make human readable group name
        human_group_name = path[2]

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
    else:
        import Exception

        #TODO: handle this.
        raise Exception("Unanticipated situation")

    return [fig]

@app.callback(
    Output('pre_title', 'children'),
    Output('pre_authors', 'children'),
    Output('pre_abstract', 'children'),
    Output('pre_links', 'children'),
    Input('top_influential_papers', 'clickData'))
def update_graph(hoverData):
    global cits 
    if cits is not None and hoverData is not None:
        titleSmal = hoverData['points'][0]['y']
        id = cits[cits['titleSmal'] == titleSmal].iloc[0].id
        #print(sec_result[sec_result['id'] == id])

        result = cits_full[cits_full['id'] == id]
        
        link = [ html.Span(f"{id}  ", style={ "font-weight": "lighter"}) , html.A(
            href= f"https://arxiv.org/pdf/{id}",
            children=[  "pdf"  ], 
        )]

        return result.title.iloc[0], result.authors.iloc[0], result.abstract.iloc[0], link
    else:
        return "", "", "", ""



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

category_map_fig = px.treemap(_df[~_df['group_name'].isna()].sort_values('id'), path=[px.Constant("all"), 'group_name', 'category_name'], values='val')
category_map_fig.update_traces(root_color="lightgrey")
category_map_fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

category_map = dcc.Graph(
    id='category_map',
    figure=category_map_fig
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
        dbc.Row(dbc.Col(category_map)),
        dbc.Row(dbc.Col(top_influential_papers, width=12)),
        dbc.Row(dbc.Col( dbc.Container(
    [
        html.H5(children="Select bank & dataset size", className="display-5", id="pre_title"),
        html.Hr(className="my-2"),
        html.Div([
            dbc.Row([
                dbc.Col( html.P( "(Lower is faster. Higher is more precise)", id="pre_authors" ) , width=10),
                dbc.Col( html.P( "",  id="pre_links" ) , width=2)
            ])
        ]),
        html.P(
            "(You can define the time frame down to month granularity)", id="pre_abstract"
        ),
    ]
),align="center", style={"backgroundColor": "rgb(243, 246, 251)"})),
        dbc.Row(dbc.Col(footer)),
        dbc.Row(dbc.Col(html.P(id='placeholder')))
    ]
)

app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)