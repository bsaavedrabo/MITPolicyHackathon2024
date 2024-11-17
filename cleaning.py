import pandas as pd

def load_data(demographics_file, commitments_file):
    """
    Load the data from the provided CSV files.
    :param demographics_file: Path to the demographics data file
    :param commitments_file: Path to the current commitments data file
    :return: pandas DataFrames with the loaded data
    """
    # Load the files into DataFrames
    demographics_df = pd.read_csv(demographics_file, low_memory=False)
    commitments_df = pd.read_csv(commitments_file, low_memory=False)

    # Clean column names: strip spaces and convert to lowercase
    demographics_df.columns = demographics_df.columns.str.strip().str.lower()
    commitments_df.columns = commitments_df.columns.str.strip().str.lower()

    # Print column names for debugging (to ensure 'cdcno' exists in both)
    print("Demographics Columns:", demographics_df.columns)
    print("Commitments Columns:", commitments_df.columns)
    
    return demographics_df, commitments_df

def merge_data(demographics_df, commitments_df):
    """
    Perform a left join of commitments with demographics data based on 'cdcno'.
    :param demographics_df: DataFrame of demographics data
    :param commitments_df: DataFrame of current commitments data
    :return: Merged DataFrame (left join)
    """
    # Check if 'cdcno' is in both DataFrames
    if 'cdcno' not in demographics_df.columns:
        print("Error: 'cdcno' column missing in demographics data")
        return None
    if 'cdcno' not in commitments_df.columns:
        print("Error: 'cdcno' column missing in commitments data")
        return None

    # Merge the DataFrames on the 'cdcno' column using a left join (keep all commitments)
    merged_df = pd.merge(commitments_df, demographics_df, on='cdcno', how='left')

    print(f"Merged DataFrame has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns")
    
    return merged_df

def merge_with_prior_summary(merged_df, prior_summary_df):
    """
    Merge the data with the prior commitments summary using a left join based on 'cdcno'.
    :param merged_df: DataFrame of merged demographics and commitments data
    :param prior_summary_df: Prior commitments summary data
    :return: Merged DataFrame (left join)
    """
    # Check if 'cdcno' is in both DataFrames
    if 'cdcno' not in merged_df.columns:
        print("Error: 'cdcno' column missing in merged data")
        return None
    if 'cdcno' not in prior_summary_df.columns:
        print("Error: 'cdcno' column missing in prior summary data")
        return None

    # Merge the DataFrames on the 'cdcno' column using a left join (keep all merged data)
    final_df = pd.merge(merged_df, prior_summary_df, on='cdcno', how='left')

    print(f"Final DataFrame has {final_df.shape[0]} rows and {final_df.shape[1]} columns")
    
    return final_df

def clean_data(merged_df):
    """
    Clean the merged data: handle missing values, convert dates, etc.
    :param merged_df: Merged DataFrame
    :return: Cleaned DataFrame
    """
    # Convert categorical columns to object before filling missing values
    for col in merged_df.select_dtypes(include=['category']).columns:
        merged_df[col] = merged_df[col].astype('object')
    
    # Fill missing values with 'Unknown'
    merged_df.fillna('Unknown', inplace=True)

    # Convert date columns to datetime format (if applicable)
    date_columns = ['offense_begin_date', 'offense_end_date']
    for date_col in date_columns:
        if date_col in merged_df.columns:
            merged_df[date_col] = pd.to_datetime(merged_df[date_col], errors='coerce')

    # Ensure that sentence columns are integers (and handle any non-integer values)
    if 'aggregate_sentence_in_months' in merged_df.columns:
        merged_df['aggregate_sentence_in_months'] = pd.to_numeric(merged_df['aggregate_sentence_in_months'], errors='coerce')
    else:
        print("Warning: 'aggregate_sentence_in_months' column is missing. Skipping conversion.")
    
    # Similarly for 'offense_time_with_enhancement'
    if 'offense_time_with_enhancement' in merged_df.columns:
        merged_df['offense_time_with_enhancement'] = pd.to_numeric(merged_df['offense_time_with_enhancement'], errors='coerce')
    else:
        print("Warning: 'offense_time_with_enhancement' column is missing. Skipping conversion.")
    
    return merged_df

def save_data(merged_df, output_file):
    """
    Save the cleaned DataFrame to a CSV file.
    :param merged_df: Cleaned DataFrame
    :param output_file: Path to the output file
    """
    if output_file.endswith('.csv'):
        merged_df.to_csv(output_file, index=False)
    else:
        merged_df.to_excel(output_file, index=False)

def main():
    # Specify the full paths to the input files
    demographics_file = '/home/danayala/MITPolicyHackathon2024/data/data/demographics.csv'  # Path to demographics file
    commitments_file = '/home/danayala/MITPolicyHackathon2024/data/data/current_commitments.csv'  # Path to current commitments file
    prior_summary_file = '/home/danayala/MITPolicyHackathon2024/data/data/prior_commitments.csv'  # Path to prior summary file
    
    # Specify the output file path for cleaned data
    output_file = '/home/danayala/MITPolicyHackathon2024/merged_data.csv'  # Path to save merged data

    # Step 1: Load the data
    demographics_df, commitments_df = load_data(demographics_file, commitments_file)
    
    # Load the prior summary file
    prior_summary_df = pd.read_csv(prior_summary_file, low_memory=False)
    prior_summary_df.columns = prior_summary_df.columns.str.strip().str.lower()

    # Step 2: Merge the data
    merged_df = merge_data(demographics_df, commitments_df)
    
    if merged_df is not None and merged_df.shape[0] > 0:
        # Step 3: Merge with prior commitments summary
        final_df = merge_with_prior_summary(merged_df, prior_summary_df)
        
        if final_df is not None:
            # Step 4: Clean the merged data
            cleaned_df = clean_data(final_df)
            
            # Step 5: Save the cleaned data to file
            save_data(cleaned_df, output_file)
            print(f"Cleaned data saved to {output_file}")
        else:
            print("No data to merge with prior summary.")
    else:
        print("No data to clean or merge.")

if __name__ == "__main__":
    main()
