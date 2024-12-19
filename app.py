import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Define function for first code functionality
def search_hacker_news(query, strict_search):
    search_url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage=50"  # Fetch 50 posts initially
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    data = response.json()

    posts = []
    for hit in data.get("hits", []):
        title = hit.get("title", "No Title")
        post = {
            "Title": title,
            "Points": hit.get("points", 0),
            "Author": hit.get("author", "Unknown"),
            "Comments": hit.get("num_comments", 0),
            "Date": datetime.fromtimestamp(hit["created_at_i"]).strftime('%Y-%m-%d'),
            "HN URL": f"https://news.ycombinator.com/item?id={hit['objectID']}"
        }
        if strict_search and query.lower() not in map(str.lower, title.split()):
            continue
        posts.append(post)

    # Always filter to top 10 by points
    return sorted(posts, key=lambda x: x["Points"], reverse=True)[:10]

# Define function to get top posts of the last 24 hours
def get_top_posts_of_the_day():
    current_time = datetime.utcnow()
    yesterday_timestamp = int((current_time - timedelta(days=1)).timestamp())
    search_url = f"https://hn.algolia.com/api/v1/search?tags=story&numericFilters=created_at_i>{yesterday_timestamp}&hitsPerPage=50"
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
    return sorted(posts, key=lambda x: x["Points"], reverse=True)[:10]

def plot_bar_chart_with_titles(df, title):
    # Set the style for dark theme
    plt.style.use('dark_background')
    
    # Create figure and axis with larger figure size
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create bars with a more vibrant color
    bars = ax.bar(range(len(df["Title"])), df["Points"], 
                 color='#4287f5',  # Brighter blue
                 width=0.7)
    
    # Customize the plot
    ax.set_title(title, fontsize=18, pad=20, color='#ffffff', fontweight='bold')
    ax.set_xlabel("Post Titles", fontsize=14, labelpad=15, color='#ffffff')
    ax.set_ylabel("Points", fontsize=14, labelpad=15, color='#ffffff')
    
    # Customize grid
    ax.grid(axis='y', linestyle='--', alpha=0.2, color='#666666')
    
    # Set background color
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    
    # Customize spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#666666')
    ax.spines['bottom'].set_color('#666666')
    
    # Customize ticks
    ax.tick_params(axis='both', colors='#ffffff', labelsize=11)
    
    # Customize x-axis labels
    ax.set_xticks(range(len(df["Title"])))
    # Truncate long titles and add ellipsis
    shortened_titles = [title[:40] + '...' if len(title) > 40 else title for title in df["Title"]]
    ax.set_xticklabels(shortened_titles, 
                      rotation=45, 
                      ha="right",
                      fontsize=11)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{int(height)}',
                ha='center', va='bottom', 
                color='#ffffff',
                fontsize=11,
                fontweight='bold')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Display the plot in Streamlit
    st.pyplot(fig)

def display_hn_data(df, title):
    # Drop the Author column
    df_display = df.drop(columns=['Author'])
    
    # Reorder columns
    df_display = df_display[['Title', 'Points', 'Comments', 'Date', 'HN URL']]
    
    # Display the dataframe with custom formatting
    st.markdown(f"### {title}")
    st.dataframe(
        df_display,
        column_config={
            "Title": st.column_config.TextColumn(
                "Title",
                width="large",
            ),
            "HN URL": st.column_config.LinkColumn("Link"),
            "Points": st.column_config.NumberColumn(
                "Points",
                format="%d ⭐"
            ),
            "Comments": st.column_config.NumberColumn(
                "Comments",
                format="%d 💬"
            )
        },
        hide_index=True,
        height=400  # Fixed height to prevent scrolling
    )

# Streamlit App setup
st.set_page_config(page_title="HackerNews Analysis", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

# Add "Try on Flows" button to the top right
col1, col2 = st.columns([6,1])
with col1:
    st.title("Hacker News Leaderboard")
with col2:
    st.link_button("Try on Atina Flows", 
                   "https://app.staging.athina.ai//apps/8238a4af-5759-475a-883a-2e6ece6cc0be/share",
                   type="primary")
    
st.sidebar.markdown("## Search Options")
query = st.sidebar.text_input("Enter your search query:", value="")
strict_search = st.sidebar.checkbox("Strict search for the keyword")
run_query = st.sidebar.button("Run Query")

st.sidebar.markdown(
    """
    ---
    <p style="text-align: center; font-size: 0.9em; color: #666;">
        Made by <a href="https://www.athina.ai/" target="_blank" style="color: #007BFF; text-decoration: none;">Athina AI</a>
    </p>
    """,
    unsafe_allow_html=True
)

# First code output
st.header("Search Results for Your Query")
if run_query and query:
    search_results = search_hacker_news(query, strict_search)
    if search_results:
        df_search = pd.DataFrame(search_results)
        display_hn_data(df_search, "Search Results")
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
    display_hn_data(df_top_posts, "Top Posts")
    plot_bar_chart_with_titles(df_top_posts, "Top Posts: Points by Post Title")
else:
    st.write("No top posts found.")
