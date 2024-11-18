import pandas as pd
from fuzzywuzzy import fuzz
import re
from tqdm import tqdm


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

def rank_funding_agencies(excel_path, output_path, threshold=90):
    print(f"Reading the Excel file from {excel_path}")
    df1 = pd.read_excel(excel_path, sheet_name='AI')
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
    
    # Save the results to an CSV file
    result_df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
