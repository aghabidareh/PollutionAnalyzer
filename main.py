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
