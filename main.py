import sqlite3
import pandas as pd
import os
import json

# Original data sources from PatentsView
PATENT_FILE = "g_patent.tsv"
INVENTOR_FILE = "g_inventor_disambiguated.tsv"
ASSIGNEE_FILE = "g_assignee_disambiguated.tsv"
LOCATION_FILE = "g_location_disambiguated.tsv"
ABSTRACT_FILE = "g_patent_abstract.tsv"

def check_files():
    files = [PATENT_FILE, INVENTOR_FILE, ASSIGNEE_FILE, LOCATION_FILE, ABSTRACT_FILE]
    missing = [f for f in files if not os.path.exists(f) and not os.path.exists(f+".zip")]
    if missing:
        print("\n[!] MISSING ORIGINAL DATA FILES:")
        for m in missing:
            print(f"    - {m} (or {m}.zip)")
        print("\nPlease download the original files from the PatentsView Data Portal:")
        print("Link: https://data.uspto.gov/bulkdata/datasets/pvgpatdis")
        print("Extract the TSV files and place them in this directory to continue.")
        return False
    return True

def run_etl_pipeline():
    print("Starting ETL Pipeline using ORIGINAL PatentsView Data...")
    
    if not check_files():
        return
        
    print("1. Extracting Data...")
    # Read files in chunks or specific lines to handle memory
    try:
        df_raw_patents = pd.read_csv(PATENT_FILE, sep="\t", on_bad_lines='skip', nrows=100000)
    except FileNotFoundError:
        df_raw_patents = pd.read_csv(PATENT_FILE+".zip", sep="\t", compression="zip", on_bad_lines='skip', nrows=100000)
        
    try:
        df_raw_abstracts = pd.read_csv(ABSTRACT_FILE, sep="\t", on_bad_lines='skip', nrows=100000)
    except FileNotFoundError:
        df_raw_abstracts = pd.read_csv(ABSTRACT_FILE+".zip", sep="\t", compression="zip", on_bad_lines='skip', nrows=100000)

    try:
        df_raw_inventors = pd.read_csv(INVENTOR_FILE, sep="\t", on_bad_lines='skip', nrows=100000)
    except FileNotFoundError:
        df_raw_inventors = pd.read_csv(INVENTOR_FILE+".zip", sep="\t", compression="zip", on_bad_lines='skip', nrows=100000)

    try:
        df_raw_assignees = pd.read_csv(ASSIGNEE_FILE, sep="\t", on_bad_lines='skip', nrows=100000)
    except FileNotFoundError:
        df_raw_assignees = pd.read_csv(ASSIGNEE_FILE+".zip", sep="\t", compression="zip", on_bad_lines='skip', nrows=100000)

    try:
        df_raw_locations = pd.read_csv(LOCATION_FILE, sep="\t", on_bad_lines='skip', nrows=100000)
    except FileNotFoundError:
        df_raw_locations = pd.read_csv(LOCATION_FILE+".zip", sep="\t", compression="zip", on_bad_lines='skip', nrows=100000)


    print("2. Transforming and Cleaning Data...")
    
    # 1. Patents Table Merge (combine g_patent with g_patent_abstract)
    df_patents_merge = pd.merge(df_raw_patents, df_raw_abstracts, on='patent_id', how='left')
    df_patents = df_patents_merge[['patent_id', 'patent_title', 'patent_abstract', 'patent_date']].copy()
    df_patents.columns = ['patent_id', 'title', 'abstract', 'filing_date']
    df_patents['year'] = pd.to_datetime(df_patents['filing_date'], errors='coerce').dt.year
    df_patents = df_patents.dropna(subset=['patent_id']).drop_duplicates(subset=['patent_id'])
    
    # 2. Inventors Table (merge with locations to get country)
    df_inv_loc = pd.merge(df_raw_inventors, df_raw_locations, on='location_id', how='left')
    df_inv_loc['name'] = df_inv_loc['disambig_inventor_name_first'].fillna('') + " " + df_inv_loc['disambig_inventor_name_last'].fillna('')
    df_inventors = df_inv_loc[['inventor_id', 'name', 'disambig_country']].copy()
    df_inventors.columns = ['inventor_id', 'name', 'country']
    df_inventors = df_inventors.dropna(subset=['inventor_id']).drop_duplicates(subset=['inventor_id'])
    
    # 3. Companies Table
    df_companies = df_raw_assignees[['assignee_id', 'disambig_assignee_organization']].copy()
    df_companies.columns = ['company_id', 'name']
    df_companies = df_companies.dropna(subset=['company_id', 'name']).drop_duplicates(subset=['company_id'])
    
    # 4. Relationships Table
    df_rel_inv = df_raw_inventors[['patent_id', 'inventor_id']].dropna()
    df_rel_assg = df_raw_assignees[['patent_id', 'assignee_id']].dropna()
    df_relationships = pd.merge(df_rel_inv, df_rel_assg, on='patent_id', how='outer')
    df_relationships.columns = ['patent_id', 'inventor_id', 'company_id']
    df_relationships = df_relationships.dropna(subset=['patent_id']).drop_duplicates()
    
    print("Saving cleaned data to CSV files...")
    df_patents.to_csv("clean_patents.csv", index=False)
    df_inventors.to_csv("clean_inventors.csv", index=False)
    df_companies.to_csv("clean_companies.csv", index=False)
    
    # 3. LOAD to SQLite
    print("3. Loading to SQLite Database...")
    conn = sqlite3.connect("patents.db")
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
        
    df_patents.to_sql('patents', conn, if_exists='replace', index=False)
    df_inventors.to_sql('inventors', conn, if_exists='replace', index=False)
    df_companies.to_sql('companies', conn, if_exists='replace', index=False)
    df_relationships.to_sql('relationships', conn, if_exists='replace', index=False)
    
    # 4. ANALYZE & REPORT
    print("4. Analyzing Data & Creating Reports...")
    
    q_top_inventors = """
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name ORDER BY total_patents DESC LIMIT 10;
    """
    df_top_inv = pd.read_sql_query(q_top_inventors, conn)
    df_top_inv.to_csv("top_inventors.csv", index=False)
    
    q_top_companies = """
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM companies c JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL
    GROUP BY c.company_id, c.name ORDER BY total_patents DESC LIMIT 10;
    """
    df_top_comp = pd.read_sql_query(q_top_companies, conn)
    df_top_comp.to_csv("top_companies.csv", index=False)
    
    q_countries = """
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL
    GROUP BY i.country ORDER BY total_patents DESC LIMIT 10;
    """
    df_top_countries = pd.read_sql_query(q_countries, conn)
    df_top_countries.to_csv("country_trends.csv", index=False)
    
    # JSON Report
    total_patents = len(df_patents)
    report_dict = {
        "total_patents": total_patents,
        "top_inventors": [{"name": row["name"], "patents": row["total_patents"]} for _, row in df_top_inv.iterrows()],
        "top_companies": [{"name": row["name"], "patents": row["total_patents"]} for _, row in df_top_comp.iterrows()],
        "top_countries": [{"country": row["country"], "share": round(row["total_patents"] / max(total_patents, 1), 3)} for _, row in df_top_countries.iterrows()]
    }
    with open("report.json", "w") as f:
        json.dump(report_dict, f, indent=2)
        
    print("\n================== PATENT REPORT ===================")
    print(f"Total Patents: {total_patents:,}")
    print("\nTop Inventors:")
    for idx, row in df_top_inv.head(2).iterrows(): print(f"{idx+1}. {row['name']} - {row['total_patents']}")
    print("\nTop Companies:")
    for idx, row in df_top_comp.head(1).iterrows(): print(f"{idx+1}. {row['name']} - {row['total_patents']}")
    print("\nTop Countries:")
    for idx, row in df_top_countries.head(2).iterrows(): print(f"{idx+1}. {row['country']} - {row['total_patents']}")
    print("====================================================\n")
    
    conn.close()
    print("Pipeline Execution Complete!")

if __name__ == "__main__":
    run_etl_pipeline()
