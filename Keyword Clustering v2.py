#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import requests
import base64
import json
import time

# --- 1. SET YOUR CREDENTIALS ---#
#you can find this in DATAFORSEO UI
API_LOGIN = "--"
API_PASSWORD = "--"

# --- 2. LOAD YOUR SEED KEYWORDS ---
# Ensure your CSV has a column named 'query'
df_seeds = pd.read_csv("gsc_seeds.csv")

# ONLY test with 10 keywords first to protect your free credit!
# keywords_to_scrape = df_seeds['query'].head(10).tolist()


# In[ ]:


# df_seeds


# In[ ]:


# --- 3. PREPARE THE API REQUEST ---
# Encode credentials in Base64 as required by DataForSEO


# In[ ]:


creds = base64.b64encode(f"{API_LOGIN}:{API_PASSWORD}".encode()).decode()
headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}


# In[ ]:


# Load your keywords
df_seeds = pd.read_csv("gsc_seeds.csv")
keywords = df_seeds['query'].tolist()

# Batching into groups of 100
batches = [keywords[i:i + 100] for i in range(0, len(keywords), 100)]
task_ids = []

print(f"Posting {len(keywords)} keywords in {len(batches)} batches...")

for batch in batches:
    payload = [{"keyword": kw, "location_code": 2036, "language_code": "en", "device": "desktop"} for kw in batch]
    response = requests.post("https://api.dataforseo.com/v3/serp/google/organic/task_post", headers=headers, data=json.dumps(payload))
    data = response.json()
    
    if data.get('status_code') == 20000:
        for task in data['tasks']:
            task_ids.append(task['id'])
    print(f"Posted batch of {len(batch)} tasks. Total IDs collected: {len(task_ids)}")

# Save these IDs so you don't lose them
pd.DataFrame(task_ids, columns=['task_id']).to_csv("task_ids.csv", index=False)


# In[ ]:


# task_ids


# In[ ]:





# In[ ]:


import time

# --- 2. LOAD IDs AND FETCH ---
# Load your saved IDs from the first step
task_ids = pd.read_csv("task_ids.csv")['task_id'].tolist()
scraped_data = []

print(f"Fetching results for {len(task_ids)} tasks...")

for tid in task_ids:
    # THE FIX: Added /regular/ before the task ID
    url = f"https://api.dataforseo.com/v3/serp/google/organic/task_get/regular/{tid}"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # SAFETY CHECK: Ensure 'tasks' exists and isn't empty/null
    if data and data.get('tasks') and len(data['tasks']) > 0:
        task = data['tasks'][0]
        
        # Check if the specific task is ready and successful (Code 20000)
        if task.get('status_code') == 20000:
            
            # Ensure there is actually a result array
            if task.get('result') and len(task['result']) > 0:
                result = task['result'][0]
                kw = result.get('keyword', 'unknown')
                
                # Loop through the results and grab the organic URLs
                for item in result.get('items', []):
                    if item.get('type') == 'organic':
                        scraped_data.append({'keyword': kw, 'url': item['url']})
            else:
                print(f"Task {tid} completed, but returned zero results.")
                
        else:
            print(f"Task {tid} not ready or failed. Message: {task.get('status_message')}")
            
    else:
        # If the API throws a broader error (like an invalid path)
        print(f"API Error for ID {tid}: {data.get('status_message')}")
        
    # A tiny pause is still good practice when looping through hundreds of requests
    time.sleep(0.1) 

# --- 3. SAVE THE OUTPUT ---
if scraped_data:
    df_final = pd.DataFrame(scraped_data)
    df_final.to_csv("serp_scraped_data.csv", index=False)
    print(f"\nSuccess! {len(df_final)} ranking URLs saved to serp_scraped_data.csv.")
    display(df_final.head(10))
else:
    print("\nNo data was retrieved. Please check the error messages above.")


# In[ ]:


df_final


# In[ ]:


