import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import subprocess
import os
import datetime

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to calculate the moving average
def calculate_moving_average(df, column, window=7):
    return df[column].rolling(window=window).mean()

# Function to add vertical lines for January 1st
def add_year_lines(fig, df):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Get unique years from the data
    years = df['year'].unique()
    
    for year in years:
        # Check if there are any dates in January for the current year
        if 1 in df[df['year'] == year]['month'].values:
            line_date = pd.Timestamp(year=year, month=1, day=1)
            fig.add_vline(x=line_date, line=dict(color="Red", width=2, dash="dash"), name=f'Jan {year}')

# Function to update the layout of the figures
def update_layout(fig, title):
    fig.update_layout(
        title=title,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        xaxis=dict(
            dtick='M1',                         # Set tick interval to monthly
            tickformat="%b '%y",                # Format for ticks
            ticks='outside',                    # Add ticks outside the plot
            tickangle=-45,                      # Angle of ticks for better readability
            showline=True,                      # Show line on x-axis
            showticklabels=True,                # Ensure tick labels are visible
            ticklen=10,                         # Length of the ticks
            tickcolor='rgba(255, 255, 255, 0.7)',  # Color of the ticks
            gridcolor='rgba(255, 255, 255, 0.3)',  # Color of the grid lines
            linecolor='rgba(255, 255, 255, 0.7)',  # Color of the x-axis line
            gridwidth=1,                        # Width of the grid lines
            showgrid=True,                      # Show grid lines
            zeroline=False,                     # Hide zero line
            linewidth=2,                        # Width of the x-axis line
        ),
        yaxis=dict(
            showgrid=True,                      # Show line on y-axis
            gridwidth=1,                        # Width of the grid lines
            showline=True,                      # Show grid lines
            gridcolor='rgba(255, 255, 255, 0.3)',  # Color of the grid lines
            linecolor='rgba(255, 255, 255, 0.7)',  # Color of the y-axis line
            linewidth=2,                        # Width of the y-axis line
        )
    )

# Load the initial data and create initial figures
def load_data_and_create_figures():
    if os.path.exists('clean_body_data.csv'):
        df = pd.read_csv('clean_body_data.csv')
    else:
        # Handle the case where the file does not exist (provide an empty DataFrame or default data)
        df = pd.DataFrame(columns=['date', 'weight', 'bmi', 'fat'])
    
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate moving averages
    df['weight_ma'] = calculate_moving_average(df, 'weight')
    df['bmi_ma'] = calculate_moving_average(df, 'bmi')
    df['fat_ma'] = calculate_moving_average(df, 'fat')
    
    return df

# Generate initial figures
def generate_figures(df, start_date, end_date):
    df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    
    # Convert 'date' column to datetime if not already done
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    
    # Ensure that 'year' and 'month' columns are computed safely
    df_filtered.loc[:, 'year'] = df_filtered['date'].dt.year
    df_filtered.loc[:, 'month'] = df_filtered['date'].dt.month
    
    weight_fig = go.Figure()
    weight_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['weight'], mode='lines', name='Weight'))
    weight_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['weight_ma'], mode='lines', name='Weight (MA)'))
    add_year_lines(weight_fig, df_filtered)
    update_layout(weight_fig, 'Weight Over Time')

    bmi_fig = go.Figure()
    bmi_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['bmi'], mode='lines', name='BMI'))
    bmi_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['bmi_ma'], mode='lines', name='BMI (MA)'))
    add_year_lines(bmi_fig, df_filtered)
    update_layout(bmi_fig, 'BMI Over Time')

    fat_fig = go.Figure()
    fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['fat'], mode='lines', name='Body Fat'))
    fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['fat_ma'], mode='lines', name='Body Fat (MA)'))
    add_year_lines(fat_fig, df_filtered)
    update_layout(fat_fig, 'Body Fat Percentage Over Time')
    
    return weight_fig, bmi_fig, fat_fig


# Initial Load data
df = load_data_and_create_figures()
start_date = df['date'].min()
end_date = df['date'].max()
initial_figures = generate_figures(df, start_date, end_date)

# Define the layout of the app
app.layout = html.Div(style={'backgroundColor': '#1f1f1f', 'padding': '10px'}, children=[
    html.H1("Personal Data Dashboard", style={'textAlign': 'center', 'color': 'white'}),
    
    # Date range slider
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df['date'].min().date(),
        end_date=df['date'].max().date(),
        display_format='YYYY-MM-DD',
        style={'color': 'white', 'border': '1px solid #4CAF50'}
    ),
    
    # Button to refresh data
    html.Button("Refresh Data", id='refresh-button', n_clicks=0, style={
        'backgroundColor': '#4CAF50',
        'color': 'white',
        'border': 'none',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inline-block',
        'fontSize': '16px',
        'margin': '4px 2px',
        'cursor': 'pointer',
        'borderRadius': '8px'
    }),
    
    # Graphs for displaying data
    dcc.Graph(id='weight-graph', figure=initial_figures[0]),
    dcc.Graph(id='bmi-graph', figure=initial_figures[1]),
    dcc.Graph(id='fat-graph', figure=initial_figures[2])
])

# Define callback to update graphs based on date range
@app.callback(
    [Output('weight-graph', 'figure'),
     Output('bmi-graph', 'figure'),
     Output('fat-graph', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('refresh-button', 'n_clicks')]
)
def update_graphs(start_date, end_date, n_clicks):
    if n_clicks > 0:
        print("Current working directory:", os.getcwd())
        print("Checking if get_all_data.py exists:", os.path.exists('get_all_data.py'))
        print("Checking if clean_body_data.py exists:", os.path.exists('clean_body_data.py'))
        
        # Run scripts to get and clean data
        subprocess.run(['python', 'get_all_data.py'], check=True)  # Run your data fetching script
        subprocess.run(['python', 'clean_body_data.py'], check=True)  # Run your data cleaning script

    # Load the updated data
    df = pd.read_csv('clean_body_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['weight_ma'] = calculate_moving_average(df, 'weight')
    df['bmi_ma'] = calculate_moving_average(df, 'bmi')
    df['fat_ma'] = calculate_moving_average(df, 'fat')
    
    return generate_figures(df, start_date, end_date)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
