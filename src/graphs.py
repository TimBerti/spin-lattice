import plotly.figure_factory as ff
import plotly.graph_objects as go
from .spin_lattice import SpinLatticeWithField, Field


def create_field_graph(field_type):
    field = Field(field_type)
    fig = ff.create_quiver(field.grid.x, field.grid.y, field.x, field.y, scale=.5, marker=dict(color='black'))
    fig.update_layout(
            plot_bgcolor= 'rgba(0, 0, 0, 0)',
            paper_bgcolor= 'rgba(0, 0, 0, 0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
    return fig


def create_frames(field_type, field_coefficient=.1, spin_coefficient=.1, increment=.1, n_frames=30, n_per_frame=10):

    spin_lattice_with_field = SpinLatticeWithField(field_coefficient, spin_coefficient, field_args=dict(field_type=field_type))

    def recursively_append_frames(increment, n_frames, n_per_frame, frames=[]):
        if n_frames == 0:
            return frames
        n_frames -= 1

        frames.append(
            ff.create_quiver(
                spin_lattice_with_field.grid.x, 
                spin_lattice_with_field.grid.y, 
                spin_lattice_with_field.spin_lattice.x, 
                spin_lattice_with_field.spin_lattice.y, 
                scale=.5, 
                marker=dict(color='black')
            )
        )
        
        spin_lattice_with_field.incrementally_rotate_spins_according_to_force(increment, n_per_frame)

        return recursively_append_frames(increment, n_frames, n_per_frame, frames)

    return recursively_append_frames(increment, n_frames, n_per_frame)


def create_spin_lattice_animation(field_type='uniform', field_coefficient=1, spin_coefficient=1):

    frames = create_frames(field_type, field_coefficient, spin_coefficient)

    fig = go.Figure(
        data=[frames[0].data[0]],
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
            ]
        ),
        frames=[go.Frame(data=[frame.data[0]]) for frame in frames[1:]]
    )

    return fig