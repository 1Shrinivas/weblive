from dash import html
import dash_bootstrap_components as dbc

login_page = html.Div([
    dbc.Container([
        html.Div([
            html.H3("Empowering Health Insights with AI Technology.",
                    style={'marginLeft': '20px', "fontStyle": "italic", 'paddingTop': '30px',
                           'fontFamily': 'sans-serif', "color": 'black',
                           'fontWeight': 'bold', "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)",
                           'textAlign': 'left'}),
            html.P(
                "Leverage advanced AI to monitor and analyze your vital signs for a clearer picture of your health.",
                style={'marginLeft': '20px', 'fontSize': '15px',
                       'fontFamily': 'sans-serif', "color": 'black',
                       'fontWeight': 'bold', "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)",
                       'textAlign': 'Left'
                       }),
        ], className="g-3", style={'marginLeft': '20px'}),
        html.Div([
            html.Div([
                html.H1(children='Welcome!',
                        style={'fontWeight': 'bold',
                               'fontSize': 30, 'fontFamily': 'sans-serif', 'fontStyle': 'italic',
                               'color': 'black', 'paddingTop': '30px', 'lineHeight': '1.5',
                               'textAlign': 'Left', "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)"}),
            ], style={'textAlign': 'Left', 'paddingLeft': '40px'},
                className="g-3",
            ),

            html.Div([
                dbc.Label("Username or Email", html_for="email-input",
                          style={'color': 'black', 'fontStyle': 'italic', 'fontWeight': 'bold',
                                 'fontFamily': 'sans-serif', 'font-size': 20}),
                dbc.Input(type="email", id="email-input", size="lg", placeholder="Enter Email"),
                dbc.FormText("We only accept Email..."),
                dbc.FormFeedback("That looks like a Email address :-)", type="valid"),
                dbc.FormFeedback(
                    "Sorry, we only accept Email for some reason...",
                    type="invalid",
                ),

            ], style={'paddingTop': '20px', 'textAlign': 'left',
                      'paddingLeft': '40px'},
                className="g-3",
            ),
            html.Div([
                dbc.Label("Password", html_for="password-input",
                          style={'color': 'black', 'fontStyle': 'italic', 'fontWeight': 'bold',
                                 'fontFamily': 'sans-serif', 'font-size': 20}),
                dbc.InputGroup([
                    dbc.Input(type="password", id="password-input", size="lg", placeholder="Enter password"),
                    dbc.InputGroupText(html.I(id="password-icon", className="bi bi-eye-slash")),
                ], id="password-group", size="lg"),

            ], style={'paddingTop': '20px', 'textAlign': 'left',
                      'paddingLeft': '40px'},
                className="g-3",
            ),
            html.Div([
                dbc.Button("Sign In", id='Login_button', n_clicks=0, size="md", color="light",
                           style={
                               'border': '1px solid black',
                               'color': 'black',
                               'backgroundColor': 'transparent',
                               'borderRadius': '10px',
                               'fontWeight': 'bold',
                               'textTransform': 'uppercase',
                               'padding': '10px 20px',
                               'fontSize': '20px',
                               'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.2)',
                           }
                           ),
            ], style={'paddingTop': '30px', 'textAlign': 'center', 'color': '#5e859d',
                      'paddingLeft': '40px'}, className="d-grid gap-2"),
            html.Br(),
            html.Div(id='authentication_output', children=[],
                     style={'textAlign': 'center', 'height': '5px',
                            'color': 'red',
                            'fontSize': '20px'}),
        ], style={'textAlign': 'Left', 'maxWidth': '60%'}),

    ], fluid=True),
], style={
    'backgroundColor': '#cfe2ff',
    'minHeight': '100vh',
    'width': '100%',
    'margin': '0',
    'padding': '0',
    'overflowX': 'hidden',
    'position': 'fixed',
})
# ], style={'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
#           'overflow': 'hidden', 'opacity': '0.8',
#           "backgroundImage": 'url("assets/shutter.jpg")',
#           'backgroundRepeat': 'no-repeat',
#           'backgroundPosition': 'center center',
#           'backgroundAttachment': 'fixed',
#           'backgroundSize': 'cover',
#           'display': 'flex',
#           'alignItems': 'center',
#           'justifyContent': 'center'
#           })
