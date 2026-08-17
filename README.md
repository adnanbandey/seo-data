# 📈 SEO & Marketing Data Playbook

A growing collection of Python and SQL scripts designed to solve real-world SEO and marketing problems. 

📂 Repository Contents
AI & Search Query Analysis
These files focus on isolating and analyzing queries driven by Artificial Intelligence features (like AI Overviews or generative search) versus standard search queries.

AI Mode queries.ipynb: A Jupyter Notebook used for interactive data exploration, visualization, and analysis of AI-specific search queries.

AI_Driven_GSC_Queries.sql: An SQL script designed to extract and process GSC data specifically related to AI-driven search behaviors.

AI_Driven_Traditional_Query_GSC_split.sql: An SQL script that segments your GSC query dataset, splitting the traffic and impression data between traditional search queries and AI-driven queries for comparative analysis.

SERP Clustering
These files handle the grouping of similar keywords based on search engine results, allowing for topic clustering and semantic analysis.

SERP Clustering.py: A Python script that executes the core logic for SERP clustering. It likely uses NLP (Natural Language Processing) and vector embeddings to group semantically related queries together based on their search results.

GSC SERP Clustering.sql: An SQL script that either prepares the raw GSC data for the Python clustering script or processes the clustered output back into a relational database format.

Intent Classification & Ranking
These files are geared toward understanding why users are searching and how different ranking signals combine.

post1_gsc-query-data.sql: An SQL script that pulls the foundational GSC query data required for intent classification (likely the data extraction step for a specific project or "post 1").

post1_gsc-intent-classifier: A script or module (likely Python) that takes the GSC queries and classifies their search intent (e.g., informational, transactional, navigational).

rrf_analysis.sql: An SQL script for Reciprocal Rank Fusion (RRF) analysis. This is used to evaluate and combine multiple ranking scores or methodologies into a single, unified ranking metric.
