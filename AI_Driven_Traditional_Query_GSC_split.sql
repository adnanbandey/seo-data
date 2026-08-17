SELECT 
    query AS `Query`,
    FORMAT_DATE('%Y-%m', data_date) AS year_month,
    CASE 
            -- Categorize queries into AI-Driven or Traditional
            WHEN REGEXP_CONTAINS(query, r'(?i)^((please|write|draft|generate|summarize|rewrite|translate|explain|compare|act as|you are a|(give|show|tell|plan) (a|me)|list|organize|pretend you are|make it (shorter|funnier)|suggest|estimate|optimize|find|can you) .*|give me .* more|(hi|hello|hey|hiya)( (there))?|good (morning|afternoon|evening)|how are you|yo|(thanks|thank you)( (so much|a lot|very much))?|thx|cheers|(awesome|great|cool) thanks|ty|thankyou|sorry|fuck (you|off)|i hate you|you suck|shut up|yes|yep|yeah|yea|sure|ok|okay|correct|fine|sounds good|perfect|great|yes both|yes i do|yes that would be great|yes go on|yes,? pricing|(yes|yeah|sure|ok|okay) (please|thanks|thank you|pls|thx|plz)|(please|thanks|thank you) (yes|yeah|sure|ok|okay)|(no|nope|nah)( (thanks|thank you|thx))?|cancel|stop|wrong|incorrect|anywhere|all|any|yes please recommend|please recommend|bye|goodbye|bye bye|see ya|end|quit|done|help|options|what can you do|start over|restart|more|next|continue|go on|show on map|show me|any other options|others|please do|show map|try again|again|shorter|longer|fix it|is that all|(where|when|anything) else|(are there|any|show|show me) (more|others)|more (recommendations|ideas|options|results|places|hotels|restaurants|things to do|attractions)|(show|tell|add) (me )?(more|others|next))$') 
            THEN 'AI-Driven' 
            ELSE 'Traditional' 
        END AS query_type,
    SUM(clicks) AS Clicks,
    SUM(impressions) AS Impressions,
    ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) AS CTR,
    
FROM 
    `project_name.searchconsole.searchdata_url_impression`
WHERE 
    data_date >= '2024-12-01' 
    AND data_date <= '2026-07-31' 
    AND is_anonymized_query = FALSE
GROUP BY 
    1,2
ORDER BY 
    Impressions DESC;

select *  FROM 
    `project_name.searchconsole.searchdata_url_impression`
    WHERE 
    data_date >= '2025-12-01' 
    AND data_date <= '2026-01-31' limit 10;
