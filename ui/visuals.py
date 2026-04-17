import plotly.graph_objects as go
import numpy as np

def plot_isolux_contour(x_points, y_points, lux_grid, target_lux):
    fig = go.Figure(data=
        go.Contour(
            z=lux_grid,
            x=x_points,
            y=y_points,
            colorscale='Viridis',
            contours=dict(
                start=0,
                end=np.max(lux_grid) * 1.1 if np.max(lux_grid)>0 else 1,
                size=max(50, np.max(lux_grid)/10),
                showlabels=True,
                labelfont=dict(size=12, color='white')
            ),
            colorbar=dict(title='Illuminance (Lux)'),
            hoverinfo='z+x+y'
        ))
        
    fig.add_trace(go.Contour(
        z=lux_grid,
        x=x_points,
        y=y_points,
        contours_coloring='lines',
        showscale=False,
        contours=dict(
            start=target_lux,
            end=target_lux,
            size=1,
            color='red',
        ),
        hoverinfo='skip'
    ))

    fig.update_layout(
        title="2D Isolux Contour Map",
        xaxis_title="Room Length (m)",
        yaxis_title="Room Width (m)",
        width=700,
        height=500
    )
    return fig

def plot_3d_room(length, width, height, workplane_h, fixtures_coords):
    fig = go.Figure()

    fig.add_trace(go.Surface(
        z=np.zeros((2,2)),
        x=[[0, length], [0, length]],
        y=[[0, 0], [width, width]],
        colorscale='Greys',
        showscale=False,
        opacity=0.3,
        name="Floor"
    ))
    
    fig.add_trace(go.Surface(
        z=np.full((2,2), workplane_h),
        x=[[0, length], [0, length]],
        y=[[0, 0], [width, width]],
        colorscale='Blues',
        showscale=False,
        opacity=0.4,
        name="Workplane"
    ))

    fx = [f[0] for f in fixtures_coords]
    fy = [f[1] for f in fixtures_coords]
    fz = [height for _ in fixtures_coords]
    
    fig.add_trace(go.Scatter3d(
        x=fx, y=fy, z=fz,
        mode='markers',
        marker=dict(size=8, color='gold', symbol='diamond'),
        name="Luminaires"
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, length], title="Length (m)"),
            yaxis=dict(range=[0, width], title="Width (m)"),
            zaxis=dict(range=[0, height], title="Height (m)"),
            camera=dict(eye=dict(x=-1.5, y=-1.5, z=1.2))
        ),
        title="3D Room & Fixture Layout",
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )
    
    return fig
