from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from fishcast import get_forecast, calculate_fishing_index, ForecastData

# Initialize the Dash app
app = Dash(__name__)

# Add custom CSS and basic icon information
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Fishcast</title>
        <link rel="icon" type="image/png" href="assets/icon_small.png">
        <link rel="manifest" href="assets/site.webmanifest">
        {%css%}
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #1a1a1a;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define color scheme
COLORS = {
    'background': '#1a1a1a',
    'card_background': '#2d2d2d',
    'text': '#ffffff',
    'muted_text': '#a0a0a0',
    'accent': '#4CAF50',
    'error': '#ff4444',
    'grid': '#404040'
}

# Define common styles
FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

COMMON_STYLES = {
    'fontFamily': FONT_FAMILY,
    'fontWeight': '400',
    'color': COLORS['text'],
    'width': '100%',
    'boxSizing': 'border-box'
}

HEADER_STYLES = {
    'fontFamily': FONT_FAMILY,
    'fontWeight': '600',
    'textAlign': 'center',
    'margin': '10px',
    'color': COLORS['text'],
    'fontSize': '24px'
}

GRAPH_LAYOUT = {
    'plot_bgcolor': COLORS['card_background'],
    'paper_bgcolor': COLORS['card_background'],
    'font': {
        'color': COLORS['text'],
        'family': FONT_FAMILY
    },
    'xaxis': {
        'gridcolor': COLORS['grid'],
        'showgrid': True,
        'color': COLORS['text']
    },
    'yaxis': {
        'gridcolor': COLORS['grid'],
        'showgrid': True,
        'color': COLORS['text']
    }
}

