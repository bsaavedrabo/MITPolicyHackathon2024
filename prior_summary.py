import pandas as pd
import os
import pathlib

current_dir = pathlib.Path(os.getcwd())

def load_prior_commitments(file_path):
    """
    Load the prior commitments data from a CSV or Excel file.
    :param file_path: Path to the prior commitments data file
    :return: pandas DataFrame with the loaded data
    """
    # Load the file into a DataFrame
    df = pd.read_csv(file_path, low_memory=False)

    # Clean column names: strip spaces and convert to lowercase
    df.columns = df.columns.str.strip().str.lower()

    # Print column names for debugging
    print("Columns in loaded file:", df.columns)

    # Check if the necessary columns exist before proceeding
    required_columns = ['cdcno', 'offense_begin_date', 'offense_end_date', 'release_date', 'offense_time_with_enhancement']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        return None

    # Convert relevant columns to appropriate types
    df['offense_begin_date'] = pd.to_datetime(df['offense_begin_date'], errors='coerce')
    df['offense_end_date'] = pd.to_datetime(df['offense_end_date'], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # Ensure 'offense_time_with_enhancement' is numeric (convert from text if necessary)
    df['offense_time_with_enhancement'] = pd.to_numeric(df['offense_time_with_enhancement'], errors='coerce')

    return df


def summarize_prior_commitments(prior_commitments_df):
    """
    Generate a summary of prior commitments by individual.
    :param prior_commitments_df: DataFrame with prior commitments data
    :return: Summary DataFrame
    """
    # Group by 'cdcno' to summarize data
    summary = prior_commitments_df.groupby('cdcno').agg(
        total_commitments=('case_number', 'nunique'),  # Count unique cases per individual
        total_time_served_months=('offense_time_with_enhancement', 'sum'),  # Sum of time served in months
        total_offenses=('offense', 'nunique'),  # Count of different offenses
        first_commitment_date=('offense_begin_date', 'min'),  # First offense date
        last_commitment_date=('offense_end_date', 'max'),  # Last offense date
        total_release_dates=('release_date', 'nunique')  # Number of distinct release dates
    ).reset_index()

    return summary


def save_summary_to_csv(summary_df, output_file):
    """
    Save the summarized data to a CSV file.
    :param summary_df: DataFrame with summarized prior commitments data
    :param output_file: Path to save the summary file
    """
    summary_df.to_csv(output_file, index=False)
    print(f"Summary data saved to {output_file}")


def main():
    # Specify the file paths
    prior_commitments_file = current_dir/ 'data/data/prior_commitments.csv'  # Correct file path
    output_file = current_dir/'data/data/prior_summary.csv'  # Output file path

    # Load the prior commitments data
    prior_commitments_df = load_prior_commitments(prior_commitments_file)
    
    if prior_commitments_df is None:
        print("Error: Could not load or process the prior commitments data.")
        return

    # Summarize the prior commitments by individual
    summary_df = summarize_prior_commitments(prior_commitments_df)

    # Save the summarized data to CSV
    save_summary_to_csv(summary_df, output_file)


if __name__ == '__main__':
    main()

    
