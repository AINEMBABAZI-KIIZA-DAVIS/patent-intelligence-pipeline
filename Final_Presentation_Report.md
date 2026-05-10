# Patent Intelligence Data Pipeline: Final Presentation Report

## 1. Executive Summary
This project presents an **End-to-End Data Engineering Pipeline** designed to process, clean, and analyze real-world patent data from the **United States Patent and Trademark Office (USPTO)**. The goal of the project was to transform raw, fragmented bulk data into an organized relational database, extract meaningful innovation insights, and present the findings in an interactive web dashboard. 

## 2. Project Objectives
- **Data Engineering**: Build a robust Extract, Transform, Load (ETL) pipeline capable of handling massive datasets.
- **Relational Modeling**: Design a normalized SQLite database capturing the relationships between patents, inventors, and assignees (companies).
- **Analytical Reporting**: Use complex SQL queries to identify top innovators and macro trends.
- **Data Visualization**: Develop an intuitive, interactive dashboard using Streamlit to present findings to stakeholders.

## 3. Data Source
The data is sourced directly from the **PatentsView Data Portal** (USPTO bulk data). 
We processed subset samples (100,000 rows per table) from the following core files:
- `g_patent.tsv`: Core patent grants data (titles, dates).
- `g_patent_abstract.tsv`: Patent abstracts.
- `g_inventor_disambiguated.tsv`: Disambiguated inventor identities.
- `g_assignee_disambiguated.tsv`: Corporate assignees (companies).
- `g_location_disambiguated.tsv`: Geographical locations of inventors.

## 4. Pipeline Architecture (The ETL Process)

### Step 1: Extract (`main.py`)
- Python's `pandas` library is used to read large `.tsv` and `.zip` files.
- To handle memory constraints efficiently, the pipeline reads chunks into memory (`nrows=100000`).

### Step 2: Transform
- **Data Cleaning**: Handled missing values, renamed columns for consistency, and dropped duplicates.
- **Data Enrichment**: 
  - Joined Patents with their Abstracts.
  - Joined Inventors with Locations to append the Country origin.
  - Extracted the 'Filing Year' from the raw dates.
- Resulting cleaned datasets are staged as `clean_patents.csv`, `clean_inventors.csv`, and `clean_companies.csv`.

### Step 3: Load (`schema.sql` & `patents.db`)
Created a relational SQLite database (`patents.db`) featuring 4 interconnected tables:
1. `patents` (patent_id, title, abstract, filing_date, year)
2. `inventors` (inventor_id, name, country)
3. `companies` (company_id, name)
4. `relationships` (patent_id, inventor_id, company_id)

## 5. Data Analysis & Insights (`analysis_queries.sql`)
Complex SQL queries—incorporating `JOIN`s, `GROUP BY` aggregations, CTEs, and Window Functions—were executed to uncover key trends.

**Key Findings from Sample Data (100,000 Data rows processed):**
*   **Top Companies**: **Samsung Electronics** leads the pack with 2,067 patents, followed closely by **IBM** (1,803) and **Canon** (1,042).
*   **Top Inventors**: **Shunpei Yamazaki** is the leading individual inventor with 36 patents in this sample, followed by **Kia Silverbrook** (23) and **Tao Luo** (17).
*   **Global Leaders**: The **United States** holds the primary share (48.4%), followed by **Japan** (16.7%), **Germany** (5.8%), **South Korea** (5.2%), and **China** (4.2%).

## 6. Interactive Dashboard (`dashboard.py`)
To make the data accessible to non-technical stakeholders, a **Streamlit Web Application** was developed.
- **Technologies**: `Streamlit` (UI framework), `Altair` (Charts), `Pandas` (Data fetching).
- **Features**: 
    - Real-time querying to the SQLite database.
    - Premium UI with custom CSS formatting for executive-level presentation.
    - Interactive horizontal bar charts analyzing Companies and Countries.
    - Area charts tracking the historical trend of patent filings over time.

## 7. How to Run & Reproduce
1. Ensure the raw PatentsView data (`.tsv` or `.zip`) is in the project directory.
2. Run the main pipeline to generate the database and reports:
   ```bash
   python main.py
   ```
3. Launch the interactive dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## 8. Conclusion
This project successfully demonstrates a highly scalable data engineering workflow. By transitioning raw flat files into a structured relational format, we've enabled extremely fast analytical querying and provided a foundation that scales efficiently to process millions of patent records for global intelligence tracking.
