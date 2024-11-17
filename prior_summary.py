import pandas as pd
import re
import os
import pathlib
import pandas as pd
import re
import os
import pathlib

def convert_to_months(time_str):
    """
    Convert a time string like '1 Year 4 Months' to the total number of months.
    :param time_str: Time duration string in the format 'X Year(s) Y Month(s)'
    :return: Total months as an integer
    """
    if isinstance(time_str, str):
        # Regular expression to capture the years and months
        years_match = re.search(r'(\d+)\s*Year', time_str)
        months_match = re.search(r'(\d+)\s*Month', time_str)
        
        # Extract years and months from the matched groups
        years = int(years_match.group(1)) if years_match else 0
        months = int(months_match.group(1)) if months_match else 0
        
        # Calculate total months: years * 12 + months
        total_months = years * 12 + months
        
        return total_months
    return 0  # If time_str is not a string or doesn't match, return 0

def load_prior_commitments(file_path):
    """
    Load the prior commitments data from a CSV file and clean the columns.
    :param file_path: Path to the prior commitments data file
    :return: pandas DataFrame with the loaded data
    """
    # Load the file into a DataFrame
    df = pd.read_csv(file_path, low_memory=False)

    # Clean column names: strip spaces, convert to lowercase, and replace spaces with underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Check if the necessary columns exist before proceeding
    required_columns = ['cdcno', 'offense_begin_date', 'offense_end_date', 'release_date', 'offense_time_with_enhancement', 'offense_description']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        return None

    # Convert relevant columns to datetime, explicitly ensuring the conversion works
    df['offense_begin_date'] = pd.to_datetime(df['offense_begin_date'], errors='coerce')
    df['offense_end_date'] = pd.to_datetime(df['offense_end_date'], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Ensure 'offense_time_with_enhancement' is numeric (convert from text if necessary)
    df['offense_time_with_enhancement_months'] = df['offense_time_with_enhancement'].apply(convert_to_months)

    # Calculate the difference in days
    df['diff_in_days'] = (df['offense_end_date'] - df['offense_begin_date']).dt.days

    # Calculate the difference in months using 365.25 days per year (dividing by 30.4375 to get months)
    df['diff_in_months'] = df['diff_in_days'] / 30.4375

    # Fix edge cases where difference is negative or zero due to invalid dates
    df['diff_in_months'] = df['diff_in_months'].apply(lambda x: max(0.0, x))

    return df


def summarize_prior_commitments(prior_commitments_df):
    """
    Generate a summary of prior commitments by individual.
    :param prior_commitments_df: DataFrame with prior commitments data
    :return: Summary DataFrame
    """
    # Group by 'cdcno' to summarize data
    summary = prior_commitments_df.groupby('cdcno').agg(
        total_commitments_prior=('case_number', 'size'),  # Count occurrences (i.e., number of commitments)
        offenses_description_list_prior=('offense_description', lambda x: list(x)),  # List of offense descriptions for each individual
        first_commitment_date_prior=('offense_begin_date', 'min'),  # First offense date
        last_commitment_date_prior=('offense_end_date', 'max'),  # Last offense date
        total_release_dates_prior=('release_date', 'nunique'),  # Number of distinct release dates
        total_commitment_duration_months_prior=('offense_time_with_enhancement_months', 'sum'),  # Sum of commitment durations in months
        avg_commitment_duration_months_prior=('offense_time_with_enhancement_months', 'mean')  # Average duration in months per commitment
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
    prior_commitments_file = 'data/data/prior_commitments.csv'  # Adjusted path for the input file
    output_file = 'data/data/prior_summary.csv'  # Output file path

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
