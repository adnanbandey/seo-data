# 📈 SEO & Marketing Data Playbook

A growing collection of Python and SQL scripts designed to solve real-world SEO and marketing problems. 

## 📂 Repository Contents

### AI & Search Query Analysis
These files focus on isolating and analyzing queries driven by Artificial Intelligence features (like AI Overviews or generative search) versus standard search queries.

| File Name | Type | Description |
| :--- | :---: | :--- |
| `AI Mode queries.ipynb` | Notebook | Interactive data exploration and visualization of AI-specific search queries. |
| `AI_Driven_GSC_Queries.sql` | SQL | Extracts and processes GSC data related to AI-driven search behaviors. |
| `AI_Driven_Traditional_Query_GSC_split.sql` | SQL | Segments GSC query dataset to compare traditional vs. AI-driven traffic and impressions. |

### SERP Clustering
These files handle the grouping of similar keywords based on search engine results, allowing for topic clustering and semantic analysis.

| File Name | Type | Description |
| :--- | :---: | :--- |
| `SERP Clustering.py` | Python | Executes core logic for SERP clustering, grouping semantically related queries together based on search results. |
| `GSC SERP Clustering.sql` | SQL | Prepares raw GSC data for the Python clustering script or processes the clustered output into a relational database. |

### Intent Classification & Ranking
These files are geared toward understanding *why* users are searching and how different ranking signals combine.

| File Name | Type | Description |
| :--- | :---: | :--- |
| `post1_gsc-query-data.sql` | SQL | Pulls foundational GSC query data required for intent classification. |
| `post1_gsc-intent-classifier` | Script | Takes the GSC queries and classifies their search intent (e.g., informational, transactional). |
| `rrf_analysis.sql` | SQL | Performs Reciprocal Rank Fusion (RRF) analysis to combine multiple ranking scores into a unified metric. |

---
