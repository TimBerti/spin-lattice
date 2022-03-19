import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


def field(x, y, field_type):
    if field_type == 'increasing curl':
        return -.25*y, .25*x
    if field_type == 'decreasing curl':
        return -4*y / (x**2 + y**2), 4*x / (x**2 + y**2)
    if field_type == 'curl':
        return -y / np.sqrt(x**2 + y**2), x / np.sqrt(x**2 + y**2)
    if field_type == 'increasing radial':
        return .25*x, .25*y
    if field_type == 'decreasing radial':
        return 4*x / (x**2 + y**2), 4*y / (x**2 + y**2)
    if field_type == 'radial':
        return x / np.sqrt(x**2 + y**2), y / np.sqrt(x**2 + y**2)
    if field_type == 'uniform':
        return np.ones(x.shape), np.ones(x.shape)

def angular_momentum(x_spin, y_spin, x_force, y_force):
    return x_spin*y_force - y_spin*x_force

def rotate(x, y, theta):
    return np.cos(theta) * x + np.sin(theta) * y, -np.sin(theta) * x + np.cos(theta) * y

def summed_neighbors(x_spin, y_spin):
    n, m = x_spin.shape

    x_tot = np.c_[x_spin[:, 1:], np.zeros((n, 1))] \
        + np.c_[np.zeros((n, 1)), x_spin[:, :-1]] \
        + np.r_[x_spin[1:, :], np.zeros((1, m))] \
        + np.r_[np.zeros((1, m)), x_spin[:-1, :]] \

    y_tot = np.c_[y_spin[:, 1:], np.zeros((n, 1))] \
        + np.c_[np.zeros((n, 1)), y_spin[:, :-1]] \
        + np.r_[y_spin[1:, :], np.zeros((1, m))] \
        + np.r_[np.zeros((1, m)), y_spin[:-1, :]] \
    
    return x_tot, y_tot

def next_spins(x_spin, y_spin, x_field, y_field, alpha, beta):
    x_interaction, y_interaction = summed_neighbors(x_spin, y_spin)

    field_momentum = angular_momentum(x_spin, y_spin, x_field, y_field)
    interaction_momentum = angular_momentum(x_spin, y_spin, x_interaction, y_interaction)

    total_angular_momentum = alpha * field_momentum + beta * interaction_momentum
    
    return rotate(x_spin, y_spin, total_angular_momentum)

def recursive_frames(x, y, x_spin, y_spin, x_field, y_field, alpha, beta, n_frames, n_per_frame, frames):
    if n_frames == 0:
        return frames
    n_frames -= 1

    for _ in range(n_per_frame):
        x_spin, y_spin = next_spins(x_spin, y_spin, x_field, y_field, alpha, beta)

    frames.append(go.Frame(data=[ff.create_quiver(x, y, x_spin, y_spin, scale=.5).data[0]]))

    return recursive_frames(x, y, x_spin, y_spin, x_field, y_field, alpha, beta, n_frames, n_per_frame, frames)


app = Dash(__name__)

server = app.server

app.layout = html.Div([
    html.H2('Spin lattice with force field'),
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
            'width': '150px'
        }
    ),
    dcc.Graph(id='field-graph',style={'width': '90vh', 'height': '90vh'}),
    dcc.Graph(id='lattice-graph',style={'width': '90vh', 'height': '90vh'}),
    dcc.Slider(-1, 1, marks=None, value=.1, id='alpha', tooltip={"placement": "top", "always_visible": True}),
    dcc.Slider(-1, 1, marks=None, value=.1, id='beta', tooltip={"placement": "top", "always_visible": True})
])

n_frames = 20
n_per_frame = 100

n = 20
m = 20

x, y = np.meshgrid(np.linspace(-10, 10, m), np.linspace(-10, 10, n))

@app.callback(Output('field-graph', 'figure'), Input('field-dropdown', 'value'))
def display_field(field_type):
    x_field, y_field = field(x, y, field_type)
    return ff.create_quiver(x, y, x_field, y_field, scale=.5)


@app.callback(Output('lattice-graph', 'figure'), [Input('field-dropdown', 'value'), Input('alpha', 'value'), Input('beta', 'value')])
def update_lattice(field_type, alpha, beta):
    
    theta = np.random.rand(n, m) * 2 * np.pi

    x_spin, y_spin = np.sin(theta), np.cos(theta)

    x_field, y_field = field(x, y, field_type)

    frames = recursive_frames(x, y, x_spin, y_spin, x_field, y_field, .1*alpha, .1*beta, n_frames, n_per_frame, [])

    fig = go.Figure(
        data=[ff.create_quiver(x, y, x_spin, y_spin, scale=.5).data[0]],
        layout=go.Layout(
            title="Start Title",
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
            ]
        ),
        frames=frames
    )

    return fig

if __name__ == '__main__':
    app.run_server()