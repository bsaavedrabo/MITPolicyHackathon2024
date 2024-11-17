import pandas as pd
import re
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_to_months(time_str):
    """
    Convert a time string like '1 Year 4 Months' to total months.
    :param time_str: Time duration string in the format 'X Year(s) Y Month(s)'
    :return: Total months as an integer
    """
    if isinstance(time_str, str):
        years_match = re.search(r'(\d+)\s*Year', time_str)
        months_match = re.search(r'(\d+)\s*Month', time_str)

        years = int(years_match.group(1)) if years_match else 0
        months = int(months_match.group(1)) if months_match else 0

        total_months = years * 12 + months
        return total_months
    return 0  # If time_str is not a string or doesn't match, return 0


def load_and_clean_data(file_path):
    """
    Load and clean the current commitments data.
    :param file_path: Path to the data file
    :return: Cleaned pandas DataFrame
    """
    ext = os.path.splitext(file_path)[1]
    if ext == '.csv':
        df = pd.read_csv(file_path, low_memory=False)
    elif ext == '.xlsx':
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    df.columns = (
        df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
    )

    logging.info(f"Loaded data with columns: {df.columns.tolist()}")

    # Convert dates to datetime
    df['offense_begin_date'] = pd.to_datetime(df['offense_begin_date'], errors='coerce')
    df['offense_end_date'] = pd.to_datetime(df['offense_end_date'], errors='coerce')

    # Convert 'offense_time_with_enhancement' to total months
    df['offense_time_with_enhancement_months'] = df['offense_time_with_enhancement'].apply(convert_to_months)

    # Add column for years
    df['offense_time_with_enhancement_years'] = df['offense_time_with_enhancement_months'] / 12

    # Drop duplicates
    df = df.drop_duplicates()

    # Reset index
    df.reset_index(drop=True, inplace=True)

    logging.info("Data cleaning completed.")
    return df


def summarize_data(df):
    """
    Generate summary statistics for the dataset.
    :param df: pandas DataFrame
    :return: None
    """
    summary = {
        'Total Records': len(df),
        'Unique Individuals (cdcno)': df['cdcno'].nunique(),
        'Average Sentence Duration (Years)': df['offense_time_with_enhancement_years'].mean(),
        'Longest Sentence Duration (Years)': df['offense_time_with_enhancement_years'].max(),
        'Shortest Sentence Duration (Years)': df['offense_time_with_enhancement_years'].min(),
        'Most Frequent Offense': df['offense_description'].mode()[0],
        'Offense Categories Count': df['offense_category'].value_counts().to_dict()
    }

    logging.info("\nSummary Statistics:")
    for key, value in summary.items():
        logging.info(f"{key}: {value}")


def visualize_data(df, save_dir="plots"):
    """
    Create visualizations and save them as images in the GitHub repository.
    :param df: pandas DataFrame
    :param save_dir: Directory to save plots
    """
    os.makedirs(save_dir, exist_ok=True)

    # Distribution of Sentence Durations in Years
    plt.figure(figsize=(10, 6))
    sns.histplot(df['offense_time_with_enhancement_years'], bins=20, kde=True)
    plt.title('Distribution of Sentence Durations (Years)')
    plt.xlabel('Sentence Duration (Years)')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(save_dir, "sentence_durations_distribution_years.png"))
    plt.close()

    # Offense Categories Count
    plt.figure(figsize=(12, 8))
    df['offense_category'].value_counts().plot(kind='bar', color='skyblue')
    plt.title('Frequency of Offense Categories')
    plt.xlabel('Offense Category')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(save_dir, "offense_categories_count.png"))
    plt.close()

    # Sentence Durations by Offense Category in Years
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='offense_category', y='offense_time_with_enhancement_years', data=df)
    plt.title('Sentence Durations by Offense Category (Years)')
    plt.xlabel('Offense Category')
    plt.ylabel('Sentence Duration (Years)')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(save_dir, "sentence_durations_by_category_years.png"))
    plt.close()

    logging.info(f"Plots saved in directory: {save_dir}")


def save_cleaned_data(df, output_file):
    """
    Save the cleaned data to a CSV file.
    :param df: Cleaned pandas DataFrame
    :param output_file: Path to save the CSV
    """
    df.to_csv(output_file, index=False)
    logging.info(f"Cleaned data saved to {output_file}")


def main():
    # Paths for input and output files
    input_file = 'data/data/current_commitments.csv'  # Replace with the actual file path
    output_file = 'data/data/current_commitments_cleaned.csv'  # Path to save the cleaned data

    try:
        # Load and clean the data
        cleaned_df = load_and_clean_data(input_file)

        # Summarize the data
        summarize_data(cleaned_df)

        # Visualize the data
        visualize_data(cleaned_df, save_dir="plots")  # Save plots in the "plots" directory

        # Save the cleaned data
        save_cleaned_data(cleaned_df, output_file)

        logging.info("Script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
