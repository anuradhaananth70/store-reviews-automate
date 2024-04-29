import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google_play_scraper import app, Sort, reviews_all
from app_store_scraper import AppStore
import uuid

# Streamlit UI
st.title('👥 App Store and Playstore Reviews - Sentiment Analysis')

# Function to fetch Google Play reviews
def fetch_google_reviews():
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

# Function to fetch app store reviews
def fetch_apple_reviews():
    a_reviews = AppStore('us', 'marrow-for-neet-pg-next', '1226886654')
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

# Load reviews data
reviews_data1 = fetch_google_reviews()
reviews_data2 = fetch_apple_reviews()

# Function to filter google reviews based on sidebar inputs
def filter_google_reviews(reviews_data, min_rating, start_date, end_date, keyword, included_rating=None):
    filtered_reviews1 = reviews_data[(reviews_data['rating'] >= min_rating) &
                                     (reviews_data['review_date'] >= start_date) &
                                     (reviews_data['review_date'] <= end_date)]
    if keyword:
        filtered_reviews1 = filtered_reviews1[filtered_reviews1['review_description'].str.contains(keyword, case=False)]
    if included_rating is not None:
        filtered_reviews1 = filtered_reviews1[filtered_reviews1['rating'] == included_rating]
    return filtered_reviews1

# Function to filter apple reviews based on sidebar inputs
def filter_apple_reviews(reviews_data, min_rating, start_date, end_date, keyword, included_rating=None):
    filtered_reviews2 = reviews_data[(reviews_data['rating'] >= min_rating) &
                                     (reviews_data['review_date'] >= start_date) &
                                     (reviews_data['review_date'] <= end_date)]
    if keyword:
        filtered_reviews2 = filtered_reviews2[filtered_reviews2['review_description'].str.contains(keyword, case=False)]
    if included_rating is not None:
        filtered_reviews2 = filtered_reviews2[filtered_reviews2['rating'] == included_rating]
    return filtered_reviews2

# Sidebar filters
st.sidebar.header('Filters')
min_rating = int(st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0))
included_rating = None  # Initialize included rating
if st.sidebar.checkbox('Include Selected Rating'):
    included_rating = int(st.sidebar.selectbox('Include Rating', [1, 2, 3, 4, 5], index=0))
start_date = pd.Timestamp(st.sidebar.date_input('Start Date', pd.to_datetime('2024-04-01')))
end_date = pd.Timestamp(st.sidebar.date_input('End Date', pd.to_datetime('2024-05-31')))
keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Apply filters for Google Play Store reviews
filtered_reviews1 = filter_google_reviews(reviews_data1, min_rating, start_date, end_date, keyword, included_rating)

# Apply filters for App Store reviews
filtered_reviews2 = filter_apple_reviews(reviews_data2, min_rating, start_date, end_date, keyword, included_rating)

# Count number of reviews per rating for Google Play Store reviews
rating_counts1 = filtered_reviews1['rating'].value_counts().sort_index()

# Count number of reviews per rating for App Store reviews
rating_counts2 = filtered_reviews2['rating'].value_counts().sort_index()

# Ensure that all ratings are present, even if there are no reviews for them
rating_counts1 = rating_counts1.reindex(range(1, 6), fill_value=0)
rating_counts2 = rating_counts2.reindex(range(1, 6), fill_value=0)

# Display filtered Google Play Store reviews
st.write('Google Play Store Reviews:')
with st.dataframe(filtered_reviews1.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1), height=800, width=1000):
    st.write(filtered_reviews1)

# Display filtered App Store reviews
st.write('App Store Reviews:')
with st.dataframe(filtered_reviews2.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1), height=800, width=1000):
    st.write(filtered_reviews2)

# Plot bar graph for Google Play Store reviews
plt.figure(figsize=(8, 6))
plt.bar(rating_counts1.index, rating_counts1.values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Reviews per Rating (Google Play Store)')
st.pyplot(plt)

# Plot bar graph for App Store reviews
plt.figure(figsize=(8, 6))
plt.bar(rating_counts2.index, rating_counts2.values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Reviews per Rating (App Store)')
st.pyplot(plt)
