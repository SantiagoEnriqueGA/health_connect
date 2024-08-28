import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import subprocess
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("ploty_dash.log"),
        logging.StreamHandler()
    ]
)

app = dash.Dash(__name__)       # Initialize the Dash app

def calculate_moving_average(df, column, window=7):
    """
    Calculate the moving average of a column in a DataFrame.
    Parameters:
        - df (pandas.DataFrame): The DataFrame containing the data.
        - column (str): The name of the column to calculate the moving average for.
        - window (int): The size of the moving window. Default is 7.
    Returns:
        - pandas.Series: The moving average of the specified column.
    """
    return df[column].rolling(window=window).mean()

def add_year_lines(fig, df):
    """
    Adds vertical lines to a Plotly figure for each year in the given DataFrame.
    Parameters:
        - fig (plotly.graph_objects.Figure): The Plotly figure to add the vertical lines to.
        - df (pandas.DataFrame): The DataFrame containing the date information.
    Returns:
        None
    """
    df['date'] = pd.to_datetime(df['date'])     # Convert 'date' column to datetime if not already done
    df['year'] = df['date'].dt.year             # Extract the year from the date column
    df['month'] = df['date'].dt.month           # Extract the month from the date column
    
    years = df['year'].unique()                 # Get the unique years in the DataFrame
    
    for year in years:                                              # Iterate over each year
        if 1 in df[df['year'] == year]['month'].values:             # Check if January data is available for the year
            line_date = pd.Timestamp(year=year, month=1, day=1)     # Create a date object for January 1st of the year
            fig.add_vline(x=line_date, line=dict(color="Red", width=2, dash="dash"), name=f'Jan {year}')

def update_layout(fig, title):
    """
    Update the layout of a Plotly figure.
    Parameters:
        - fig: Plotly figure object
        - title: Title of the figure
    Returns:
        None
    """
    fig.update_layout(
        title={
            'text': title,          # Set the title of the figure
            'x': 0.5,               # Center the title
            'xanchor': 'center'     # Anchor the title in the center
        },
        paper_bgcolor='rgba(0, 0, 0, 0)',       # Set the background color of the plot
        plot_bgcolor='rgba(0, 0, 0, 1)',        # Set the background color of the plot area
        font=dict(color='white'),               # Set the font color to white
        xaxis=dict(                                         
            dtick='M1',                         # Set tick interval to monthly
            tickformat="%b\n%Y",                # Format for ticks
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

def load_data_and_create_figures():
    """
    Load data from 'clean_body_data.csv' if it exists, otherwise provide an empty DataFrame or default data.
    Convert the 'date' column to datetime.
    Calculate moving averages for 'weight', 'bmi', and 'fat' columns.
    Returns:
        df (pandas.DataFrame): The DataFrame containing the loaded data and calculated moving averages.
    """
    if os.path.exists('clean_body_data.csv'):       # Check if the file exists
        df = pd.read_csv('clean_body_data.csv')     # Load the data from the file
    else:                                           # Handle the case where the file does not exist (provide an empty DataFrame or default data)
        df = pd.DataFrame(columns=['date', 'weight', 'bmi', 'fat'])
    
    df['date'] = pd.to_datetime(df['date'])                     # Convert 'date' column to datetime if not already done
    
    df['weight_ma'] = calculate_moving_average(df, 'weight')    # Calculate moving average for 'weight' column
    df['bmi_ma'] = calculate_moving_average(df, 'bmi')          # Calculate moving average for 'bmi' column
    df['fat_ma'] = calculate_moving_average(df, 'fat')          # Calculate moving average for 'fat' column
    
    return df

def generate_figures(df, start_date, end_date, bmi_fat_selected_lines, weight_selected_lines):
    """
    Generate figures for BMI, Body Fat Percentage, and Weight over time, based on the selected date range and lines.
    Parameters:
        - df (DataFrame): The input DataFrame containing the data.
        - start_date (str or datetime): The start date for filtering the data.
        - end_date (str or datetime): The end date for filtering the data.
        - bmi_fat_selected_lines (list): List of selected lines for BMI and Body Fat Percentage.
        - weight_selected_lines (list): List of selected lines for Weight.
    Returns:
        - weight_fig (Figure): The figure for Weight over time.
        - bmi_fat_fig (Figure): The figure for BMI and Body Fat Percentage over time.
    """
    df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()  # Filter the data based on the date range
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])                       # Convert 'date' column to datetime if not already done
    
    df_filtered.loc[:, 'year'] = df_filtered['date'].dt.year        # Extract the year from the date column
    df_filtered.loc[:, 'month'] = df_filtered['date'].dt.month      # Extract the month from the date column
    
    
    bmi_fat_fig = go.Figure()       # Create a new figure for BMI and Body Fat Percentage
    if 'bmi' in bmi_fat_selected_lines:
        bmi_fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['bmi'], mode='lines', name='BMI'))                # Add BMI data to the figure
    if 'bmi_ma' in bmi_fat_selected_lines:
        bmi_fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['bmi_ma'], mode='lines', name='BMI (MA)'))        # Add BMI moving average data to the figure
    if 'fat' in bmi_fat_selected_lines:
        bmi_fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['fat'], mode='lines', name='Body Fat'))           # Add Body Fat Percentage data to the figure
    if 'fat_ma' in bmi_fat_selected_lines:        
        bmi_fat_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['fat_ma'], mode='lines', name='Body Fat (MA)'))   # Add Body Fat Percentage moving average data to the figure
    add_year_lines(bmi_fat_fig, df_filtered)                                # Add vertical lines for each year
    update_layout(bmi_fat_fig, 'BMI and Body Fat Percentage Over Time')     # Update the layout of the figure
    
    weight_fig = go.Figure()        # Create a new figure for Weight over time
    if 'weight' in weight_selected_lines:
        weight_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['weight'], mode='lines', name='Weight'))           # Add Weight data to the figure
    if 'weight_ma' in weight_selected_lines:
        weight_fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['weight_ma'], mode='lines', name='Weight (MA)'))   # Add Weight moving average data to the figure
    add_year_lines(weight_fig, df_filtered)             # Add vertical lines for each year
    update_layout(weight_fig, 'Weight Over Time')       # Update the layout of the figure
    
    return weight_fig, bmi_fat_fig