import pandas as pd
from collections import defaultdict
from itertools import combinations
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# --- 1. SET CLUSTERING THRESHOLDS ---
MIN_COMMON_URLS = 3
MIN_OVERLAP = 0.1

print("Loading scraped SERP data...")
df_serp = pd.read_csv("serp_scraped_data.csv")

# --- 2. MAP KEYWORDS TO URLs ---
keyword_urls = defaultdict(set)
for _, row in df_serp.iterrows():
    kw = row['keyword']
    url = row['url']
    if pd.notna(kw) and pd.notna(url):
        keyword_urls[kw].add(url)

print(f"Mapped ranking URLs for {len(keyword_urls)} unique keywords.")


# In[ ]:


# --- 3. BUILD THE NETWORK GRAPH ---
G = nx.Graph()

# Add all keywords as nodes
for keyword in keyword_urls.keys():
    G.add_node(keyword)

# Calculate overlaps and draw connecting edges
for kw1, kw2 in combinations(keyword_urls.keys(), 2):
    urls1 = keyword_urls[kw1]
    urls2 = keyword_urls[kw2]
    
    common_urls = urls1.intersection(urls2)
    if len(common_urls) >= MIN_COMMON_URLS:
        
        # The Set Theory Math: |A ∩ B| / min(|A|, |B|)
        overlap = len(common_urls) / min(len(urls1), len(urls2))
        
        if overlap >= MIN_OVERLAP:
            G.add_edge(kw1, kw2, weight=overlap)


# In[ ]:


# --- 4. EXTRACT AND LABEL CLUSTERS ---
# Find groups of connected keywords
clusters_raw = list(nx.connected_components(G))
print(f"Discovered {len(clusters_raw)} distinct keyword clusters.")

vectorizer = TfidfVectorizer(stop_words='english')
cluster_results = []

for cluster in clusters_raw:
    cluster_list = list(cluster)
    
    # Aggregate all unique URLs for this specific cluster
    cluster_urls = set()
    for kw in cluster_list:
        cluster_urls.update(keyword_urls[kw])
        
    # Use TF-IDF to find the most representative "Head" keyword to name the topic
    topic_name = ""
    try:
        tfidf_matrix = vectorizer.fit_transform(cluster_list)
        avg_similarities = []
        for i in range(len(cluster_list)):
            similarities = []
            for j in range(len(cluster_list)):
                if i != j:
                    sim = (tfidf_matrix[i] * tfidf_matrix[j].T).toarray()[0][0]
                    similarities.append(sim)
            avg_similarities.append(np.mean(similarities) if similarities else 0)
        
        topic_name = cluster_list[np.argmax(avg_similarities)]
    except:
        # Fallback if TF-IDF fails (e.g., keywords are too short/similar)
        topic_name = min(cluster_list, key=len)

    # Save the cluster data
    cluster_results.append({
        'cluster_topic': topic_name,
        'keywords': cluster_list,
        'size': len(cluster_list),
        'common_urls': list(cluster_urls),
        'url_count': len(cluster_urls)
    })

# --- 5. FINALIZE AND EXPORT ---
df_clusters = pd.DataFrame(cluster_results)
# Sort so the largest, most valuable clusters appear at the top
df_clusters = df_clusters.sort_values(by='size', ascending=False)

df_clusters.to_csv("keyword_clusters.csv", index=False)

print("Pipeline complete! Data saved to keyword_clusters.csv")
display(df_clusters.head(10))


# In[ ]:


df_clusters.to_clipboard()


# In[ ]:


# Extract the lists from the original un-flattened clusters
df_lists = df_clusters[['keywords', 'common_urls']].copy()

# The index of df_clusters is the cluster_id, so make it a column for the merge
df_lists['cluster_id'] = df_lists.index

# Left-merge the lists onto our new summary table
df_cluster_summary = pd.merge(
    df_cluster_summary,
    df_lists,
    on='cluster_id',
    how='left'
)

