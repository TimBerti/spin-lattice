import os
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from src.utils import field, recursive_frames


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
                dcc.Slider(-1, 1, marks=None, value=.1, id='alpha', tooltip={"placement": "top", "always_visible": True}),
                html.H5('Spin Interaction Strength:'),
                dcc.Slider(-1, 1, marks=None, value=.1, id='beta', tooltip={"placement": "top", "always_visible": True}),
                
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

n_frames = 20
n_per_frame = 100

n = 20
m = 20

x, y = np.meshgrid(np.linspace(-10, 10, m), np.linspace(-10, 10, n))

@app.callback(Output('field-graph', 'figure'), Input('field-dropdown', 'value'))
def display_field(field_type):
    x_field, y_field = field(x, y, field_type)
    fig = ff.create_quiver(x, y, x_field, y_field, scale=.5, marker=dict(color='black'))
    fig.update_layout(
            plot_bgcolor= 'rgba(0, 0, 0, 0)',
            paper_bgcolor= 'rgba(0, 0, 0, 0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
    return fig


@app.callback([Output('lattice-graph', 'figure'), Output("loading-output", "children")], [Input('field-dropdown', 'value'), Input('alpha', 'value'), Input('beta', 'value')])
def update_lattice(field_type, alpha, beta):
    
    theta = np.random.rand(n, m) * 2 * np.pi

    x_spin, y_spin = np.sin(theta), np.cos(theta)

    x_field, y_field = field(x, y, field_type)

    frames = recursive_frames(x, y, x_spin, y_spin, x_field, y_field, .1*alpha, .1*beta, n_frames, n_per_frame, [])

    fig = go.Figure(
        data=[ff.create_quiver(x, y, x_spin, y_spin, scale=.5, marker=dict(color='black')).data[0]],
        layout=go.Layout(
            plot_bgcolor= 'rgba(0, 0, 0, 0)',
            paper_bgcolor= 'rgba(0, 0, 0, 0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode=False,
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                dict(frame=dict(duration=150, redraw=False))
                            ]
                        )
                    ]
                )
            ],
            sliders = [
                dict(
                    transition= dict(duration= 0 ),
                    x=0,#slider starting position  
                    y=0, 
                    currentvalue=dict(font=dict(size=12), 
                                    prefix='Time: ', 
                                    visible=True, 
                                    xanchor= 'center'
                                    ),  
                    len=1.0 #slider length
                )
           ]
        ),
        frames=frames
    )

    return fig, None

if __name__ == '__main__':
    app.run_server(debug=not os.environ.get('PRODUCTION'))