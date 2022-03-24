import os
from dash import Dash, dcc, html, Input, Output
from src.graphs import create_field_graph, create_spin_lattice_animation


app = Dash(__name__, external_stylesheets=['/assets/style.css'])

server = app.server



app.layout = html.Div([
    html.Div(
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
                style={'width': '15rem', 'height': '15rem', 'margin': 'auto'}
            ),
            html.H4('Force Field Strength:'),
            dcc.Slider(-1, 1, marks=None, value=.5, id='field_coefficient', tooltip={"placement": "top", "always_visible": True}),
            html.H4('Spin Interaction Strength:'),
            dcc.Slider(-1, 1, marks=None, value=.5, id='spin_coefficient', tooltip={"placement": "top", "always_visible": True}),            
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "20rem",
            "padding": "2rem 1rem",
            "background-color": "#f8f9fa",
        }
    ),
    html.Div(
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
                style={'width': 'min(70vh, 70vw)', 'height': 'min(70vh, 70vw)', 'margin': 'auto'}, 
                config={
                    'displayModeBar': False
                }
            )
        ],
        style={
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
        }
    )]
)


@app.callback(Output('field-graph', 'figure'), Input('field-dropdown', 'value'))
def display_field(field_type):
    return create_field_graph(field_type)

@app.callback([Output('lattice-graph', 'figure'), Output("loading-output", "children")], [Input('field-dropdown', 'value'), Input('field_coefficient', 'value'), Input('spin_coefficient', 'value')])
def lattice_callback(field_type, field_coefficient, spin_coefficient): 
    return create_spin_lattice_animation(field_type, field_coefficient, spin_coefficient), None

if __name__ == '__main__':
    app.run_server(debug=not os.environ.get('PRODUCTION'))