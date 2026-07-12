WITH filtered_data AS (
  SELECT
    url,
    query,
    -- Calculate true average position across the date range
    (SUM(sum_position) / SUM(impressions)) AS avg_position,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks
  FROM
    `your-project.searchconsole.searchdata_url_impression`
  WHERE
    -- Look at the last 30 days for fresh performance signals
    data_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY
    url,
    query
),

categorized_tech_topics AS (
  SELECT
    *,
    -- Mapping queries to Consumer Electronics product categories
    CASE 
      -- 1. Smartphones
      WHEN REGEXP_CONTAINS(LOWER(query), 'phone|smartphone|iphone|galaxy|pixel|mobile') THEN 'Smartphones'
      
      -- 2. Laptops & Computers
      WHEN REGEXP_CONTAINS(LOWER(query), 'laptop|macbook|pc|desktop|chromebook|monitor') THEN 'Laptops & Computers'
      
      -- 3. Audio & Headphones
      WHEN REGEXP_CONTAINS(LOWER(query), 'headphones|earbuds|airpods|speaker|soundbar|audio') THEN 'Audio & Headphones'
      
      -- 4. Wearables
      WHEN REGEXP_CONTAINS(LOWER(query), 'watch|smartwatch|fitness tracker|garmin|apple watch') THEN 'Wearables & Smartwatches'
      
      -- 5. Support & Troubleshooting (High intent for existing customers)
      WHEN REGEXP_CONTAINS(LOWER(query), 'fix|repair|support|warranty|won''t turn on|battery replacement') THEN 'Support & Troubleshooting'
      
      ELSE 'General Brand / Accessories'
    END AS topic_cluster
  FROM
    filtered_data
)

SELECT
  topic_cluster,
  COUNT(DISTINCT url) AS distinct_urls_ranking,
  COUNT(DISTINCT query) AS distinct_queries_captured,
  SUM(total_impressions) AS cluster_impressions,
  
  -- The Total RRF Score (Heavily influenced by raw query volume)
  SUM(1.0 / (60.0 + avg_position)) AS total_rrf_score,
  
  -- THE FIX: Average RRF Score per Query (Normalizes for volume skew)
  ROUND(SUM(1.0 / (60.0 + avg_position)) / COUNT(DISTINCT query), 4) AS avg_rrf_per_query,
  
  -- Context metric
  ROUND(AVG(avg_position), 2) AS avg_cluster_position
FROM
  categorized_tech_topics
GROUP BY
  topic_cluster
ORDER BY
  avg_rrf_per_query DESC;
