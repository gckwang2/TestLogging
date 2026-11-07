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

@st.cache_data(ttl=1800, show_spinner=False) 
def fetch_feed_data(url):
    """Fetches and extracts simple strings from the RSS feed for safe Streamlit caching."""
    parsed = feedparser.parse(url)
    
    # If the feed failed to load completely
    if not getattr(parsed, 'entries', None):
        return None
        
    feed_title = parsed.feed.get('title', 'Unknown Feed')
    
    # Extract only the primitive strings we need (safe for PyArrow serialization)
    entries = []
    for entry in parsed.entries[:5]:
        entries.append({
            "title": entry.get("title", "No Title"),
            "link": entry.get("link", url)
        })
        
    return {
        "title": feed_title,
        "entries": entries
    }

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
            
            # Consume the simplified dictionary returned by the cached function
            if feed_data and feed_data.get('entries'):
                feed_title = feed_data['title']
                with st.sidebar.expander(f"📌 {feed_title}", expanded=False):
                    for entry in feed_data['entries']:
                        st.markdown(f"- [{entry['title']}]({entry['link']})")
            else:
                st.sidebar.error(f"Failed to load: {url}")