# Handle the "Unclustered" group (-1) which didn't exist in df_clusters
mask_unclustered = df_cluster_summary['cluster_id'] == -1
if mask_unclustered.any():
    # Grab all the unclustered queries directly from the mapped dataframe
    unclustered_kws = df_mapped[df_mapped['cluster_id'] == -1]['query'].dropna().tolist()
    
    idx = df_cluster_summary[mask_unclustered].index[0]
    df_cluster_summary.at[idx, 'keywords'] = unclustered_kws
    df_cluster_summary.at[idx, 'common_urls'] = ["No shared URLs (Unclustered)"]

# Reorder columns to make it clean and easy to read
final_cols = [
    'cluster_id', 
    'cluster_topic', 
    'keyword_count', 
    'total_clicks', 
    'total_impressions', 
    'blended_ctr_percent', 
    'keywords', 
    'common_urls'
]
df_cluster_summary = df_cluster_summary[final_cols]

# Save the enriched macro view
df_cluster_summary.to_csv("gsc_cluster_summary_enriched.csv", index=False)

print("Added keywords and common_urls lists to the summary!")
display(df_cluster_summary.head(10))


# In[ ]:


df_cluster_summary.to_clipboard()


# In[ ]:


df_cluster_summary.columns


# In[ ]:


import pandas as pd
import plotly.express as px

# 1. Load the dataset
df = pd.read_csv("gsc_cluster_summary_enriched.csv")

# 2. Exclude the unclustered data
if 'cluster_id' in df.columns:
    df_clean = df[df['cluster_id'] != -1].copy()
else:
    df_clean = df.copy()

# 3. Apply Percentile Filtering
lower_percentile = 0.20  # Removes the bottom 20%
upper_percentile = 0.90  # Removes the top 10%

lower_bound = df_clean['total_impressions'].quantile(lower_percentile)
upper_bound = df_clean['total_impressions'].quantile(upper_percentile)

df_filtered = df_clean[(df_clean['total_impressions'] >= lower_bound) & 
                       (df_clean['total_impressions'] <= upper_bound)].copy()

# 4. Calculate medians on the *filtered* dataset
median_impressions = df_filtered['total_impressions'].median()
median_ctr = df_filtered['blended_ctr_percent'].median()

# 5. Define and apply quadrant logic based on the filtered medians
def assign_quadrant(row):
    imp = row['total_impressions']
    ctr = row['blended_ctr_percent']
    
    if imp > median_impressions and ctr < median_ctr:
        return 'Opportunities (High Imp / Low CTR)'
    elif imp > median_impressions and ctr >= median_ctr:
        return 'Stars (High Imp / High CTR)'
    elif imp <= median_impressions and ctr >= median_ctr:
        return 'Niche Performers (Low Imp / High CTR)'
    else:
        return 'Underperformers (Low Imp / Low CTR)'

# Apply the function to create the new column
df_filtered['Quadrant'] = df_filtered.apply(assign_quadrant, axis=1)

# 6. Create the interactive Plotly scatter plot
fig = px.scatter(
    df_filtered,
    x='total_impressions',
    y='blended_ctr_percent',
    size='keyword_count',           
    color='blended_ctr_percent',    
    hover_name='cluster_topic',     
    hover_data={
        'total_impressions': ':,',  
        'blended_ctr_percent': ':.2f', 
        'total_clicks': ':,',
        'keyword_count': True,
        'Quadrant': True            # <--- Added the quadrant to the hover panel
    },
    title='Interactive Keyword Cluster Quadrants (Outliers Removed)',
    labels={
        'total_impressions': 'Total Impressions',
        'blended_ctr_percent': 'Blended CTR (%)',
        'keyword_count': 'Number of Keywords',
        'Quadrant': 'Strategic Group'
    },
    size_max=40,
    template='plotly_white'
)

