import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google_play_scraper import app, Sort, reviews_all
from app_store_scraper import AppStore
import uuid

# Function to fetch Google Play reviews
def fetch_google_play_reviews():
    g_reviews = reviews_all(
        "com.marrow",
        sleep_milliseconds=0,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
    )
    g_df = pd.DataFrame(np.array(g_reviews), columns=['review'])
    g_df2 = g_df.join(pd.DataFrame(g_df.pop('review').tolist()))
    g_df2.drop(columns={'userImage', 'reviewCreatedVersion'}, inplace=True)
    g_df2.rename(columns={'score': 'rating', 'userName': 'user_name', 'reviewId': 'review_id',
                          'content': 'review_description', 'at': 'review_date',
                          'replyContent': 'developer_response', 'repliedAt': 'developer_response_date',
                          'thumbsUpCount': 'thumbs_up'}, inplace=True)
    g_df2.insert(loc=0, column='source', value='Google Play')
    g_df2.insert(loc=3, column='review_title', value=None)
    g_df2['laguage_code'] = 'en'
    g_df2['country_code'] = 'us'
    g_df2['review_date'] = pd.to_datetime(g_df2['review_date'])
    return g_df2

# Function to fetch App Store reviews
def fetch_app_store_reviews():
    a_reviews = AppStore(country='us', app_name='marrow-for-neet-pg-next', app_id='1226886654')
    a_reviews.review()
    a_df = pd.DataFrame(np.array(a_reviews.reviews), columns=['review'])
    a_df2 = a_df.join(pd.DataFrame(a_df.pop('review').tolist()))
    a_df2.drop(columns={'isEdited'}, inplace=True)
    a_df2.insert(loc=0, column='source', value='App Store')
    a_df2['developer_response_date'] = None
    a_df2['thumbs_up'] = None
    a_df2['laguage_code'] = 'en'
    a_df2['country_code'] = 'us'
    a_df2.insert(loc=1, column='review_id', value=[uuid.uuid4() for _ in range(len(a_df2.index))])
    a_df2.rename(columns={'review': 'review_description', 'userName': 'user_name', 'date': 'review_date',
                          'title': 'review_title', 'developerResponse': 'developer_response'}, inplace=True)
    a_df2 = a_df2.where(pd.notnull(a_df2), None)
    return a_df2

# Function to filter reviews based on sidebar inputs
def filter_reviews(reviews_data, min_rating, start_date, end_date, keyword):
    filtered_reviews = reviews_data[(reviews_data['rating'] >= min_rating) &
                                    (reviews_data['review_date'] >= start_date) &
                                    (reviews_data['review_date'] <= end_date)]
    if keyword:
        filtered_reviews = filtered_reviews[filtered_reviews['review_description'].str.contains(keyword, case=False)]
    return filtered_reviews

# Streamlit UI
st.title('👥 App Store and Playstore Reviews - Sentiment Analysis')

# Sidebar image
st.sidebar.image('ml.png', width=150)

# Sidebar filters for Google Play Store reviews
st.sidebar.header('Google Play Store Filters')
gp_min_rating = int(st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0))
gp_start_date = pd.Timestamp(st.sidebar.date_input('Start Date', pd.to_datetime('2024-04-01')))
gp_end_date = pd.Timestamp(st.sidebar.date_input('End Date', pd.to_datetime('2024-04-25')))
gp_keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Sidebar filters for App Store reviews
st.sidebar.header('App Store Filters')
as_min_rating = int(st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0))
as_start_date = pd.Timestamp(st.sidebar.date_input('Start Date', pd.to_datetime('2024-04-01')))
as_end_date = pd.Timestamp(st.sidebar.date_input('End Date', pd.to_datetime('2024-04-25')))
as_keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Load reviews data
google_play_reviews_data = fetch_google_play_reviews()
app_store_reviews_data = fetch_app_store_reviews()

# Apply filters for Google Play Store reviews
filtered_google_play_reviews = filter_reviews(google_play_reviews_data, gp_min_rating, gp_start_date, gp_end_date, gp_keyword)

# Apply filters for App Store reviews
filtered_app_store_reviews = filter_reviews(app_store_reviews_data, as_min_rating, as_start_date, as_end_date, as_keyword)

# Count number of reviews per rating for Google Play Store reviews
gp_rating_counts = filtered_google_play_reviews['rating'].value_counts().sort_index()
gp_rating_counts = gp_rating_counts.reindex(range(1, 6), fill_value=0)

# Count number of reviews per rating for App Store reviews
as_rating_counts = filtered_app_store_reviews['rating'].value_counts().sort_index()
as_rating_counts = as_rating_counts.reindex(range(1, 6), fill_value=0)

# Display filtered Google Play Store reviews
st.write('Google Play Store Reviews:')
with st.dataframe(filtered_google_play_reviews.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1), height=800, width=1000):
    st.write(filtered_google_play_reviews)

# Plot bar graph for Google Play Store reviews
plt.figure(figsize=(8, 6))
plt.bar(gp_rating_counts.index, gp_rating_counts.values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Google Play Store Reviews per Rating')
st.pyplot(plt)

# Display filtered App Store reviews
st.write('App Store Reviews:')
with st.dataframe(filtered_app_store_reviews.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1), height=800, width=1000):
    st.write(filtered_app_store_reviews)

# Plot bar graph for App Store reviews
plt.figure(figsize=(8, 6))
plt.bar(as_rating_counts.index, as_rating_counts.values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of App Store Reviews per Rating')
st.pyplot(plt)
