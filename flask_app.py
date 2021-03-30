import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import flask
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
external_stylesheets = [dbc.themes.BOOTSTRAP]
pd.set_option("display.precision", 4)

# load data
projects = pd.read_csv(os.path.join(ROOT_DIR, "data/projects.csv"))

# page header
jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H1("Кластеризация курсов", className="display-3"),
                html.Hr(),
                html.H3(
                    "Кластеризация проводилась по данным курсов Classroom.",
                    className="lead",
                ),
                html.H3(
                    "В результате вакансии были разделены на 15 кластеров. На данной странице представлено описание "
                    "кластеров.",
                    className="lead",
                ),
            ],
            fluid=False,
        )
    ],
    fluid=False,
)

cluster_counts = projects["cluster"].value_counts()
colors = ['#1f77b4', ] * 15
# colors = dict(zip(cluster_counts.index+1, colors))
colors[0] = 'crimson'
cluster_counts = cluster_counts.sort_index()
fig_counts = go.Figure(
    go.Bar(
        x=cluster_counts.index + 1,
        y=cluster_counts.values,
        text=cluster_counts.values,
        textposition="outside",
        marker_color=colors
    )
)

fig_counts.update_xaxes(tickmode="linear", title="Номер кластера")
fig_counts.update_yaxes(
    title="Количество элементов в кластере", range=[1, 80], showticklabels=False
)

fig_counts.update_layout(
    height=400,
    paper_bgcolor="#f9f9f9",
    plot_bgcolor="#f9f9f9",
    title="Наполненность кластеров<br>(кликните по кластеру чтобы увидеть ключевые слова)",
    hovermode="x",
    font={"family": "Century Gothic"},
    xaxis_showgrid=False,
    yaxis_showgrid=False,
)

# scatter_plot.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor='grey')
# scatter_plot.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor='grey')


server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.title = "MIEM Cabinet"

app.layout = html.Div(
    children=[
        jumbotron,
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.Div([dcc.Graph(
                            id="bar-chart",
                            figure=fig_counts,
                        )], className="pretty_container", )
                    ],
                    width={"size": 6, "offset": 1},
                ),
                dbc.Col(
                    children=[
                        html.Div(
                            className="pretty_container",
                            children=[
                                html.H5(
                                    "Ключевые слова кластера",
                                    style={"position": "absolute"},
                                ),
                                html.Img(
                                    id="wordCloud",
                                    src=app.get_asset_url("cluster_1.png"),
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justify-content": "center",
                                "height": "430px",
                            },
                        )
                    ],
                    width={"size": 4, "offset": 0},
                ),
            ]
        ),
        html.Hr(),
    ],
    style={"background-color": "#f2f2f2"},
)


@app.callback(Output("wordCloud", "src"), Output("bar-chart", "figure"),
              [Input("bar-chart", "clickData")])

def change_cluster_wordcloud(data: dict):
    start_time = time.time()
    if data is None:
        print(f"Callback took {time.time() - start_time} s.")
        return app.get_asset_url(f"cluster_1.png"), dash.no_update

    colors = ['#1f77b4', ] * 15
    colors[data['points'][0]['label'] - 1] = 'crimson'
    # fig['data'][0]['marker']['color'] = colors
    fig_counts.update_traces(marker_color=colors)
    print(f"Callback took {time.time() - start_time} s.")
    return app.get_asset_url(f"cluster_{data['points'][0]['label']}.png"), fig_counts


if __name__ == "__main__":
    app.run_server(debug=True)