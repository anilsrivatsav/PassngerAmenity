import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

def preprocess_csv_data(df):
    """
    Preprocess the dataframe to handle missing values and data types.
    Logs any issues with specific columns for easier debugging.
    """
    try:
        for col in df.columns:
            # Handle missing or malformed object (string) fields
            if df[col].dtype == "object":
                original_null_count = df[col].isnull().sum()
                df[col] = df[col].fillna("").astype(str)
                logging.info(f"Processed column '{col}' as string. Filled {original_null_count} missing values.")
            
            # Handle missing or malformed numeric fields
            else:
                original_null_count = df[col].isnull().sum()
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                logging.info(f"Processed column '{col}' as numeric. Filled {original_null_count} missing values.")

        logging.info("Preprocessing completed successfully.")
        return df

    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        raise  # Re-raise the exception to ensure it's captured by higher-level error handling

# Example usage during CSV loading
try:
    # Load the CSV
    logging.info("Loading 'stations.csv'...")
    df = pd.read_csv("stations.csv")

    # Log the initial shape of the dataframe
    logging.info(f"Loaded dataframe with shape {df.shape}.")

    # Preprocess the CSV data
    df = preprocess_csv_data(df)

    # Display the first few rows for verification
    logging.info(f"First few rows after preprocessing:\n{df.head()}")

except FileNotFoundError:
    logging.error("The file 'stations.csv' was not found. Ensure it exists in the current directory.")
except pd.errors.EmptyDataError:
    logging.error("The file 'stations.csv' is empty. Provide a valid CSV file.")
except pd.errors.ParserError as e:
    logging.error(f"Error parsing the CSV file: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
