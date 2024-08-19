import pandas as pd
from fuzzywuzzy import fuzz
import re
from tqdm import tqdm
import multiprocessing as mp
from functools import partial

def find_funding_agencies(excel_path, output_path, threshold=90):
    print(f"Reading the Excel file from {excel_path}")
    df1 = pd.read_excel(excel_path, sheet_name='funding_agencies_automatic_extr')
    print(f"Funding agencies sheet read successfully. Number of rows: {len(df1)}")
    
    df2 = pd.read_excel(excel_path, sheet_name='companies')
    print(f"Companies sheet read successfully. Number of rows: {len(df2)}")
    
    companies = df2['companies'].tolist()
    print(f"Extracted {len(companies)} companies from the companies sheet")
    
    def find_matches(name):
        for company in companies:
            # Use partial ratio for better matching of substrings
            if fuzz.partial_ratio(company.lower(), name.lower()) >= threshold:
                # Check if the company name is a standalone word or surrounded by word boundaries
                if re.search(r'\b' + re.escape(company) + r'\b', name, re.IGNORECASE):
                    return [name]
        return []
    
    print("Applying fuzzy matching...")
    df1['matched_companies'] = df1['funding_agency'].apply(find_matches)
    print("Fuzzy matching completed.")
    
    print("Exploding the matched_companies column to create separate rows for each match")
    df_exploded = df1.explode('matched_companies')
    
    # Check if 'occurrences' column exists
    columns_to_include = ['matched_companies']
    if 'occurrences' in df_exploded.columns:
        columns_to_include.append('occurrences')
        print("Including 'occurrences' column in the output")
    else:
        print("Warning: 'occurrences' column not found in the input file")
    
    df_output = df_exploded[columns_to_include].rename(columns={'matched_companies': 'matched_company'})
    df_output = df_output[df_output['matched_company'].notna()]  # Remove rows where no match was found
    
    print(f"Saving the results to {output_path}")
    df_output.to_excel(output_path, index=False)
    print("Results saved successfully.")

def clean_string(s):
    return re.sub(r'[^\w\s]', '', s.lower())

def rank_funding_agencies(excel_path, output_path, threshold=85):
    print(f"Reading the Excel file from {excel_path}")
    df1 = pd.read_excel(excel_path, sheet_name='SIGIR')
    print(f"Funding agencies sheet read successfully. Number of rows: {len(df1)}")
    
    df2 = pd.read_excel(excel_path, sheet_name='unique funding agencies')
    print(f"Companies sheet read successfully. Number of rows: {len(df2)}")
    
    unique_funding_agencies = df2['funding agencies'].tolist()
    print(f"Extracted {len(unique_funding_agencies)} companies from the companies sheet")

    results = {}
    
    for agency in unique_funding_agencies:
        clean_agency = clean_string(agency)
        total_occurrences = 0
        
        for _, row in df1.iterrows():
            industry_agency = clean_string(row['industry_agency'])
            similarity = fuzz.partial_ratio(clean_agency, industry_agency)
            
            if similarity >= threshold:
                total_occurrences += row['occurrence_count']
        
        if total_occurrences > 0:
            results[agency] = total_occurrences
    
    # Create a DataFrame from the results and sort it by occurrence count in descending order
    result_df = pd.DataFrame(list(results.items()), columns=['Funding Agency', 'Total Occurrences'])
    result_df = result_df.sort_values('Total Occurrences', ascending=False)
    
    # Save the results to an Excel file
    result_df.to_excel(output_path, index=False)
    print(f"Results saved to {output_path}")

def calculate_similarities(chunk_scb_pair):
    """Calculate similarities for a chunk of WOS data and all SCB data"""
    chunk, scb_df = chunk_scb_pair
    matches = []
    for _, wos_row in chunk.iterrows():
        for _, scb_row in scb_df.iterrows():
            similarity = fuzz.ratio(wos_row['item_title'], scb_row['item_title'])
            if similarity >= SIMILARITY_THRESHOLD:
                matches.append((
                    wos_row['id'],
                    wos_row['item_title'],
                    scb_row['item_title'],
                    similarity
                ))
    return matches

def fuzzy_match_csv(scb_file, wos_file, output_file, threshold=80, chunk_size=10000):
    """
    Perform fuzzy matching between two CSV files using multi-core processing and save the results.
    
    Args:
    scb_file (str): Path to the SCB CSV file
    wos_file (str): Path to the WOS CSV file
    output_file (str): Path to save the output CSV file
    threshold (int): Similarity threshold for matching (0-100)
    chunk_size (int): Number of rows to process at a time
    """
    global SIMILARITY_THRESHOLD
    SIMILARITY_THRESHOLD = threshold
    
    # Read the SCB file entirely
    scb_df = pd.read_csv(scb_file)
    
    # Initialize the multiprocessing pool
    num_cores = mp.cpu_count()
    pool = mp.Pool(num_cores)
    
    # Prepare the data for parallel processing
    chunks = pd.read_csv(wos_file, chunksize=chunk_size)
    chunk_scb_pairs = [(chunk, scb_df) for chunk in chunks]
    
    # Process chunks in parallel
    matches = []
    for chunk_matches in tqdm(pool.imap(calculate_similarities, chunk_scb_pairs), 
                              desc=f"Processing chunks using {num_cores} cores"):
        matches.extend(chunk_matches)
    
    # Close the pool
    pool.close()
    pool.join()
    
    # Create a DataFrame from the matches
    result_df = pd.DataFrame(matches, columns=['wos_id', 'wos_item_title', 'scb_item_title', 'similarity'])
    
    # Sort by similarity in descending order
    result_df = result_df.sort_values('similarity', ascending=False)
    
    # Save the results to CSV
    result_df.to_csv(output_file, index=False)
    print(f"Matching results saved to {output_file}")



# Usage example
if __name__ == "__main__":
    scb_file = "/Users/max/Desktop/scb_b_202401_funded_venue_items_18_24_202408191802.csv"
    wos_file = "/Users/max/Desktop/wos_202401_funded_items_18_24_202408191803.csv"
    output_file = "/Users/max/Desktop/matched_items.csv"
    
    fuzzy_match_csv(scb_file, wos_file, output_file, threshold=96)