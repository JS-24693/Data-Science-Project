# Import required libraries
import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash app
app = Dash(__name__)

# Helper function: Dropdown
def create_dropdown(df):
    options = [{'label': 'All Sites', 'value': 'ALL'}] + \
              [{'label': site, 'value': site} for site in df['Launch Site'].unique()]
    return dcc.Dropdown(
        id='launch-site-dropdown',
        options=options,
        value='ALL',
        placeholder='Select a Launch Site',
        clearable=False,
        searchable=True
    )

# App Layout
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={
        'textAlign': 'center',
        'color': '#503D36',
        'fontSize': 40
    }),
    create_dropdown(spacex_df),
    html.Br(),

    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    dcc.RangeSlider(
        id='payload-slider',
        min=spacex_df['Payload Mass (kg)'].min(),
        max=spacex_df['Payload Mass (kg)'].max(),
        step=1000,
        marks={int(i): f'{int(i)}' for i in np.linspace(
            spacex_df['Payload Mass (kg)'].min(),
            spacex_df['Payload Mass (kg)'].max(), 5)},
        value=[
            spacex_df['Payload Mass (kg)'].min(),
            spacex_df['Payload Mass (kg)'].max()
        ]
    ),
    html.Br(),

    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('launch-site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            filtered_df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs Failure for site {selected_site}',
            labels={0: 'Failed', 1: 'Success'}
        )
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('launch-site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs. Success for {selected_site}',
        labels={'class': 'Launch Success (1=Success, 0=Failure)'}
    )
    return fig

# Run the app
if __name__ == '__main__':
     app.run(debug=True, port=8050)

