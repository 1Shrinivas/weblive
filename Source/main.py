import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import flask
import secrets
import re
import uuid
import base64
import time
import pandas as pd
import numpy as np
from flask import session
from login import login_page
from live import live_page
from database import *
import warnings

warnings.filterwarnings("ignore")

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])

app.title = "Asma-health.ai"

app.server.secret_key = secrets.token_hex(16)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Login", href="/Login", id="nav-Login"),
                        style={"fontSize": "18px", "padding": "10px", "color": 'black'}),
            dbc.NavItem(dbc.NavLink("Real-time-monitoring", href="/Real-time", id="nav-Real-time"),
                        style={"fontSize": "18px", "padding": "10px", "color": 'black'}),
            dbc.NavItem(dbc.NavLink("About Us", href="/About", id="nav-About"),
                        style={"fontSize": "18px", "padding": "10px", "color": 'black'}),
            dbc.NavItem(dbc.NavLink("Contact", href="/Contact", id="nav-Contact"),
                        style={"fontSize": "18px", "padding": "10px", "color": 'black'}),
        ],
        brand=html.Div(
            [
                html.Img(src="assets/apex-legends-symbol.png", height="40px"),
                html.Span("Asma-health.ai",
                          style={"marginLeft": "1px", "verticalAlign": "middle", 'fontWeight': 'bold',
                                 'textAlign': 'center', "fontStyle": "italic",
                                 'fontSize': 30, "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)"}),
            ],
            style={"display": "flex", "alignItems": "center"}
        ),
        brand_href="https://asmaitha.com/",
        color="#cfe2ff",
        dark=False,
        className="sticky-top",
        style={
            "borderBottom": "1px solid #4f4f4f",
            "borderRadius": "0px"
        }
    ),
    html.Div(id='page-content'),
    html.Div(id='hidden-div', style={'display': 'none'}),
])


@app.callback(
    [Output("email-input", "valid"), Output("email-input", "invalid")],
    [Input("email-input", "value")],
)
def check_validity(text):
    if text:
        is_mail = re.match(r"[^@]+@[^@]+\.[^@]+", text) is not None
        return is_mail, not is_mail
    return False, False


@app.callback(
    Output("password-input", "type"),
    Output("password-icon", "className"),
    [Input("password-icon", "n_clicks")],
    [State("password-input", "type")],
)
def toggle_password_visibility(n_clicks, c):
    if n_clicks:
        if n_clicks % 2 == 1:
            return "text", "bi bi-eye"
        else:
            return "password", "bi bi-eye-slash"
    return "password", "bi bi-eye-slash"


@app.callback(
    Output('patient-id-db', 'options'),
    Input('patient-update-button', 'n_clicks')
)
def update_dropdown_patients(n_clicks):
    user_ids = Chest_Data_collection.distinct("userId")
    return [{'label': j, 'value': j} for j in user_ids]