# Initial setup
df = load_data_and_create_figures()                             # Load data and create initial figures
start_date = df['date'].min()                                   # Get the minimum date from the data
end_date = df['date'].max()                                     # Get the maximum date from the data
initial_figures = generate_figures(df, start_date, end_date, ['bmi','bmi_ma','fat','fat_ma'], ['weight','weight_ma'])    # Generate initial figures based on the data

# Define the layout of the Dash app, HTML elements and components
app.layout = html.Div(style={'backgroundColor': '#1f1f1f', 'padding': '10px', 'height': '100vh'}, children=[
    html.H1("Personal Data Dashboard", style={'textAlign': 'center', 'color': 'white'}),    # Header

    dcc.DatePickerRange(
        id='date-picker-range',                                     # Date picker range component
        start_date=df['date'].min().date(),                         # Set the start date to the minimum date in the data
        end_date=df['date'].max().date(),                           # Set the end date to the maximum date in the data
        display_format='YYYY-MM-DD',                                # Display format for the date
        style={'color': 'white', 'border': '1px solid #4CAF50'}     # Style for the date picker
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
    
    dcc.Graph(id='weight-graph', figure=initial_figures[0]),    # Weight graph
    
    dcc.Checklist(
    id='weight-line-toggle',
    options=[
        {'label': 'Show Weight', 'value': 'weight'},
        {'label': 'Show Weight (MA)', 'value': 'weight_ma'}
    ],
    value=['weight','weight_ma'],
    style={'color': 'white'}
    ),
    
    dcc.Graph(id='bmi-fat-graph', figure=initial_figures[1]),   # BMI and Body Fat Percentage graph
    
    dcc.Checklist(
    id='bmi-fat-line-toggle',
    options=[
        {'label': 'Show BMI', 'value': 'bmi'},
        {'label': 'Show BMI (MA)', 'value': 'bmi_ma'},
        {'label': 'Show Body Fat', 'value': 'fat'},
        {'label': 'Show Body Fat (MA)', 'value': 'fat_ma'}
    ],
    value=['bmi','bmi_ma','fat','fat_ma'],
    style={'color': 'white'}
    ),
    
    # TODO
    # Display a summary of the data below the graphs, such as the latest BMI, weight, and fat percentage, or the average over the selected date range.
    html.Div(id='data-summary', style={'color': 'white'}),
    
    dcc.Interval(id='interval', interval=3600*1000, n_intervals=0)
])

# Define callback to update graphs based on date range
@app.callback(
    [Output('weight-graph', 'figure'),          # Output for the Weight graph
     Output('bmi-fat-graph', 'figure')],        # Output for the BMI and Body Fat Percentage graph
    [Input('date-picker-range', 'start_date'),  # Input for the start date
     Input('date-picker-range', 'end_date'),    # Input for the end date
     Input('refresh-button', 'n_clicks'),       # Input for the refresh button
     Input('bmi-fat-line-toggle', 'value'),
     Input('weight-line-toggle', 'value'),
     Input('interval', 'n_intervals')]
)
def update_graphs(start_date, end_date, n_clicks,bmi_fat_selected_lines, weight_selected_lines,n_intervals):
    """
    Update the graphs based on the selected date range and line toggles.
    Parameters:
        - start_date (str): The start date for the data.
        - end_date (str): The end date for the data.
        - n_clicks (int): The number of clicks.
        - bmi_fat_selected_lines (list): The selected lines for BMI and fat.
        - weight_selected_lines (list): The selected lines for weight.
        - n_intervals (int): The number of intervals.
    Returns:
        - dict: A dictionary containing the generated figures based on the updated data.
    """
    ...
    if n_clicks > 0:    # Check if the refresh button has been clicked
        # Debugging information
        logging.debug("Current working directory: %s", os.getcwd())
        logging.debug("Checking if get_all_data.py exists: %s", os.path.exists('get_all_data.py'))
        logging.debug("Checking if clean_body_data.py exists: %s", os.path.exists('clean_body_data.py'))
        
        try:
            subprocess.run(['python', 'get_all_data.py'], check=True)  # Run data fetching script
            subprocess.run(['python', 'clean_body_data.py'], check=True)  # Run data cleaning script
        except subprocess.CalledProcessError as e:
            logging.error("An error occurred while running the subprocess: %s", e)
            return {}

    df = pd.read_csv('clean_body_data.csv')                     # Load the cleaned data
    df['date'] = pd.to_datetime(df['date'])                     # Convert 'date' column to datetime if not already done
    df['weight_ma'] = calculate_moving_average(df, 'weight')    # Calculate moving average for 'weight' column
    df['bmi_ma'] = calculate_moving_average(df, 'bmi')          # Calculate moving average for 'bmi' column
    df['fat_ma'] = calculate_moving_average(df, 'fat')          # Calculate moving average for 'fat' column
    
    return generate_figures(df, start_date, end_date, bmi_fat_selected_lines, weight_selected_lines)

if __name__ == '__main__':
    # Run in debug mode, live reloading enabled
    app.run_server(debug=True)  