# 7. Add the quadrant lines
fig.add_hline(
    y=median_ctr, 
    line_dash="dash", 
    line_color="blue",
    annotation_text=f"Median CTR: {median_ctr:.2f}%", 
    annotation_position="bottom right"
)

fig.add_vline(
    x=median_impressions, 
    line_dash="dash", 
    line_color="red",
    annotation_text=f"Median Impressions: {median_impressions:,.0f}", 
    annotation_position="top right"
)

# 8. Update layout 
fig.update_layout(
    height=700,
    width=1100,
    coloraxis_colorbar=dict(title="CTR (%)")
)

# 9. Render the plot
fig.show()


# In[ ]:


import pandas as pd
import numpy as np

# 1. Load your clustered data
df = pd.read_csv('gsc_cluster_summary_enriched.csv')

# 2. Exclude unclustered data (cluster_id == -1) to avoid skewing the baselines
if 'cluster_id' in df.columns:
    df_clean = df[df['cluster_id'] != -1].copy()
else:
    df_clean = df.copy()

# 3. Calculate the medians to serve as your quadrant thresholds
median_impressions = df_clean['total_impressions'].median()
median_ctr = df_clean['blended_ctr_percent'].median()

print(f"Thresholds -> Median Impressions: {median_impressions:.0f}, Median CTR: {median_ctr:.4f}%")

# 4. Define a function to categorize each row into a quadrant
def assign_quadrant(row):
    imp = row['total_impressions']
    ctr = row['blended_ctr_percent']
    
    if imp > median_impressions and ctr < median_ctr:
        return 'Opportunities (High Imp / Low CTR)'
    elif imp > median_impressions and ctr >= median_ctr:
        return 'Stars (High Imp / High CTR)'
    elif imp <= median_impressions and ctr >= median_ctr:
        return 'Niche Performers (Low Imp / High CTR)'
    else:
        return 'Underperformers (Low Imp / Low CTR)'

# 5. Apply the function to create a new column
df_clean['quadrant'] = df_clean.apply(assign_quadrant, axis=1)

# 6. Group and display the counts in each quadrant
print("\nQuadrant Distribution:")
print(df_clean['quadrant'].value_counts())

# 7. Save the newly categorized data to a new CSV file
df_clean.to_csv("gsc_cluster_summary_quadrants.csv", index=False)
print("\nExported categorized clusters to 'gsc_cluster_summary_quadrants.csv'.")


# In[ ]:


df_clean


# In[ ]:


import pandas as pd
import ast

# 1. Configuration
FILE_PATH = 'gsc_cluster_summary_enriched.csv'
MY_DOMAIN = '---'  # Set your target domain here

# 2. Load and prep data
df = pd.read_csv(FILE_PATH)

# Exclude unclustered data 
if 'cluster_id' in df.columns:
    df_clean = df[df['cluster_id'] != -1].copy()
else:
    df_clean = df.copy()

# 3. Define Quadrant Thresholds
median_impressions = df_clean['total_impressions'].median()
median_ctr = df_clean['blended_ctr_percent'].median()

# 4. Isolate the "Opportunities" (High Impressions, Low CTR)
df_opps = df_clean[(df_clean['total_impressions'] > median_impressions) & 
                   (df_clean['blended_ctr_percent'] < median_ctr)].copy()

print(f"Analyzing {len(df_opps)} Opportunity Clusters...\n")

competitor_analysis_data = []