@app.callback(
    [Output('measurement-output', 'children'),
     Output('measurement-interval-component', 'max_intervals'),
     Output('last-username-count', 'data')],
    [Input('submit-patient', 'n_clicks'),
     Input('measurement-interval-component', 'n_intervals')],
    [State('patient-id-db', 'value'),
     State('last-username-count', 'data')],
    prevent_initial_call=True
)
def start_data_collection(n_clicks, measurement_interval, specific_user_id, last_count):
    if n_clicks is None:
        return dash.no_update, dash.no_update, last_count

    if specific_user_id:
        data_list = list(Chest_Data_collection.find({'userId': specific_user_id}))
        if data_list:
            last_five_data = data_list[-5:]
            desired_fields = ["userId", "userName", "PulR", "SPO2", "SBP", "DBP", "ECG_CATEGORY", "RESPIRATION", "PDF"]
            filtered_data = [{field: doc.get(field, None) for field in desired_fields} for doc in last_five_data]
            df = pd.DataFrame(filtered_data)
            df = df[desired_fields]

            df['HR_avg'] = df['PulR'].apply(lambda x: round(sum(x) / len(x)) if len(x) > 0 else None)
            df['SBP_avg'] = df['SBP'].apply(lambda x: round(sum(x) / len(x)) if len(x) > 0 else None)
            df['DBP_avg'] = df['DBP'].apply(lambda x: round(sum(x) / len(x)) if len(x) > 0 else None)

            df = df.drop(columns=['SBP', 'DBP', "PulR"])
            df = df.rename(columns={'SBP_avg': 'Systolic(mmHg)',
                                    'DBP_avg': 'Diastolic(mmHg)', 'HR_avg': 'HeartRate(BPM)'})
            current_count = len(data_list)
            if current_count != last_count['count']:
                new_last_count = {'count': current_count}
                max_intervals = -1
                index = current_count - 1

                if index < current_count:
                    dataset = data_list[index]
                    features_dataframe_filtered = pd.DataFrame({key: pd.Series(value) for key, value
                                                                in dataset.items() if key != '_id'})

                    if not features_dataframe_filtered.empty:
                        return html.Div([
                            dcc.Store(id='stored_feature_data',
                                      data=features_dataframe_filtered.to_dict('records')),
                            dcc.Store(id='stored_history',
                                      data=df.to_dict('records')),
                            html.Div(id='processing-div'),
                        ], style={'marginLeft': '0px', 'marginRight': '0px'}), max_intervals, new_last_count

                    else:
                        return dash.no_update, dash.no_update, last_count
                else:
                    return dash.no_update, dash.no_update, last_count
            else:
                return dash.no_update, dash.no_update, last_count
        else:
            return html.Div([
                html.P("No data is found for this user", className='card-title', style={"color": "red"}),
            ], style={'width': '50%', 'margin': 'auto', 'textAlign': 'center'}), dash.no_update, last_count

    else:
        return html.Div([
            html.P('Please select the patient', className='card-title', style={"color": "red"}),
        ], style={'width': '50%', 'margin': 'auto', 'textAlign': 'center'}), dash.no_update, last_count


@app.callback(Output('processing-div', 'children'),
              Input('stored_feature_data', 'data'))
