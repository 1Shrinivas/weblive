from dash import html, dcc
import dash_bootstrap_components as dbc
from database import *

live_page = html.Div([
    dbc.Container([
        html.Div([
            html.Br(),
            html.H3("Unlocking insights into your health with Data-Driven analysis",
                    style={'marginLeft': '20px', 'fontWeight': 'bold', "fontStyle": "italic",
                           'color': 'black', "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)",
                           'fontFamily': 'sans-serif',
                           'textAlign': 'left'}),
            html.P(
                "Gain a deeper understanding of your well-being through your Physiological Signals",
                style={'marginLeft': '20px', 'color': 'black', 'fontSize': '15px',
                       "fontStyle": "italic", "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)", 'lineHeight': '1'}),
        ], style={'marginLeft': '50px'}, className="g-3"),
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id="patient-id-db",
                    options=[{'label': j, 'value': j} for j in Chest_Data_collection.distinct("userId")],
                    placeholder="Patient_id",
                    clearable=False,
                    style={"height": "40px", 'borderRadius': '10px'}
                ), xs=12, sm=12, md=6, lg=8, xl=8),
                dbc.Col(
                    dbc.Button('Submit', id='submit-patient', color='primary',
                               style={"width": "50%", 'borderRadius': '10px', "height": "40px",
                                      "border": "1px solid black", "color": "black", 'fontWeight': 'bold',
                                      "backgroundColor": "transparent"}),
                    xs=12, sm=12, md=6, lg=4, xl=4),
            ], justify="around", align="left", style={'width': '100%', 'textAlign': 'left'})
        ], style={'textAlign': 'left', 'width': '100%', 'marginLeft': '70px'}),
        html.Br(),
        html.Hr(style={'size': '10', 'borderColor': 'black', 'borderHeight': "20vh",
                       'marginLeft': '70px', 'marginRight': '70px'}),
        html.Br(),
        html.Button(id='patient-update-button', style={'display': 'none'}),
        html.Div(id="measurement-output"),
        dcc.Interval(
            id='measurement-interval-component',
            interval=1 * 60000,
            n_intervals=0,
            max_intervals=-1
        ),
        dcc.Store(id='last-username-count', data={'count': 0}),
    ], fluid=True),
], style={
    'backgroundColor': '#cfe2ff',
    'minHeight': '100vh',
    'width': '100%',
    'margin': '0',
    'padding': '0',
    'overflowX': 'hidden'
})
