import streamlit as st
import feedparser
import os

FEED_FILE = "rss_subscriptions.txt"

def get_saved_feeds():
    """Reads the saved RSS URLs from the local file."""
    if not os.path.exists(FEED_FILE):
        return []
    with open(FEED_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_feed(url):
    """Saves a new RSS URL to the file if it doesn't already exist."""
    feeds = get_saved_feeds()
    if url not in feeds:
        with open(FEED_FILE, "a") as f:
            f.write(f"{url}\n")
        return True
    return False

@st.cache_data(ttl=1800) # Caches the RSS fetch for 30 minutes
def fetch_feed_data(url):
    """Fetches and parses the RSS feed."""
    return feedparser.parse(url)

def render_rss_sidebar():
    """Renders the RSS reader interface inside the Streamlit sidebar."""
    st.sidebar.header("📰 RSS News Reader")
    
    # Subscription Input
    new_feed = st.sidebar.text_input("Enter RSS Feed URL:", placeholder="https://example.com/rss")
    if st.sidebar.button("Subscribe", use_container_width=True):
        if new_feed:
            if save_feed(new_feed):
                st.sidebar.success("Subscribed successfully!")
                st.rerun() # Refresh the app to load the new feed immediately
            else:
                st.sidebar.warning("Already subscribed to this feed.")
        else:
            st.sidebar.error("Please enter a valid URL.")
    
    st.sidebar.divider()
    
    # Display Subscribed Feeds
    feeds = get_saved_feeds()
    if not feeds:
        st.sidebar.info("No subscriptions yet. Add an RSS link above.")
    else:
        st.sidebar.subheader("Latest News")
        for url in feeds:
            feed_data = fetch_feed_data(url)
            
            # Check if the feed is valid and has entries
            if feed_data and getattr(feed_data, 'entries', None):
                feed_title = feed_data.feed.get('title', 'Unknown Feed')
                with st.sidebar.expander(f"📌 {feed_title}", expanded=False):
                    # Display the top 5 most recent articles
                    for entry in feed_data.entries[:5]:
                        st.markdown(f"- [{entry.title}]({entry.link})")
            else:
                st.sidebar.error(f"Failed to load: {url}")
