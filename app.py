import streamlit as st
import requests
from datetime import datetime, timedelta

# 🔑 Add your NewsAPI key here
NEWS_API_KEY = '4d9b9e571e6e4d59a096a98c6144bef2'  # Replace this

def fetch_articles(keyword, websites=None):
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': keyword,
        'from': from_date,
        'to': to_date,
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': NEWS_API_KEY,
    }
    if websites:
        params['domains'] = ','.join(websites)

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        st.error(f"Error fetching data: {response.status_code} - {response.text}")
        return []

def filter_articles(articles, keyword):
    keyword_lower = keyword.lower()
    filtered = []
    for article in articles:
        title = article.get('title', '')
        if title and keyword_lower in title.lower():
            filtered.append(article)
    return filtered

# 🔷 Streamlit UI
st.set_page_config(page_title="Trending Topic Finder", layout="centered")
st.title("📈 Trending Topic Finder (Last 30 Days)")

keyword = st.text_input("🔍 Enter a keyword")
websites_input = st.text_input("🌐 Filter by website domains (optional, comma-separated)")
websites = [w.strip() for w in websites_input.split(",") if w.strip()] if websites_input else None

if st.button("Find Topics"):
    if not keyword:
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Fetching trending topics..."):
            articles = fetch_articles(keyword, websites)
            matched = filter_articles(articles, keyword)

            if matched:
                st.success(f"Found {len(matched)} articles matching '{keyword}'")
                for article in matched:
                    st.markdown(f"### [{article['title']}]({article['url']})")
                    st.markdown(f"**Source:** {article['source']['name']} | **Date:** {article['publishedAt'][:10]}")
                    st.write("---")
            else:
                st.info("No articles matched the keyword.")
