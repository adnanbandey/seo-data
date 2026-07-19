--GET GSC SEEDs DATA
SELECT 
    query, 
    SUM(impressions) AS total_impressions, 
    SUM(clicks) AS total_clicks,
    ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) AS blended_ctr_percent
FROM 
    `project_name.searchconsole.searchdata_url_impression`
WHERE 
    data_date >= '2025-06-01' 
    AND data_date <= '2026-06-01' 
    AND is_anonymized_query = FALSE
    -- 1. Eliminate short broad single words that don't cluster well
    AND ARRAY_LENGTH(SPLIT(TRIM(query), ' ')) >= 3
GROUP BY 
    query
HAVING 
    -- Moved to HAVING because we want to filter queries whose TOTAL impressions are > 100
    total_impressions > 100 
ORDER BY 
    total_clicks DESC, 
    total_impressions DESC;

--GET DOMAIN URLS
SELECT 
    query, 
    -- Concatenates all unique URLs into a comma-separated list in a single row
    STRING_AGG(DISTINCT url, ', ') AS all_pages,
    -- Count how many unique pages this query triggered
    COUNT(DISTINCT url) AS unique_page_count,
    SUM(impressions) AS total_impressions, 
    SUM(clicks) AS total_clicks,
    ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) AS blended_ctr_percent
FROM 
    `project_name.searchconsole.searchdata_url_impression`
WHERE 
    data_date >= '2025-06-01' 
    AND data_date <= '2026-06-01' 
    AND is_anonymized_query = FALSE
    -- 1. Eliminate short broad single words that don't cluster well
    AND ARRAY_LENGTH(SPLIT(TRIM(query), ' ')) >= 3
GROUP BY 
    query
HAVING 
    -- Moved to HAVING because we want to filter queries whose TOTAL impressions are > 100
    total_impressions > 100 
ORDER BY 
    total_clicks DESC, 
    total_impressions DESC;
