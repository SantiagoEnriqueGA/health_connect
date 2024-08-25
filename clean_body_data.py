import pandas as pd

def clean_body_data(input_filename='body_data.csv', output_filename='clean_body_data.csv'):
    # Load the data
    df = pd.read_csv(input_filename)

    pd.set_option('future.no_silent_downcasting', True)

    # Infer object dtypes if necessary
    df = df.infer_objects()

    # Drop duplicate dates, keeping the first occurrence
    df = df.drop_duplicates(subset='date', keep='first')

    # Sort the DataFrame by date to ensure correct forward filling
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    # Convert columns to numeric, forcing errors to NaN
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].apply(pd.to_numeric, errors='coerce')

    # Replace zeros with NaN
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].replace(0, pd.NA)

    # Forward fill missing values
    df[['bmi', 'fat', 'weight']] = df[['bmi', 'fat', 'weight']].ffill()

    # Save the cleaned data to a new CSV file
    df.to_csv(output_filename, index=False)

    # Display final state of the DataFrame
    print(f"Cleaned DataFrame saved to {output_filename}:")

if __name__ == "__main__":
    clean_body_data()
