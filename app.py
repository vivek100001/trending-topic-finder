import streamlit as st
import requests
from datetime import datetime, timedelta

# 🔑 Add your NewsAPI key here or use st.secrets["NEWS_API_KEY"]
NEWS_API_KEY = '4d9b9e571e6e4d59a096a98c6144bef2'

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
        'pageSize': 100  # max limit for NewsAPI
    }
    if websites:
        params['domains'] = ','.join(websites)

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        st.error(f"Error fetching data: {response.status_code} - {response.text}")
        return []

def filter_articles(articles, keyword, country_code=None):
    keyword_lower = keyword.lower()
    filtered = []

    for article in articles:
        title = article.get('title', '')
        source = article.get('source', {}).get('name', '')

        if title and keyword_lower in title.lower():
            if country_code:
                if country_code.lower() in source.lower():  # basic check
                    filtered.append(article)
            else:
                filtered.append(article)

    return filtered

# 🌐 Country codes (not accurate for filtering in NewsAPI everything, used as soft filters)
country_options = {
    "All": "",
    "India": "india",
    "United States": "us",
    "United Kingdom": "uk",
    "Canada": "canada",
    "Australia": "australia",
    "Germany": "germany",
    "France": "france"
}

# 🔷 Streamlit UI
st.set_page_config(page_title="Trending Topic Finder", layout="centered")
st.title("📈 Trending Topic Finder (Last 30 Days)")
st.text("Developed by: Vivek")
keyword = st.text_input("🔍 Enter a keyword").strip()
websites_input = st.text_input("🌐 Filter by website domains (optional, comma-separated)").strip()
websites = [w.strip() for w in websites_input.split(",") if w.strip()] if websites_input else None

selected_country = st.selectbox("🌎 Filter by country (based on source name)", list(country_options.keys()))
country_code = country_options[selected_country]

if st.button("Find Topics"):
    if not keyword:
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Fetching trending topics..."):
            articles = fetch_articles(keyword, websites)
            matched = filter_articles(articles, keyword, country_code)

            if matched:
                st.success(f"Found {len(matched)} articles matching '{keyword}'")
                for article in matched:
                    st.markdown(f"### [{article['title']}]({article['url']})")
                    st.markdown(f"**Source:** {article['source']['name']} | **Date:** {article['publishedAt'][:10]}")
                    st.write("---")
            else:
                st.info("No articles matched the keyword.")
