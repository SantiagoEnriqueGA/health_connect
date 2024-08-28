# Project Overview

This project is designed to gather, clean, and visualize data from Fitbit using Plotly Dash. It includes scripts for data fetching, cleaning, and generating interactive graphs.

## Main File Structure
`clean_body_data.py `  
`gather_keys_oauth2.py `  
`get_all_data.py`  
`plotly_dash.py`  

### File Descriptions

- **`get_all_data.py`**
    - Script to fetch all necessary data from the Fitbit API.
    - This script is called by `update_graphs` in `plotly_dash.py`.

- **`clean_body_data.py`**
    - Contains the function `clean_body_data` which cleans the raw body data and saves it to a CSV file.
    - Usage:
        ```sh
        python clean_body_data.py
        ```

- **`gather_keys_oauth2.py`**
    - Implements the `OAuth2Server` class for handling OAuth2 authentication with Fitbit.
    - Main functionalities include:
        - Initializing the OAuth2 server.
        - Authorizing via a web browser.
        - Fetching and displaying the user's profile and access token.
    - Usage:
        ```sh
        python gather_keys_oauth2.py <client_id> <client_secret>
        ```

- **`plotly_dash.py`**
    - Main script for generating and displaying interactive graphs using Plotly Dash.
    - Key functions:
        - `generate_figures`: Generates figures for BMI, Body Fat Percentage, and Weight over time.
        - `update_graphs`: Updates the graphs based on user input and date range.
    - Contains Dash components for user interaction and data visualization.
    - Can update data by running scripts: `get_all_data.py` and `clean_body_data.py`

## Configuration

Before running the scripts, you need to create a configuration file named `client_config.json` in the root directory of the project. This file should contain your Fitbit API client ID and client secret.

### Example `client_config.json`

```json
{
    "CLIENT_ID": "your_client_id_here",
    "CLIENT_SECRET": "your_client_secret_here"
}
```

## Usage

1. **Fetch Data:**  
Run the following script to fetch the data. This script will internally run `gather_keys_oauth2.py` as a subprocess to obtain the access and refresh tokens.
    ```sh
    python get_all_data.py
    ```

2. **Clean Data:**  
Run the following script to clean the fetched data.
    ```sh
    python clean_body_data.py
    ```

3. **Run the Dash Application:**  
Start the Dash application.
    ```sh
    python plotly_dash.py
    ```

From this point forward, you can simply run `plotly_dash.py` to start the dashboard. The dashboard includes a button to update/refresh data by running the necessary subprocesses.

## Dependencies
`pandas`  
`plotly`  
`dash`  
`cherrypy`  
`oauthlib`  
`fitbit`  

Ensure all dependencies are installed before running the scripts.