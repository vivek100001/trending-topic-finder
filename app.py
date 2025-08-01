import streamlit as st
import requests
import feedparser
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq

# ---------- 🔍 Trending Query from Google ----------
def get_trending_queries(keyword, geo):
    pytrends = TrendReq(hl='en-US', tz=330)
    pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo=geo)
    related = pytrends.related_queries()
    top_queries = related.get(keyword, {}).get('top')
    if top_queries is not None:
        return top_queries['query'].tolist()[:5]  # Top 5 related queries
    return []

# ---------- 📰 News from Google News RSS ----------
def fetch_articles_from_google_rss(query, base_keyword):
    keyword = f'"{base_keyword} {query}"'
    encoded_query = keyword.replace(' ', '+')
    url = f"https://news.google.com/rss/search?q={encoded_query}+when:30d&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        if base_keyword.lower() in entry.title.lower() or query.lower() in entry.title.lower():
            articles.append({
                'title': entry.title,
                'url': entry.link,
                'published': entry.published
            })
    return articles

# ---------- 📥 CSV Export ----------
def convert_articles_to_csv(articles):
    df = pd.DataFrame(articles)
    return df.to_csv(index=False).encode('utf-8')

# ---------- 🌍 Geo Codes ----------
geo_map = {
    "Worldwide": "",
    "India": "IN",
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU"
}

# ---------- 🖼️ Streamlit App ----------
st.set_page_config(page_title="Google Trends + News", layout="wide")
st.title("🔥 Trending Topics & News Finder")
st.markdown("Enter a keyword to find trending search queries and latest news articles in India.")

keyword = st.text_input("Enter a seed keyword (e.g., car insurance, fitness, AI)")
country_name = st.selectbox("Select a region", list(geo_map.keys()))
geo = geo_map[country_name]

if st.button("Get Trends & News") and keyword:
    with st.spinner("📊 Fetching related trending queries..."):
        queries = get_trending_queries(keyword, geo)

    if not queries:
        st.warning("No trending queries found for this keyword.")
    else:
        st.success(f"Top related trending queries in {country_name}:")
        for i, q in enumerate(queries, 1):
            st.markdown(f"### {i}. {q}")
            with st.spinner(f"Fetching news for: {q}"):
                articles = fetch_articles_from_google_rss(q, keyword)
                if articles:
                    for article in articles:
                        st.markdown(f"- [{article['title']}]({article['url']})  \n_Published: {article['published']}_")

                    # ✅ Add download button
                    csv = convert_articles_to_csv(articles)
                    st.download_button(
                        label="📥 Download News as CSV",
                        data=csv,
                        file_name=f"{q.replace(' ', '_')}_news.csv",
                        mime='text/csv'
                    )
                else:
                    st.markdown("_No relevant news found for this topic._")
            st.write("---")