def processing(stored_data):
    if stored_data is not None:
        stored_df = pd.DataFrame(stored_data)
        hr_value = round(np.mean((stored_df['PulR'].dropna().tolist())))
        sbp_value = round(np.mean((stored_df['SBP'].dropna().tolist())))
        dbp_value = round(np.mean((stored_df['DBP'].dropna().tolist())))

        ecg_category = stored_df["ECG_CATEGORY"].dropna().iloc[0]
        resp_value = round(stored_df["RESPIRATION"].dropna().iloc[0])
        spo2_value = stored_df["SPO2"].dropna().tolist()[0]

        return html.Div([
            html.Div([
                dbc.Container([
                    html.Div([
                        dbc.Row([
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-heart-fill",
                                                                   style={"fontSize": "2rem", "color": "black"}),
                                                            html.P("Heart Rate", className="card-text",
                                                                   style={"color": "black",
                                                                          "textShadow": "0 0 10px rgba(255, 255, 255, "
                                                                                        "0.9)"}),
                                                            html.P(hr_value, className="card-text",
                                                                   style={"color": "black", 'fontWeight': 'bold'}),
                                                        ],
                                                        style={"textAlign": "center"}
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-4",
                                        style={"maxWidth": "540px", "border": "none"},
                                        color="transparent",
                                    )
                                ],
                                xs=12, sm=12, md=6, lg=2, xl=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-droplet",
                                                                   style={"fontSize": "2rem", "color": "black"}),
                                                            html.P("Spo2", className="card-text",
                                                                   style={"color": "black",
                                                                          "textShadow": "0 0 10px rgba(255, 255, 255, "
                                                                                        "0.9)"}),
                                                            html.P(spo2_value, className="card-text",
                                                                   style={"color": "black", 'fontWeight': 'bold'}),
                                                        ],
                                                        style={"textAlign": "center"}
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-4",
                                        style={"maxWidth": "540px", "border": "none"},
                                        color="transparent",
                                    )
                                ],
                                xs=12, sm=12, md=6, lg=2, xl=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-heart-pulse-fill",
                                                                   style={"fontSize": "2rem", "color": "black"}),
                                                            html.P("Blood Pressure", className="card-text",
                                                                   style={"color": "black",
                                                                          "textShadow": "0 0 10px rgba(255, 255, 255, "
                                                                                        "0.5)"}),
                                                            html.P(f"{sbp_value}/{dbp_value} mmHg",
                                                                   className="card-text",
                                                                   style={"color": "black", 'fontWeight': 'bold'}),
                                                        ],
                                                        style={"textAlign": "center"}
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-4",
                                        style={"maxWidth": "540px", "border": "none"},
                                        color="transparent",
                                    )
                                ],
                                xs=12, sm=12, md=6, lg=2, xl=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-activity",
                                                                   style={"fontSize": "2rem", "color": "black"}),
                                                            html.P("Electrocardiogram", className="card-text",
                                                                   style={"color": "black",
                                                                          "textShadow": "0 0 10px rgba(255, 255, 255, "
                                                                                        "0.5)"}),
                                                            html.P(ecg_category, className="card-text",
                                                                   style={"color": "black", 'fontWeight': 'bold'}),
                                                        ],
                                                        style={"textAlign": "center"}
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-4",
                                        style={"maxWidth": "540px", "border": "none"},
                                        color="transparent",
                                    )
                                ],
                                xs=12, sm=12, md=6, lg=2, xl=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-lungs",
                                                                   style={"fontSize": "2rem", "color": "black"}),
                                                            html.P("Respiration Rate", className="card-text",
                                                                   style={"color": "black",
                                                                          "textShadow": "0 0 10px rgba(255, 255, 255, "
                                                                                        "0.5)"}),
                                                            html.P(f"{resp_value} Per minute", className="card-text",
                                                                   style={"color": "black", 'fontWeight': 'bold'}),
                                                        ],
                                                        style={"textAlign": "center"}
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-4",
                                        style={"maxWidth": "540px", "border": "none"},
                                        color="transparent",
                                    )
                                ],
                                xs=12, sm=12, md=6, lg=2, xl=2
                            ),
                        ], justify="around", className="g-3"),

                    ], style={'marginLeft': '50px'}, className="g-3"),
                ], fluid=True),
            ]),
            html.Div(id='output-history'),
        ])

    return dash.no_update


@app.callback(Output('output-history', 'children'),
              Input('stored_history', 'data'))
def processing(stored_data_last_five):
    if stored_data_last_five is not None:
        history_df = pd.DataFrame(stored_data_last_five)
        col = list(history_df.columns.values)
        data = history_df.values.tolist()[::-1]
        table_rows = []
        for index, row in enumerate(data, start=0):
            uid = row[col.index("userId")]
            name = row[col.index("userName")]
            pdf_base64 = row[col.index("PDF")]
            spo2 = row[col.index("SPO2")]
            respiration = round(row[col.index("RESPIRATION")], 3)
            ecg_category = row[col.index("ECG_CATEGORY")]
            heart_rate = row[col.index("HeartRate(BPM)")]
            SBP = row[col.index("Systolic(mmHg)")]
            DBP = row[col.index("Diastolic(mmHg)")]

            pdf_data = base64.b64decode(pdf_base64)
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            pdf_data_url = f"data:application/pdf;base64,{base64_pdf}"

            pdf_link = (
                html.A("View PDF",
                       style={'textAlign': 'center'},
                       href=pdf_data_url,
                       target="_blank",
                       id=f"pdf-link-{index}")
            )
            table_row = html.Tr([
                html.Td(5 - index, style={'textAlign': 'center'}),
                html.Td(uid, style={'textAlign': 'center'}),
                html.Td(name, style={'textAlign': 'center'}),
                html.Td(heart_rate, style={'textAlign': 'center'}),
                html.Td(spo2, style={'textAlign': 'center'}),
                html.Td(respiration, style={'textAlign': 'center'}),
                html.Td(ecg_category, style={'textAlign': 'center'}),
                html.Td(SBP, style={'textAlign': 'center'}),
                html.Td(DBP, style={'textAlign': 'center'}),
                html.Td(pdf_link),
            ])
            table_rows.append(table_row)

        table = dbc.Table(id="my_table",
                          children=[
                              html.Thead(
                                  html.Tr(
                                      [html.Th('Sl.No', style={'textAlign': 'center'}),
                                       html.Th('Patient-Id', style={'textAlign': 'center'}),
                                       html.Th('Name', style={'textAlign': 'center'}),
                                       html.Th('HeartRate(BPM)', style={'textAlign': 'center'}),
                                       html.Th('Blood Oxygen(%)', style={'textAlign': 'center'}),
                                       html.Th('Respiration(per min)', style={'textAlign': 'center'}),
                                       html.Th('ECG', style={'textAlign': 'center'}),
                                       html.Th('Systolic(mmHg)', style={'textAlign': 'center'}),
                                       html.Th('Diastolic(mmHg)', style={'textAlign': 'center'}),
                                       html.Th('Report', style={'textAlign': 'center'})]
                                  )
                              ),
                              html.Tbody(table_rows)
                          ],
                          bordered=True,
                          color='primary',
                          hover=True,
                          responsive=True,
                          striped=True,
                          )
        return html.Div([
            html.H3("History", style={'marginLeft': '0px',
                                      'color': 'black', "fontStyle": "italic",
                                      'fontFamily': 'sans-serif',
                                      'textAlign': 'left'}),
            table
        ], style={'marginLeft': '50px', 'marginRight': '50px'}, className="g-3")


