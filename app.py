import os
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from src.graphs import create_field_graph, create_spin_lattice_animation


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/style.css'])

server = app.server

app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            [
                html.H2('Spin Lattice with Force Field'),
                html.Br(),
                html.H5('Force Field:'),
                dcc.Dropdown(
                    id='field-dropdown',
                    options=[
                        {'label': 'uniform', 'value': 'uniform'},
                        {'label': 'increasing curl', 'value': 'increasing curl'},
                        {'label': 'decreasing curl', 'value': 'decreasing curl'},
                        {'label': 'curl', 'value': 'curl'},
                        {'label': 'increasing radial', 'value': 'increasing radial'},
                        {'label': 'decreasing radial', 'value': 'decreasing radial'},
                        {'label': 'radial', 'value': 'radial'}
                    ],
                    multi=False,
                    value='uniform',
                    style={
                        'color': 'black'
                    }
                ),
                dcc.Graph(
                    id='field-graph', 
                    config={
                        'displayModeBar': False
                    },
                    style={'width': '20vw', 'height': '20vw', 'padding-left': '15px'}
                ),
                html.H5('Force Field Strength:'),
                dcc.Slider(-1, 1, marks=None, value=.1, id='field_coefficient', tooltip={"placement": "top", "always_visible": True}),
                html.H5('Spin Interaction Strength:'),
                dcc.Slider(-1, 1, marks=None, value=.1, id='spin_coefficient', tooltip={"placement": "top", "always_visible": True}),
                
            ],
            width=3,
            style={
                'color': 'white',
                'padding': '30px',
                'background': '#004c6d',
                'margin-right': '10px'
            }
        ),
        dbc.Col(
            [
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=html.Div(id='loading-output'),
                    style={
                        'margin': 'auto'
                    }
                ),
                dcc.Graph(
                    id='lattice-graph',
                    style={'width': 'min(100vh, 70vw)', 'height': 'min(100vh, 70vw)'}, 
                    config={
                        'displayModeBar': False
                    }
                )
            ],
            width=7
        )
    ])
    ],
    style={
        'background': '#8aa1b4'
    }
)


@app.callback(Output('field-graph', 'figure'), Input('field-dropdown', 'value'))
def display_field(field_type):
    return create_field_graph(field_type)

@app.callback([Output('lattice-graph', 'figure'), Output("loading-output", "children")], [Input('field-dropdown', 'value'), Input('field_coefficient', 'value'), Input('spin_coefficient', 'value')])
def lattice_callback(field_type, field_coefficient, spin_coefficient):
    
    return create_spin_lattice_animation(field_type, field_coefficient, spin_coefficient), None

if __name__ == '__main__':
    app.run_server(debug=not os.environ.get('PRODUCTION'))