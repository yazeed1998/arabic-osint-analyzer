import sys
import os
# Force add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from app.location_extractor import extract_and_geocode
from textblob import TextBlob
import io

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/aljazeera_translated.csv')
        df['date_collected'] = pd.to_datetime(df['date_collected'], utc=True, errors='coerce')
        if df.empty:
            st.warning("⚠ No data found. Using sample data for demo.")
            df = pd.DataFrame({
                'date_collected': pd.date_range(end=pd.Timestamp.today(), periods=5).to_pydatetime(),
                'title': ['خبر عربي']*5,
                'title_en': [
                    'Sample headline about Gaza',
                    'Sample headline about Syria',
                    'Sample headline about Lebanon',
                    'Sample headline about Egypt',
                    'Sample headline about Iraq'
                ],
                'source': ['Al Jazeera Arabic']*5,
                'link': ['https://aljazeera.net']*5
            })
        return df
    except FileNotFoundError:
        st.error("❌ Translated data file not found. Please run the scraper and translator first.")
        return pd.DataFrame()

# Analyze sentiment
@st.cache_data
def add_sentiment(df):
    df['sentiment'] = df['title_en'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['sentiment_label'] = df['sentiment'].apply(
        lambda x: '😊 Positive' if x > 0 else ('😐 Neutral' if x == 0 else '☹ Negative')
    )
    return df

# Export data
def export_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig')

def main():
    st.set_page_config(page_title="Arabic OSINT Dashboard", layout="wide")
    st.title("🌐 Arabic OSINT Dashboard")
    st.markdown("Collect, translate, and analyze Arabic headlines from Al Jazeera.")

    df = load_data()
    if df.empty:
        st.stop()

    df = add_sentiment(df)

    # Sidebar filters
    st.sidebar.header("🔎 Filters")
    keyword = st.sidebar.text_input("Search keyword (English):")
    sources = st.sidebar.multiselect("Select sources:", options=df['source'].unique(), default=list(df['source'].unique()))
    sentiment_options = st.sidebar.multiselect("Filter by sentiment:", options=df['sentiment_label'].unique(), default=list(df['sentiment_label'].unique()))
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(df['date_collected'].min(), df['date_collected'].max()),
        min_value=df['date_collected'].min(),
        max_value=df['date_collected'].max()
    )

    # Apply filters
    filtered_df = df[
        (df['source'].isin(sources)) &
        (df['sentiment_label'].isin(sentiment_options)) &
        (df['date_collected'].dt.date.between(date_range[0], date_range[1]))
    ]
    if keyword:
        filtered_df = filtered_df[filtered_df['title_en'].str.contains(keyword, case=False, na=False)]

    if filtered_df.empty:
        st.warning("⚠ No headlines match your filters.")
        st.stop()

    # Geocode locations
    geo_df = extract_and_geocode(filtered_df)

    st.subheader(f"📄 Headlines ({len(filtered_df)} results)")
    st.dataframe(filtered_df[['date_collected', 'title', 'title_en', 'source', 'sentiment_label', 'link']], height=400)

    # Charts
    st.subheader("📊 Headline Trends Over Time")
    if not filtered_df.empty:
        trends = filtered_df.groupby(filtered_df['date_collected'].dt.date).size()
        st.line_chart(trends)

    st.subheader("📊 Top Sources")
    if not filtered_df.empty:
        source_counts = filtered_df['source'].value_counts()
        st.bar_chart(source_counts)

    st.subheader("📊 Sentiment Distribution")
    if not filtered_df.empty:
        sentiment_counts = filtered_df['sentiment_label'].value_counts()
        st.bar_chart(sentiment_counts)

    # Map view
    st.subheader("🗺 Map View")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')
    if 'latitude' in geo_df and 'longitude' in geo_df:
        geo_df = geo_df.dropna(subset=['latitude', 'longitude'])
        if not geo_df.empty:
            for _, row in geo_df.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"<b>{row['headline']}</b><br>{row['location_name']}",
                    tooltip=row['location_name'],
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
        else:
            st.info("ℹ No geocoded locations found for current filters.")
    else:
        st.info("ℹ Geolocation data unavailable.")

    st_folium(m, width=700, height=500)

    # Export options
    st.subheader("📤 Export Data")
    csv_data = export_csv(filtered_df)
    st.download_button("Download Filtered Data as CSV", data=csv_data, file_name="filtered_headlines.csv", mime="text/csv")

if __name__ == "__main__":
    main()
