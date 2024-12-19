import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Define function for first code functionality
def search_hacker_news(query):
    search_url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage=10"
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    data = response.json()

    posts = []
    for hit in data.get("hits", []):
        posts.append({
            "Title": hit.get("title", "No Title"),
            "Points": hit.get("points", 0),
            "Author": hit.get("author", "Unknown"),
            "Comments": hit.get("num_comments", 0),
            "Date": datetime.fromtimestamp(hit["created_at_i"]).strftime('%Y-%m-%d'),
            "HN URL": f"https://news.ycombinator.com/item?id={hit['objectID']}",
        })
    return posts

# Define function for second code functionality
def get_top_posts_of_the_day():
    current_time = datetime.utcnow()
    yesterday_timestamp = int((current_time - timedelta(days=1)).timestamp())

    search_url = f"https://hn.algolia.com/api/v1/search?tags=story&numericFilters=created_at_i>{yesterday_timestamp}&hitsPerPage=10"
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    data = response.json()

    posts = []
    for post in data.get("hits", []):
        posts.append({
            "Title": post.get("title", "N/A"),
            "Points": post.get("points", 0),
            "Comments": post.get("num_comments", 0),
            "Author": post.get("author", "N/A"),
            "Date": datetime.fromtimestamp(post.get("created_at_i")).strftime('%Y-%m-%d %H:%M:%S'),
            "HN URL": f"https://news.ycombinator.com/item?id={post['objectID']}",
        })
    return posts

# Function to plot bar chart with titles on x-axis and points on y-axis
def plot_bar_chart_with_titles(df, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df["Title"], df["Points"], color="skyblue")
    ax.set_title(title)
    ax.set_xlabel("Post Titles")
    ax.set_ylabel("Points")
    ax.set_xticks(range(len(df["Title"])))
    ax.set_xticklabels(df["Title"], rotation=45, ha="right")
    st.pyplot(fig)

# Streamlit App
st.set_page_config(page_title="Hacker News Analysis", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
st.title("HackerNews Leaderboard")

# Sidebar for user input
query = st.sidebar.text_input("Enter your search query:", value="")
st.sidebar.markdown("_Type in the query to start._")
run_query = st.sidebar.button("Run Query")

# First code output
st.header("Search Results for Your Query")
if run_query and query:
    search_results = search_hacker_news(query)
    if search_results:
        df_search = pd.DataFrame(search_results)
        st.dataframe(df_search, use_container_width=True)
        plot_bar_chart_with_titles(df_search, "Search Results: Points by Post Title")
    else:
        st.write("No results found.")
else:
    st.write("Type in the query to start.")

# Second code output
st.header("Top Posts of the Last 24 Hours")
top_posts = get_top_posts_of_the_day()
if top_posts:
    df_top_posts = pd.DataFrame(top_posts)
    st.dataframe(df_top_posts, use_container_width=True)
    plot_bar_chart_with_titles(df_top_posts, "Top Posts: Points by Post Title")
else:
    st.write("No top posts found.")
