-- Q1: Top Inventors (Who has the most patents?)
SELECT i.name, COUNT(DISTINCT r.patent_id) AS total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q2: Top Companies (Which companies own the most patents?)
SELECT c.name, COUNT(DISTINCT r.patent_id) AS total_patents
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
WHERE c.name IS NOT NULL
GROUP BY c.company_id, c.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q3: Countries (Which countries produce the most patents?)
SELECT i.country, COUNT(DISTINCT r.patent_id) AS total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country IS NOT NULL
GROUP BY i.country
ORDER BY total_patents DESC
LIMIT 10;

-- Q4: Trends Over Time (How many patents are created each year?)
SELECT year, COUNT(patent_id) AS total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year DESC;

-- Q5: JOIN Query (Combine patents with inventors and companies)
SELECT p.patent_id, p.title, i.name AS inventor_name, c.name AS company_name
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
LIMIT 20;

-- Q6: CTE Query (WITH statement: Break a complex query into steps)
-- Example: Find top companies, then find the average number of patents of those top companies.
WITH CompanyPatentCounts AS (
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL
    GROUP BY c.company_id, c.name
)
SELECT name, patent_count
FROM CompanyPatentCounts
WHERE patent_count > 1
ORDER BY patent_count DESC
LIMIT 10;

-- Q7: Ranking Query (Rank inventors using window functions)
SELECT 
    name, 
    total_patents,
    RANK() OVER(ORDER BY total_patents DESC) AS inventor_rank
FROM (
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
)
LIMIT 10;
