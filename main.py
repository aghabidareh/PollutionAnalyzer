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

@app.callback(
    [Output('yearly-aqi', 'figure'), Output('monthly-aqi', 'figure'), Output('hourly-max', 'figure'),
     Output('yearly-pollutant', 'figure'), Output('monthly-pollutant', 'figure'), Output('yearly-mean-pollutants', 'figure'),
     Output('hourly-o3-max', 'figure'), Output('monthly-aqi-violin', 'figure'), Output('top-states-aqi', 'figure'),
     Output('top-cities-aqi', 'figure'), Output('state-aqi-box', 'figure'), Output('top-counties-aqi', 'figure'),
     Output('top-cities-mean', 'figure'), Output('state-mean', 'figure'), Output('top-sites-max', 'figure'),
     Output('top-cities-co-mean', 'figure'), Output('scatter-no2-o3', 'figure'), Output('correlation-heatmap', 'figure'),
     Output('scatter-no2-co', 'figure'), Output('scatter-so2-o3', 'figure'), Output('aqi-pairplot', 'figure'),
     Output('pollutant-distribution', 'figure'), Output('no2-aqi-dist', 'figure'), Output('o3-aqi-exceed', 'figure'),
     Output('so2-aqi-dist', 'figure'), Output('co-aqi-dist', 'figure'), Output('top-site-no2', 'figure'),
     Output('top-site-o3', 'figure'), Output('top-site-so2', 'figure'), Output('top-site-co', 'figure')],
    [Input('state-dropdown', 'value'), Input('city-dropdown', 'value'), Input('year-dropdown', 'value'), Input('pollutant-dropdown', 'value')]
)
def update_graphs(states, cities, years, pollutant):
    # Filter data
    dff = df.copy()
    if states:
        dff = dff[dff['State'].isin(states)]
    if cities:
        dff = dff[dff['City'].isin(cities)]
    if years:
        dff = dff[dff['Year'].isin(years)]

    figures = []

    yearly_aqi = dff.groupby('Year')[f'{pollutant} AQI'].mean().reset_index()
    fig1 = px.line(yearly_aqi, x='Year', y=f'{pollutant} AQI', title=f'Yearly Mean {pollutant} AQI', markers=True)
    figures.append(fig1)

    monthly_aqi = dff.groupby('Month')[f'{pollutant} AQI'].mean().reset_index()
    fig2 = px.bar(monthly_aqi, x='Month', y=f'{pollutant} AQI', title=f'Monthly Mean {pollutant} AQI')
    figures.append(fig2)

    fig3 = px.box(dff, x=f'{pollutant} 1st Max Hour', y=f'{pollutant} 1st Max Value',
                  title=f'Hourly Distribution of {pollutant} Max Values')
    figures.append(fig3)

    fig4 = px.line(dff.groupby('Year')[f'{pollutant} AQI'].mean().reset_index(), x='Year', y=f'{pollutant} AQI',
                   title=f'Yearly Mean {pollutant} AQI', markers=True)
    figures.append(fig4)

    fig5 = px.bar(dff.groupby('Month')[f'{pollutant} AQI'].mean().reset_index(), x='Month', y=f'{pollutant} AQI',
                  title=f'Monthly Mean {pollutant} AQI')
    figures.append(fig5)

    yearly_means = dff.groupby('Year')[['NO2 Mean', 'O3 Mean', 'SO2 Mean', 'CO Mean']].mean().reset_index()
    fig6 = go.Figure()
    for col in ['NO2 Mean', 'O3 Mean', 'SO2 Mean', 'CO Mean']:
        fig6.add_trace(go.Scatter(x=yearly_means['Year'], y=yearly_means[col], mode='lines+markers', name=col))
    fig6.update_layout(title='Yearly Mean Pollutant Concentrations', xaxis_title='Year', yaxis_title='Concentration')
    figures.append(fig6)

    fig7 = px.box(dff, x='O3 1st Max Hour', y='O3 1st Max Value', title='Hourly Distribution of O3 Max Values')
    figures.append(fig7)

    fig8 = px.violin(dff, x='Month', y=f'{pollutant} AQI', title=f'Monthly {pollutant} AQI Distribution', box=True)
    figures.append(fig8)

    top_states = dff.groupby('State')[f'{pollutant} AQI'].mean().nlargest(10).reset_index()
    fig9 = px.bar(top_states, x=f'{pollutant} AQI', y='State', title=f'Top 10 States by Mean {pollutant} AQI')
    figures.append(fig9)

    top_cities = dff.groupby('City')[f'{pollutant} AQI'].mean().nlargest(10).reset_index()
    fig10 = px.bar(top_cities, x=f'{pollutant} AQI', y='City', title=f'Top 10 Cities by Mean {pollutant} AQI')
    figures.append(fig10)

    fig11 = px.box(dff, x='State', y=f'{pollutant} AQI', title=f'{pollutant} AQI Distribution by State')
    fig11.update_layout(xaxis={'tickangle': 45})
    figures.append(fig11)

    top_counties = dff.groupby('County')[f'{pollutant} AQI'].mean().nlargest(10).reset_index()
    fig12 = px.bar(top_counties, x=f'{pollutant} AQI', y='County', title=f'Top 10 Counties by Mean {pollutant} AQI')
    figures.append(fig12)

    top_cities_mean = dff.groupby('City')[f'{pollutant} Mean'].mean().nlargest(10).reset_index()
    fig13 = px.bar(top_cities_mean, x=f'{pollutant} Mean', y='City', title=f'Top 10 Cities by Mean {pollutant} Concentration')
    figures.append(fig13)

    state_mean = dff.groupby('State')[f'{pollutant} Mean'].mean().reset_index()
    fig14 = px.bar(state_mean, x='State', y=f'{pollutant} Mean', title=f'Mean {pollutant} Concentration by State')
    fig14.update_layout(xaxis={'tickangle': 45})
    figures.append(fig14)

    top_sites = dff.groupby('State_County_City')[f'{pollutant} 1st Max Value'].mean().nlargest(10).reset_index()
    fig15 = px.bar(top_sites, x=f'{pollutant} 1st Max Value', y='State_County_City',
                   title=f'Top 10 Sites by Mean {pollutant} Max Value')
    figures.append(fig15)

    top_cities_co = dff.groupby('City')['CO Mean'].mean().nlargest(10).reset_index()
    fig16 = px.bar(top_cities_co, x='CO Mean', y='City', title='Top 10 Cities by Mean CO Concentration')
    figures.append(fig16)

    fig17 = px.scatter(dff, x='NO2 Mean', y='O3 Mean', title='NO2 vs O3 Mean Concentrations', opacity=0.5)
    figures.append(fig17)

    corr = dff[['NO2 Mean', 'O3 Mean', 'SO2 Mean', 'CO Mean', 'NO2 AQI', 'O3 AQI', 'SO2 AQI', 'CO AQI']].corr()
    fig18 = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='RdBu', showscale=True))
    fig18.update_layout(title='Correlation Between Pollutants and AQI')
    figures.append(fig18)

    fig19 = px.scatter(dff, x='NO2 AQI', y='CO AQI', title='NO2 AQI vs CO AQI', opacity=0.5)
    figures.append(fig19)

    fig20 = px.scatter(dff, x='SO2 1st Max Value', y='O3 1st Max Value', title='SO2 vs O3 Max Values', opacity=0.5)
    figures.append(fig20)

    fig21 = px.scatter_matrix(dff, dimensions=['NO2 AQI', 'O3 AQI', 'SO2 AQI', 'CO AQI'],
                             title='Pairplot of AQI Values')
    figures.append(fig21)

    fig22 = px.histogram(dff, x=f'{pollutant} Mean', nbins=50, title=f'Distribution of {pollutant} Mean Concentrations')
    figures.append(fig22)

    fig23 = px.histogram(dff, x='NO2 AQI', nbins=50, title='Distribution of NO2 AQI')
    figures.append(fig23)

    o3_exceed = dff[dff['O3 AQI'] > 100]['O3 AQI'].value_counts().sort_index().reset_index()
    o3_exceed.columns = ['O3 AQI', 'Count']
    fig24 = px.line(o3_exceed, x='O3 AQI', y='Count', title='O3 AQI Exceedances (>100)', markers=True)
    figures.append(fig24)

    fig25 = px.histogram(dff, x='SO2 AQI', nbins=50, title='Distribution of SO2 AQI')
    figures.append(fig25)

    fig26 = px.histogram(dff, x='CO AQI', nbins=50, title='Distribution of CO AQI')
    figures.append(fig26)

    top_site_no2 = dff.groupby('State_County_City')['NO2 1st Max Value'].mean().nlargest(5).reset_index()
    fig27 = px.bar(top_site_no2, x='NO2 1st Max Value', y='State_County_City',
                   title='Top 5 Sites by Mean NO2 Max Value')
    figures.append(fig27)

    top_site_o3 = dff.groupby('State_County_City')['O3 1st Max Value'].mean().nlargest(5).reset_index()
    fig28 = px.bar(top_site_o3, x='O3 1st Max Value', y='State_County_City',
                   title='Top 5 Sites by Mean O3 Max Value')
    figures.append(fig28)

    top_site_so2 = dff.groupby('State_County_City')['SO2 AQI'].mean().nlargest(5).reset_index()
    fig29 = px.bar(top_site_so2, x='SO2 AQI', y='State_County_City', title='Top 5 Sites by Mean SO2 AQI')
    figures.append(fig29)

    top_site_co = dff.groupby('State_County_City')['CO AQI'].mean().nlargest(5).reset_index()
    fig30 = px.bar(top_site_co, x='CO AQI', y='State_County_City', title='Top 5 Sites by Mean CO AQI')
    figures.append(fig30)

    return figures

