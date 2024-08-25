import subprocess
import re
import fitbit
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

def load_config(filename='client_config.json'):
    """
    Load client credentials from a configuration file.

    Args:
        filename (str): The name of the JSON configuration file to load. Defaults to 'client_config.json'.

    Returns:
        tuple: A tuple containing the client ID and client secret.

    """
    with open(filename, 'r') as file:                   # Open the configuration file in read mode
        config = json.load(file)                        # Parse the JSON data from the file
        
    return config['CLIENT_ID'], config['CLIENT_SECRET']  # Extract and return the client ID and client secret


def get_tokens_from_gather_keys(client_id, client_secret):
    """
    Run gather_keys_oauth2.py to obtain the access and refresh tokens.

    Args:
        client_id (str): The client ID for OAuth2 authentication.
        client_secret (str): The client secret for OAuth2 authentication.

    Returns:
        tuple: A tuple containing the access token and refresh token.
               Returns (None, None) if an error occurs.
    """
    # Run the OAuth2 script with client credentials
    result = subprocess.run(['python', 'gather_keys_oauth2.py', client_id, client_secret], capture_output=True, text=True)
    
    if result.returncode != 0:                                          # Check for errors during script execution
        print(f"Error running gather_keys_oauth2.py: {result.stderr}")  # Print error message if the script fails
        return None, None                                               # Return None if there was an error
    
    # Extract tokens from the script's output
    output = result.stdout
    access_token = None
    refresh_token = None
    
    access_token_match = re.search(r'access_token\s*=\s*(\S+)', output)     # Search for the access token in the output
    if access_token_match: access_token = access_token_match.group(1)       # Extract the access token
    
    refresh_token_match = re.search(r'refresh_token\s*=\s*(\S+)', output)   # Search for the refresh token in the output
    if refresh_token_match: refresh_token = refresh_token_match.group(1)    # Extract the refresh token
    
    return access_token, refresh_token                                      # Return the extracted tokens


def get_body_data(authd_client, start_date, end_date, period='30d'):
    """
    Fetch body weight data between start_date and end_date or for a specified period.

    Args:
        authd_client (object): An authenticated client instance with methods to fetch body data.
        start_date (datetime.date): The start date for fetching body weight data.
        end_date (datetime.date): The end date for fetching body weight data.
        period (str): The period for fetching data. It can be '1d', '7d', '30d', etc. Defaults to '30d'.

    Returns:
        list: A list of body weight entries fetched from the API.
    """
    all_bodyweight = []             # List to store all body weight entries
    current_date = start_date       # Initialize current_date to start_date

    # Loop through the date range, fetching data in chunks based on the period
    while current_date <= end_date:
        # Calculate the next date based on the specified period or end_date
        next_date = min(current_date + timedelta(days=int(period[:-1])), end_date)
        try:
            # Fetching data for the current period or date range
            body_data = authd_client.get_bodyweight(base_date=current_date.strftime('%Y-%m-%d'), end_date=next_date)
            if 'weight' in body_data:
                # Append each weight entry to the list
                for entry in body_data['weight']:
                    all_bodyweight.append(entry)
        except Exception as e:
            # Print an error message if fetching data fails
            print(f"Error fetching body data from {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}: {e}")

        current_date = next_date + timedelta(days=1)    # Move to the next date after the current period
        time.sleep(1)                                   # Pause to avoid hitting API rate limits

    return all_bodyweight                               # Return the list of body weight entries


def get_start_date_from_csv(filename='body_data.csv'):
    """
    Get the maximum date from an existing CSV file and set the start date to max_date + 1.

    Args:
        filename (str): The path to the CSV file. Defaults to 'body_data.csv'.

    Returns:
        datetime.date: The start date for fetching new data, which is the maximum date in the CSV plus one day.
                       If the file does not exist or is empty, a default start date is returned.
    """
    if os.path.exists(filename):                        # Check if the file exists
        df = pd.read_csv(filename)                      # Read the CSV file into a DataFrame
        if not df.empty:                                # Ensure the DataFrame is not empty
            df['date'] = pd.to_datetime(df['date'])     # Convert the 'date' column to datetime objects
            max_date = df['date'].max()                 # Find the maximum date in the DataFrame
            return max_date + timedelta(days=1)         # Return the next day after the maximum date

    return datetime(year=2023, month=7, day=1)          # Return a default start date if the file does not exist or is empty


def append_data_to_csv(df, filename='body_data.csv'):
    """
    Append data to an existing CSV file or create a new one if it doesn't exist, ensuring columns are in the correct order.

    Args:
        df (pd.DataFrame): The DataFrame containing data to append or write to the CSV file.
        filename (str): The path to the CSV file. Defaults to 'body_data.csv'.

    Returns:
        None
    """
    columns_order = ['bmi', 'date', 'logId', 'source', 'time', 'weight', 'fat'] # Define the correct column order
    df = df.reindex(columns=columns_order)                                      # Reorder columns in the DataFrame according to columns_order
    
    if os.path.exists(filename):                                    # If the file already exists
        df.to_csv(filename, mode='a', header=False, index=False)    # Append to the existing file without writing header
    
    else:                                                           # If new file 
        df.to_csv(filename, index=False)                            # Create a new file and write data with header


if __name__ == "__main__":
    CLIENT_ID, CLIENT_SECRET = load_config()                                                # Load client credentials from config file
    access_token, refresh_token = get_tokens_from_gather_keys(CLIENT_ID, CLIENT_SECRET)     # Get tokens from gather_keys_oauth2.py
    
    if not access_token or not refresh_token: 
        print("Failed to get access and refresh tokens.")
        exit(1)

    # Create a Fitbit client with the obtained tokens
    authd_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, access_token=access_token, refresh_token=refresh_token)
    
    start_date = get_start_date_from_csv()  # Get the start date based on existing data
    end_date = datetime.today()             # End date today

    all_bodyweight = get_body_data(authd_client, start_date, end_date, period='30d')    # Get all bodyweight data
    df = pd.DataFrame(all_bodyweight)                                                   # Convert to DataFrame
    append_data_to_csv(df, 'body_data.csv')                                             # Append data to the CSV
    
    print(f"Data appended to 'body_data.csv'")