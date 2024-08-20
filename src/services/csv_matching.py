import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

def fuzzy_match_csv(scb_file, wos_file, output_file, threshold=90, chunk_size=10000):
    """
    Perform fuzzy matching between two CSV files and save the results.
    
    Args:
    scb_file (str): Path to the SCB CSV file
    wos_file (str): Path to the WOS CSV file
    output_file (str): Path to save the output CSV file
    threshold (int): Similarity threshold for matching (0-100)
    chunk_size (int): Number of rows to process at a time
    """
    
    print("Reading SCB file...")
    # Read the SCB file entirely (assuming it's smaller)
    scb_df = pd.read_csv(scb_file)
    print(f"SCB file read with {len(scb_df)} rows.")
    
    # Initialize an empty list to store matches
    matches = []
    
    print("Processing WOS file in chunks...")
    # Process the WOS file in chunks
    for chunk in tqdm(pd.read_csv(wos_file, chunksize=chunk_size), desc="Processing chunks"):
        print(f"Processing chunk with {len(chunk)} rows...")
        
        # Perform cartesian product between chunk and scb_df
        cross = pd.MultiIndex.from_product([chunk.index, scb_df.index])
        
        print("Calculating similarity scores...")
        # Calculate similarity scores
        similarities = [
            fuzz.partial_ratio(str(chunk.loc[i, 'item_title']), str(scb_df.loc[j, 'item_title'])) 
            for i, j in cross
        ]
        
        # Create a DataFrame with the cartesian product and similarities
        cross_df = pd.DataFrame(index=cross, data={'similarity': similarities})
        
        # Filter matches above the threshold
        matches_chunk = cross_df[cross_df['similarity'] >= threshold]
        print(f"Found {len(matches_chunk)} matches above the threshold.")
        
        # Add to matches list
        matches.extend([
            (
                chunk.loc[i, 'id'],  # WOS ID
                chunk.loc[i, 'item_title'],  # WOS item title
                scb_df.loc[j, 'item_title'],  # SCB item title
                sim
            ) 
            for (i, j), sim in matches_chunk['similarity'].items()
        ])
    
    print("Creating result DataFrame from matches...")
    # Create a DataFrame from the matches
    result_df = pd.DataFrame(matches, columns=['wos_id', 'wos_item_title', 'scb_item_title', 'similarity'])
    
    print("Sorting results by similarity...")
    # Sort by similarity in descending order
    result_df = result_df.sort_values('similarity', ascending=False)
    
    print(f"Saving results to {output_file}...")
    # Save the results to CSV
    result_df.to_csv(output_file, index=False)
    print(f"Matching results saved to {output_file}")


# Usage example
if __name__ == "__main__":
    scb_file = r"c:\Users\Anwender\Desktop\scb_b_202401_funded_venue_items_18_24_202408191802.csv"
    wos_file = r"c:\Users\Anwender\Desktop\wos_202401_funded_items_18_24_202408191803.csv"
    output_file = r"c:\Users\Anwender\Desktop\matched_items.csv"
    fuzzy_match_csv(scb_file, wos_file, output_file, threshold=96)