def get_wind_direction_label(degrees):
    """Convert degrees to cardinal direction labels"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    val = int((degrees/22.5) + 0.5)
    return directions[val % 16]

def create_wind_graph(df):
    """Create a wind speed graph with direction markers"""
    # Create the base wind speed line
    fig = px.line(
        df,
        x='time',
        y='windspeed',
        title='Wind Speed and Direction'
    )
    
    # Add direction markers
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['windspeed'],
            mode='markers+text',
            text=[get_wind_direction_label(d) for d in df['winddirection']],
            textposition='top center',
            name='Direction',
            textfont=dict(size=10),
            marker=dict(size=8),
            showlegend=False
        )
    )
    
    # Update layout
    fig.update_layout(
        font_family=FONT_FAMILY,
        title_font_family=FONT_FAMILY,
        xaxis_title="Time",
        yaxis_title="Wind Speed (m/s)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey', showgrid=True),
        yaxis=dict(gridcolor='lightgrey', showgrid=True),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate="<br>".join([
            "Time: %{x}",
            "Speed: %{y} m/s",
            "<extra></extra>"
        ])
    )
    
    return fig

def get_forecast_data(place, include_sealevel=False):
    """Fetch and process forecast data for the dashboard"""
    try:
        forecast_data_list = get_forecast(
            timezone="Europe/Helsinki",
            place=place,
            hours=48,
            sealevel=place if include_sealevel else None
        )
        
        if not forecast_data_list:
            return pd.DataFrame(), f"No data found for {place}"
        
        fishing_index_forecast = []
        for i, data in enumerate(forecast_data_list):
            if i == 0:
                continue
            
            prev_data = ForecastData(**forecast_data_list[i-1])
            curr_data = ForecastData(**data)
            calculate_fishing_index(curr_data, prev_data)
            fishing_index_forecast.append(curr_data)
        
        df = pd.DataFrame([
            {
                'time': data.time,
                'fishing_index': data.fishing_index,
                'pressure': data.pressure,
                'temperature': data.temperature,
                'windspeed': data.windspeed,
                'winddirection': data.winddirection,
                'sealevel': data.sealevel if include_sealevel else None
            }
            for data in fishing_index_forecast
        ])
        
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Define the layout
app.layout = html.Div([
    dcc.Store(id='data-fetched', data=False),
    
    # Logo container with vignette effect
    html.Div([
        html.Div([
            html.Img(
                src='assets/logo.jpg',
                style={
                    'height': 'auto',
                    'width': '300px',
                    'marginBottom': '0px',
                    'position': 'relative',
                    'zIndex': '1'
                }
            )
        ], style={
            'position': 'relative',
            'display': 'inline-block',
            'maskImage': 'radial-gradient(ellipse at center, black 40%, transparent 70%)',
            'WebkitMaskImage': 'radial-gradient(ellipse at center, black 40%, transparent 70%)',
        })
    ], style={
        'textAlign': 'center',
        'marginBottom': '20px',
        'marginTop': '20px'
    }),
    
    # Form container
    html.Div([
        # Location input
        html.Div([
            html.Label(
                'Location: ',
                style={
                    **COMMON_STYLES,
                    'fontSize': '16px',
                    'marginBottom': '10px',
                    'display': 'block'
                }
            ),
            dcc.Input(
                id='place-input',
                type='text',
                placeholder='Enter location...',
                style={
                    **COMMON_STYLES,
                    'padding': '8px 12px',
                    'borderRadius': '6px',
                    'border': f'1px solid {COLORS["grid"]}',
                    'fontSize': '14px',
                    'backgroundColor': COLORS['card_background'],
                    'color': COLORS['text'],
                    'marginBottom': '15px',
                    'display': 'block',
                    'maxWidth': '100%'
                }
            ),
        ], style={'marginBottom': '15px'}),
        
        # Sea level checkbox
        html.Div([
            dcc.Checklist(
                id='sealevel-checkbox',
                options=[{'label': ' Include sea level forecast', 'value': 'yes'}],
                value=[],
                style={
                    **COMMON_STYLES,
                    'marginBottom': '15px',
                    'display': 'block'
                }
            ),
        ]),
        
        # Get Forecast button
        html.Button(
            'Get Forecast',
            id='submit-button',
            n_clicks=0,
            style={
                **COMMON_STYLES,
                'padding': '12px 16px',
                'backgroundColor': COLORS['accent'],
                'color': COLORS['text'],
                'border': 'none',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'fontWeight': '500',
                'marginBottom': '15px',
                'display': 'block',
                'maxWidth': '100%'
            }
        ),
        
        # Error and update time messages
        html.Div([
            html.Div(
                id='error-message',
                style={
                    **COMMON_STYLES,
                    'color': COLORS['error'],
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'marginBottom': '5px'
                }
            ),
            
            html.Div(
                id='last-update-time',
                style={
                    **COMMON_STYLES,
                    'color': COLORS['muted_text'],
                    'fontSize': '14px'
                }
            )
        ])
    ], style={
        'padding': '15px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '8px',
        'margin': '10px',
        'maxWidth': '570px',
        'width': '90%',
        'marginLeft': 'auto',
        'marginRight': 'auto'
    }),
    
    # Graphs container with initial display: none
    html.Div([
        # Main fishing index graph
        html.Div([
            dcc.Graph(
                id='fishing-index-graph',
                style={
                    'height': '300px'
                },
                config={
                    'displayModeBar': False,
                    'responsive': True
                }
            )
        ], style={
            'marginBottom': '10px',
            'backgroundColor': COLORS['card_background'],
            'padding': '10px',
            'borderRadius': '8px'
        }),
        
        # Pressure graph
        html.Div([
            dcc.Graph(
                id='pressure-graph',
                style={
                    'height': '300px'
                },
                config={
                    'displayModeBar': False,
                    'responsive': True
                }
            )
        ], style={
            'marginBottom': '10px',
            'backgroundColor': COLORS['card_background'],
            'padding': '10px',
            'borderRadius': '8px'
        }),
        
        # Temperature graph
        html.Div([
            dcc.Graph(
                id='temperature-graph',
                style={
                    'height': '300px'
                },
                config={
                    'displayModeBar': False,
                    'responsive': True
                }
            )
        ], style={
            'marginBottom': '10px',
            'backgroundColor': COLORS['card_background'],
            'padding': '10px',
            'borderRadius': '8px'
        }),
        
        # Wind speed graph
        html.Div([
            dcc.Graph(
                id='wind-graph',
                style={
                    'height': '300px'
                },
                config={
                    'displayModeBar': False,
                    'responsive': True
                }
            )
        ], style={
            'marginBottom': '10px',
            'backgroundColor': COLORS['card_background'],
            'padding': '10px',
            'borderRadius': '8px'
        }),
        
        # Sea level graph (conditionally displayed)
        html.Div([
            dcc.Graph(
                id='sealevel-graph',
                style={
                    'height': '300px'
                },
                config={
                    'displayModeBar': False,
                    'responsive': True
                }
            )
        ], style={
            'marginBottom': '10px',
            'backgroundColor': COLORS['card_background'],
            'padding': '10px',
            'borderRadius': '8px',
            'display': 'none'
        }, id='sealevel-container')
    ], style={
        'maxWidth': '600px',
        'width': '90%',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'display': 'none'  # Initially hidden
    }, id='graphs-container')  # Add ID to control visibility
], style={
    **COMMON_STYLES,
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'padding': '10px',
    'margin': '0',
    'width': '100%',
    'boxSizing': 'border-box'
})

@callback(
    [Output('fishing-index-graph', 'figure'),
     Output('pressure-graph', 'figure'),
     Output('temperature-graph', 'figure'),
     Output('wind-graph', 'figure'),
     Output('sealevel-graph', 'figure'),
     Output('sealevel-container', 'style'),
     Output('last-update-time', 'children'),
     Output('error-message', 'children'),
     Output('graphs-container', 'style'),  # Add output for graphs container
     Output('data-fetched', 'data')],  # Add output for data store
    [Input('submit-button', 'n_clicks'),
     Input('place-input', 'n_submit')],
    [State('place-input', 'value'),
     State('sealevel-checkbox', 'value')],
    prevent_initial_call=True
)
def update_graphs(n_clicks, n_submit, place, sealevel_checked):
    include_sealevel = 'yes' in (sealevel_checked or [])
    sealevel_style = {
        'marginBottom': '10px',
        'backgroundColor': COLORS['card_background'],
        'padding': '10px',
        'borderRadius': '8px',
        'display': 'block' if include_sealevel else 'none'
    }
    
    # Base style for graphs container
    graphs_container_style = {
        'maxWidth': '600px',
        'width': '90%',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'display': 'none'  # Hidden by default
    }
    
    if not place:
        empty_fig = go.Figure()
        empty_fig.update_layout(**GRAPH_LAYOUT, title={'text': "Enter a location to see forecast", 'font': {'color': COLORS['text']}})
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, sealevel_style, "", "Please enter a location", graphs_container_style, False
    
    df, error = get_forecast_data(place, include_sealevel)
    
    if error:
        empty_fig = go.Figure()
        empty_fig.update_layout(**GRAPH_LAYOUT, title={'text': f"No data available for {place}", 'font': {'color': COLORS['text']}})
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, sealevel_style, "", f"Error: {error}", graphs_container_style, False
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(**GRAPH_LAYOUT, title={'text': f"No data available for {place}", 'font': {'color': COLORS['text']}})
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, sealevel_style, "", f"No data found for {place}", graphs_container_style, False
    
    # Show graphs container when data is successfully fetched
    graphs_container_style['display'] = 'block'
    
    # Create fishing index figure
    fishing_fig = go.Figure()
    fishing_fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['fishing_index'],
        mode='lines+markers',
        line={'color': COLORS['accent']}
    ))
    fishing_fig.update_layout(
        **GRAPH_LAYOUT,
        title={'text': f'Fishing Index Forecast for next 48 hours', 'font': {'color': COLORS['text']}},
        yaxis_range=[0, 100]
    )
    
    # Create pressure figure
    pressure_fig = go.Figure()
    pressure_fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['pressure'],
        mode='lines+markers',
        line={'color': COLORS['accent']}
    ))
    pressure_fig.update_layout(
        **GRAPH_LAYOUT,
        title={'text': 'Air Pressure (hPa)', 'font': {'color': COLORS['text']}}
    )
    
    # Create temperature figure
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['temperature'],
        mode='lines+markers',
        line={'color': COLORS['accent']}
    ))
    temp_fig.update_layout(
        **GRAPH_LAYOUT,
        title={'text': 'Temperature (°C)', 'font': {'color': COLORS['text']}}
    )
    
    # Create wind figure with direction markers
    wind_fig = go.Figure()
    wind_fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['windspeed'],
        mode='lines+markers+text',
        line={'color': COLORS['accent']},
        text=[get_wind_direction_label(dir) for dir in df['winddirection']],
        textposition='top center',
        textfont={'color': COLORS['muted_text']}
    ))
    wind_fig.update_layout(
        **GRAPH_LAYOUT,
        title={'text': 'Wind Speed (m/s) with Direction', 'font': {'color': COLORS['text']}}
    )
    
    # Create sea level figure if data exists
    if include_sealevel and 'sealevel' in df.columns and df['sealevel'].notna().any():
        sealevel_fig = go.Figure()
        sealevel_fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['sealevel'],
            mode='lines+markers',
            line={'color': COLORS['accent']}
        ))
        sealevel_fig.update_layout(
            **GRAPH_LAYOUT,
            title={'text': 'Sea Level (cm)', 'font': {'color': COLORS['text']}}
        )
    else:
        sealevel_fig = go.Figure()
        sealevel_fig.update_layout(
            **GRAPH_LAYOUT,
            title={'text': 'Sea level data not available', 'font': {'color': COLORS['text']}}
        )
    
    # Update graph layouts for mobile
    mobile_layout = {
        **GRAPH_LAYOUT,
        'margin': dict(l=40, r=20, t=40, b=40),
        'height': 300,
        'xaxis': {
            **GRAPH_LAYOUT['xaxis'],
            'tickangle': 45,
            'tickformat': '%H:%M\n%d-%m'
        }
    }
    
    # Update each figure with mobile layout
    fishing_fig.update_layout(**mobile_layout)
    pressure_fig.update_layout(**mobile_layout)
    temp_fig.update_layout(**mobile_layout)
    wind_fig.update_layout(**mobile_layout)
    sealevel_fig.update_layout(**mobile_layout)
    
    update_time = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({place})"
    
    return fishing_fig, pressure_fig, temp_fig, wind_fig, sealevel_fig, sealevel_style, update_time, "", graphs_container_style, True

def get_wind_direction(degrees):
    """Convert degrees to cardinal direction"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    val = int((degrees/22.5) + 0.5)
    return directions[val % 16]

if __name__ == '__main__':
    app.run(debug=False) 