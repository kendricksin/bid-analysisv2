from fuzzywuzzy import process

def fuzzy_search(query, companies_df, limit=5):
    if not query:
        return []
    
    # Ensure registered_no is treated as string and padded to 13 digits
    companies_df['registered_no'] = companies_df['registered_no'].astype(str).str.zfill(13)
    
    # Combine registered_no, company_name_thai, and company_name_english into a single string for searching
    choices = companies_df.apply(lambda row: f"({row['registered_no']}) {row['company_name_thai']} - {row['company_name_english']}", axis=1).tolist()
    results = process.extract(query, choices, limit=limit*2)  # Get more results initially
    
    # Filter results to only include those with 13-digit IDs
    valid_results = [result for result in results if len(result[0].split(')')[0].strip('(')) == 13]
    
    # Return unique results, limited to the original limit
    return list(dict.fromkeys(result[0] for result in valid_results))[:limit]