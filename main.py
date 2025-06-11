import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os

df = pd.read_csv('data.csv')

df = df.drop(columns=['Unnamed: 0'], errors='ignore')
df['Date Local'] = pd.to_datetime(df['Date Local'], errors='coerce')
df['Year'] = df['Date Local'].dt.year
df['Month'] = df['Date Local'].dt.month
df['State_County_City'] = df['State'] + '_' + df['County'] + '_' + df['City']

for col in ['NO2 Mean', 'O3 Mean', 'SO2 Mean', 'CO Mean', 'NO2 1st Max Value', 'O3 1st Max Value', 'SO2 1st Max Value', 'CO 1st Max Value']:
    df[col] = df[col].clip(lower=0)

df['SO2 AQI'] = df['SO2 AQI'].fillna(df['SO2 AQI'].median())
df['CO AQI'] = df['CO AQI'].fillna(df['CO AQI'].median())

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

states = df['State'].unique()
cities = df['City'].unique()
years = df['Year'].dropna().unique().astype(int)
pollutants = ['NO2', 'O3', 'SO2', 'CO']

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Air Pollution Dashboard", className="text-center"), width=12),
        dbc.Col(html.P("Interactive visualizations of air quality data (NO2, O3, SO2, CO) across the US.",
                       className="text-center"), width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H4("Filters"),
            html.Label("Select State:"),
            dcc.Dropdown(id='state-dropdown', options=[{'label': s, 'value': s} for s in states], value=None, multi=True, placeholder="All States"),
            html.Label("Select City:", className="mt-2"),
            dcc.Dropdown(id='city-dropdown', options=[{'label': c, 'value': c} for c in cities], value=None, multi=True, placeholder="All Cities"),
            html.Label("Select Year:", className="mt-2"),
            dcc.Dropdown(id='year-dropdown', options=[{'label': y, 'value': y} for y in years], value=None, multi=True, placeholder="All Years"),
            html.Label("Select Pollutant:", className="mt-2"),
            dcc.Dropdown(id='pollutant-dropdown', options=[{'label': p, 'value': p} for p in pollutants], value='NO2', placeholder="Select Pollutant")
        ], width=3),

        dbc.Col([
            dcc.Tabs([
                dcc.Tab(label="Temporal Trends", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='yearly-aqi'), width=6),
                        dbc.Col(dcc.Graph(id='monthly-aqi'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='hourly-max'), width=6),
                        dbc.Col(dcc.Graph(id='yearly-pollutant'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='monthly-pollutant'), width=6),
                        dbc.Col(dcc.Graph(id='yearly-mean-pollutants'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='hourly-o3-max'), width=6),
                        dbc.Col(dcc.Graph(id='monthly-aqi-violin'), width=6),
                    ]),
                ]),
                dcc.Tab(label="Geographical Insights", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-states-aqi'), width=6),
                        dbc.Col(dcc.Graph(id='top-cities-aqi'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='state-aqi-box'), width=6),
                        dbc.Col(dcc.Graph(id='top-counties-aqi'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-cities-mean'), width=6),
                        dbc.Col(dcc.Graph(id='state-mean'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-sites-max'), width=6),
                        dbc.Col(dcc.Graph(id='top-cities-co-mean'), width=6),
                    ]),
                ]),
                dcc.Tab(label="Pollutant Relationships", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='scatter-no2-o3'), width=6),
                        dbc.Col(dcc.Graph(id='correlation-heatmap'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='scatter-no2-co'), width=6),
                        dbc.Col(dcc.Graph(id='scatter-so2-o3'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='aqi-pairplot'), width=6),
                        dbc.Col(dcc.Graph(id='pollutant-distribution'), width=6),
                    ]),
                ]),
                dcc.Tab(label="AQI Analysis", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='no2-aqi-dist'), width=6),
                        dbc.Col(dcc.Graph(id='o3-aqi-exceed'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='so2-aqi-dist'), width=6),
                        dbc.Col(dcc.Graph(id='co-aqi-dist'), width=6),
                    ]),
                ]),
                dcc.Tab(label="Site-Specific Analysis", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-site-no2'), width=6),
                        dbc.Col(dcc.Graph(id='top-site-o3'), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-site-so2'), width=6),
                        dbc.Col(dcc.Graph(id='top-site-co'), width=6),
                    ]),
                ]),
            ])
        ], width=9)
    ], className="mb-4")
], fluid=True)


