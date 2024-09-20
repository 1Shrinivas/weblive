from main import app
from flask import session
import uuid
import base64
import time
from dash.dependencies import Input, Output, State
from dash import html
from login import login_page
from database import *
from live import live_page


@app.callback(
    [Output(f'nav-{name}', 'style') for name in ['Login', 'Real-time', 'About', 'Contact']],
    [Input('url', 'pathname')]
)
def update_active_links(pathname):
    default_style = {"fontSize": "18px", "padding": "10px", "color": 'black'}
    active_style = {"fontSize": "18px", "padding": "10px", 'fontWeight': 'bold', "color": 'black',
                    "textShadow": "0 0 10px rgba(255, 255, 255, 0.5)"}

    home_style = active_style if pathname == "/Login" else default_style
    register_style = active_style if pathname == "/Real-time" else default_style
    about_style = active_style if pathname == "/About" else default_style
    contact_style = active_style if pathname == "/Contact" else default_style

    return home_style, register_style, about_style, contact_style


# Define the callback function that will handle the authentication
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
        userName = pathname.split("/")[1]
        if pathname in ["/", "/Login"]:
            return login_page
        elif pathname == "/Real-time":
            return live_page
        elif pathname == "/About":
            return html.P("This is the content of about page. Yay!")
        elif pathname == "/Contact":
            return html.P("This is the content of contact page. Yay!")
        else:
            document = Chest_Data_collection.find_one({'userName': userName})
            if document:
                pdf_base64 = document.get('PDF')
                pdf_data = base64.b64decode(pdf_base64)
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_data_url = f"data:application/pdf;base64,{base64_pdf}"
                return html.Div([
                    html.Iframe(src=pdf_data_url, style={"width": "100%", "height": "100%", "border": "none"}),
                ], style={"margin": "0", "padding": "0", "height": "100vh", "width": "100vw"})
            else:
                return html.Div([
                    html.P('Oops! No Record found', className='card-title', style={"color": "red"}),
                ], style={'width': '50%', 'margin': 'auto', 'textAlign': 'center'})
    else:
        time.sleep(0.5)
        return login_page




