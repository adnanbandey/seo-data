SELECT 
    query, 
    SUM(impressions) AS IMP, 
    SUM(clicks) AS CLICKS,
    ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) AS CTR_PERCENT
FROM `your-project.searchconsole.searchdata_url_impression`
WHERE data_date BETWEEN '2024-01-01' AND '2026-06-28' 
    AND is_anonymized_query = FALSE 
    AND ARRAY_LENGTH(SPLIT(TRIM(query), ' ')) >= 10
GROUP BY 1 HAVING IMP > 10 ORDER BY IMP DESC
