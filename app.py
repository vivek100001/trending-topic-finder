import streamlit as st
import requests
from datetime import datetime, timedelta
from pytrends.request import TrendReq

# Replace with your actual NewsAPI key
NEWS_API_KEY = '4d9b9e571e6e4d59a096a98c6144bef2'

def get_trending_queries(keyword, geo):
    pytrends = TrendReq(hl='en-US', tz=330)
    pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo=geo)
    related = pytrends.related_queries()
    top_queries = related.get(keyword, {}).get('top')
    if top_queries is not None:
        return top_queries['query'].tolist()[:5]  # Top 5 related queries
    return []

def fetch_articles_from_newsapi(query):
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': NEWS_API_KEY,
        'pageSize': 10
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        return []

# 🌍 Country selection (Google Trends geo codes)
geo_map = {
    "Worldwide": "",
    "India": "IN",
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU"
}

# 🖼️ Streamlit UI
st.set_page_config(page_title="Google Trends + News API App", layout="wide")
st.title("🔥 Trending Topics + News Headlines")
st.markdown("Enter a keyword to discover what people are searching and read related news articles.")

keyword = st.text_input("Enter a seed keyword (e.g., AI, fitness, crypto)")
country_name = st.selectbox("Select a region", list(geo_map.keys()))
geo = geo_map[country_name]

if st.button("Get Trends & News") and keyword:
    with st.spinner("Analyzing Google Trends..."):
        queries = get_trending_queries(keyword, geo)

    if not queries:
        st.warning("No trending queries found for this keyword.")
    else:
        st.success(f"Top related trending queries in {country_name}:")
        for i, q in enumerate(queries, 1):
            st.markdown(f"**{i}. {q}**")
            with st.spinner(f"Fetching news for: {q}"):
                articles = fetch_articles_from_newsapi(q)
                if articles:
                    for article in articles:
                        st.markdown(f"- [{article['title']}]({article['url']})")
                else:
                    st.markdown(f"_No news found for this topic_")
            st.write("---")
