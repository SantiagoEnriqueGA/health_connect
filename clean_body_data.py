import pandas as pd

def clean_body_data(input_filename='body_data.csv', output_filename='clean_body_data.csv'):
    
    df = pd.read_csv(input_filename)                        # Load the data

    pd.set_option('future.no_silent_downcasting', True)
    df = df.infer_objects()                                 # Infer object dtypes if necessary

    df = df.drop_duplicates(subset='date', keep='first')    # Drop duplicate dates, keeping the first occurrence

    df['date'] = pd.to_datetime(df['date'])                 # Ensure datetime
    df = df.sort_values(by='date')                          # Sort the DataFrame by date to ensure correct forward filling

    
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].apply(pd.to_numeric, errors='coerce')   # Convert columns to numeric, forcing errors to NaN\
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].replace(0, pd.NA)                       # Replace zeros with NaN
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].ffill()                                 # Forward fill missing values

    df.to_csv(output_filename, index=False)                 # Save the cleaned data to a new CSV file
    print(f"Cleaned DataFrame saved to {output_filename}:") # Display final state of the DataFrame

if __name__ == "__main__":
    clean_body_data()