@app.callback([Output('url', 'pathname'),
               Output('authentication_output', 'children')],
              [Input('Login_button', 'n_clicks')],
              [State('email-input', 'value'),
               State('password-input', 'value')],
              prevent_initial_call=True)
def authenticate_user(n_clicks, email, password):
    if n_clicks:
        if not email or not password:
            return '/', html.H1(" ", style={'fontWeight': 'bold',
                                            'font-family': 'Arial',
                                            'textAlign': 'center',
                                            'border-color': '#a0a3a2',
                                            'color': 'red',
                                            'font-size': 20,
                                            })
        if email == "contact@asmaitha.com" and password == "admin@123":
            session['authenticated'] = True
            session['username'] = email
            session['session_id'] = str(uuid.uuid4())
            return '/Real-time', None

        else:
            return '/', html.H1("Please Enter Valid Details", style={'fontWeight': 'bold',
                                                                     'font-family': 'Arial',
                                                                     'textAlign': 'center',
                                                                     'border-color': '#a0a3a2',
                                                                     'color': 'red',
                                                                     'font-size': 20})

    return '/', None


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def render_page_content(pathname):
    if 'authenticated' in session and session['authenticated']:
        if pathname in ["/", "/Login"]:
            return login_page
        elif pathname == "/Real-time":
            return live_page
        elif pathname == "/About":
            return html.P("This is the content of about page. Yay!")
        elif pathname == "/Contact":
            return html.P("This is the content of contact page. Yay!")
        else:
            return html.P("error!!!!")
    else:
        time.sleep(0.3)
        return login_page


@app.callback(
    [Output(f'nav-{name}', 'style') for name in ['Login', 'Real-time', 'About', 'Contact']],
    [Input('url', 'pathname')]
)
def update_active_links(pathname):
    default_style = {"fontSize": "18px", "padding": "10px", "color": 'black'}
    active_style = {"fontSize": "18px", "padding": "10px", 'fontWeight': 'bold', "color": 'black',
                    "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)"}

    login_style = active_style if pathname in ["/Login", "/"] else default_style
    live_style = active_style if pathname == "/Real-time" else default_style
    about_style = active_style if pathname == "/About" else default_style
    contact_style = active_style if pathname == "/Contact" else default_style

    return login_style, live_style, about_style, contact_style


app.clientside_callback(
    """
    function(value1, value2) {
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                document.getElementById('Login_button').click();
            }
        });
        return '';
    }
    """,
    Output('hidden-div', 'children'),
    [Input('email-input', 'value'), Input('password-input', 'value')],
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8000)
