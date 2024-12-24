import os
import sys
import re

import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output
from flask import Flask, render_template, request

sys.path.append(os.getcwd())
from config import DEBUG
from methods import get_weather
from api_requests.main import get_coordinates

app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, url_base_pathname="/dash/")

dash_app.layout = html.Div(
    [
        dcc.Store(id="weather-store"),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="route-map", style={"height": "400px"})],
                    className="mb-4",
                ),
                html.Div(
                    [
                        dcc.RadioItems(
                            id="days-selector",
                            options=[
                                {"label": "1 день", "value": 1},
                                {"label": "3 дня", "value": 3},
                                {"label": "5 дней", "value": 5},
                            ],
                            value=1,
                            className="mb-3",
                        ),
                        dcc.Graph(id="temperature-graph", style={"height": "300px"}),
                        dcc.Graph(id="precipitation-graph", style={"height": "300px"}),
                    ]
                ),
            ]
        ),
    ]
)


@dash_app.callback(
    [
        Output("route-map", "figure"),
        Output("temperature-graph", "figure"),
        Output("precipitation-graph", "figure"),
    ],
    [Input("weather-store", "data"), Input("days-selector", "value")],
)
def update_graphs(stored_data, selected_days):
    if not stored_data:
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig

    map_fig = go.Figure()
    lats, lons, names = [], [], []

    for point in stored_data:
        coords = get_coordinates(point["location"])
        if coords:
            lats.append(coords["lat"])
            lons.append(coords["lon"])
            names.append(point["location"])

    map_fig.add_trace(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="markers+lines",
            marker={"size": 12},
            text=names,
            name="Маршрут",
        )
    )

    map_fig.update_layout(
        mapbox={
            "style": "open-street-map",
            "center": {
                "lat": sum(lats) / len(lats),
                "lon": sum(lons) / len(lons),
            },
            "zoom": 5,
        },
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=False,
    )

    temp_fig = go.Figure()
    precip_fig = go.Figure()
    colors = px.colors.qualitative.Set3

    for i, point in enumerate(stored_data):
        dates = [x["Date"] for x in point["DailyForecasts"][:selected_days]]
        temps = [x["Temperature"]["Maximum"]["Value"] for x in point["DailyForecasts"][:selected_days]]
        precips = [x["Day"]["PrecipitationProbability"] for x in point["DailyForecasts"][:selected_days]]

        temp_fig.add_trace(
            go.Scatter(
                x=dates,
                y=temps,
                name=point["location"],
                line={"color": colors[i % len(colors)]},
                mode="lines+markers",
            )
        )

        precip_fig.add_trace(
            go.Bar(
                x=dates,
                y=precips,
                name=point["location"],
                marker_color=colors[i % len(colors)],
            )
        )

    temp_fig.update_layout(
        title="Температура",
        xaxis_title="Дата",
        yaxis_title="Температура (°C)",
        hovermode="x unified",
    )

    precip_fig.update_layout(
        title="Осадки",
        xaxis_title="Дата",
        yaxis_title="Осадки (мм)",
        hovermode="x unified",
        barmode="group",
    )

    return map_fig, temp_fig, precip_fig


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        points = []

        for key in request.form:
            if key.startswith("point"):
                location = request.form[key]
                if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', location):
                    return render_template(
                        "index.html",
                        error="Некорректный ввод"
                    )
                weather_data = get_weather(location, get_cached=DEBUG)
                points.append({"location": location, "weather": weather_data})

        return render_template(
            "weather.html",
            points=points,
            days_interval=int(request.form.get("days_interval", 1)),
            dash_url="/dash/",
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run("0.0.0.0", debug=DEBUG)