# 5. Extract and filter competitor URLs
for index, row in df_opps.iterrows():
    cluster_topic = row['cluster_topic']
    impressions = row['total_impressions']
    ctr = row['blended_ctr_percent']
    
    # Extract the new columns
    keyword_count = row['keyword_count']
    
    # Safely parse the keywords list
    keywords_str = row.get('keywords', '[]')
    try:
        keywords = ast.literal_eval(keywords_str)
        if not isinstance(keywords, list):
            keywords = [keywords_str]
    except:
        keywords = [keywords_str]
    
    # Handle the common_urls column (safely evaluate the string representation of the list)
    urls_str = row.get('common_urls', '[]')
    if pd.isna(urls_str):
        continue
        
    try:
        # Convert string representation of list to actual Python list
        url_list = ast.literal_eval(urls_str)
        if not isinstance(url_list, list):
            url_list = [urls_str] # Fallback if it's just a single string
    except:
        url_list = [urls_str]

    # Filter out your domain
    competitor_urls = [url for url in url_list if MY_DOMAIN not in str(url)]
    
    # Store the results
    if competitor_urls:
        competitor_analysis_data.append({
            'cluster_topic': cluster_topic,
            'keyword_count': keyword_count,
            'keywords': keywords,
            'impressions': impressions,
            'ctr': ctr,
            'competitor_url_count': len(competitor_urls),
            'competitor_urls': competitor_urls
        })

# 6. Final Output
if competitor_analysis_data:
    df_competitors = pd.DataFrame(competitor_analysis_data)
    
    # Sort by impressions so the biggest opportunities are at the top
    df_competitors = df_competitors.sort_values(by='impressions', ascending=False)
    
    # Reorder columns to a logical view
    final_cols = [
        'cluster_topic', 'keyword_count', 'impressions', 'ctr', 
        'competitor_url_count', 'keywords', 'competitor_urls'
    ]
    df_competitors = df_competitors[final_cols]
    
    df_competitors.to_csv('opportunity_competitor_urls.csv', index=False)
    print("Success! Created 'opportunity_competitor_urls.csv'.")
    print(df_competitors[['cluster_topic', 'keyword_count', 'impressions']].head(10))
else:
    print("No competitor URLs found for the Opportunity clusters.")


# In[ ]:





# In[ ]:


df_competitors


# In[ ]:


GSC_PAGE_FILE = 'gsc_query_page_data_aggregated.csv'


# In[ ]:


# Load your new aggregated BigQuery export
try:
    df_gsc = pd.read_csv(GSC_PAGE_FILE)
except FileNotFoundError:
    print(f"Error: Could not find {GSC_PAGE_FILE}. Make sure the file is in the same directory.")
    df_gsc = pd.DataFrame(columns=['query', 'all_pages', 'unique_page_count']) # Dummy dataframe to prevent crash if file missing


# In[ ]:


df_competitors.columns


# In[ ]:





# In[ ]:


if not df_competitors.empty and not df_gsc.empty:
    
    # Perform a left join. 
    # Left table = df_competitors (using 'cluster_topic')
    # Right table = df_gsc (using 'query')
    df_final = pd.merge(
        df_competitors, 
        df_gsc[['query', 'all_pages', 'unique_page_count']], 
        left_on='cluster_topic', 
        right_on='query', 
        how='left'
    )
    
    # Drop the redundant 'query' column after the merge
    df_final = df_final.drop(columns=['query'])
    
    # Rename the columns as requested
    df_final = df_final.rename(columns={
        'all_pages': 'domain_pages',
        'unique_page_count': 'total_domain_page_count'
    })
    
    # Reorder columns for a logical flow
    final_cols = [
        'cluster_topic', 'impressions', 'ctr','keywords','keyword_count',
        'total_domain_page_count', 'domain_pages', 'competitor_urls','competitor_url_count'
    ]
    df_final = df_final[final_cols]
    
    # Save the output
    output_filename = 'opportunities_competitor_vs_domain_urls.csv'
    df_final.to_csv(output_filename, index=False)
    
    print(f"Success! Merged data saved to '{output_filename}'")
    print("\nPreview of final data:")
    print(df_final[['cluster_topic', 'total_domain_page_count', 'domain_pages']].head())

else:
    print("Could not complete merge. Either no opportunity clusters were found, or the GSC file is missing/empty.")


# In[ ]:


df_final.to_clipboard(index=False)


# In[ ]:




