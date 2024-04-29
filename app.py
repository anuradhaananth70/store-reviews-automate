import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google_play_scraper import reviews_all, Sort
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
    g_df2['language_code'] = 'en'
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
    a_df2['language_code'] = 'en'
    a_df2['country_code'] = 'us'
    a_df2.insert(loc=1, column='review_id', value=[uuid.uuid4() for _ in range(len(a_df2.index))])
    a_df2['review_date'] = pd.to_datetime(a_df2['date'])  # Use 'date' column as 'review_date'
    a_df2 = a_df2.where(pd.notnull(a_df2), None)
    return a_df2

# Sidebar filters
st.sidebar.header('Filters')
min_rating = int(st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0))
start_date = pd.Timestamp(st.sidebar.date_input('Start Date', pd.to_datetime('2024-04-01')))
end_date = pd.Timestamp(st.sidebar.date_input('End Date', pd.to_datetime('2024-05-31')))
keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Load reviews data
reviews_data1 = fetch_google_reviews()
reviews_data2 = fetch_apple_reviews()

# Concatenate the review dataframes and reset index
all_reviews_data = pd.concat([reviews_data1, reviews_data2], ignore_index=True)

# Function to filter reviews based on sidebar inputs
def filter_reviews(reviews_data, min_rating, start_date, end_date, keyword):
    filtered_reviews = reviews_data[(reviews_data['rating'] >= min_rating) &
                                    (reviews_data['review_date'] >= start_date) &
                                    (reviews_data['review_date'] <= end_date)]
    if keyword:
        filtered_reviews = filtered_reviews[filtered_reviews['review_description'].str.contains(keyword, case=False)]
    return filtered_reviews

# Apply filters
filtered_reviews = filter_reviews(all_reviews_data, min_rating, start_date, end_date, keyword)

# Separate the filtered reviews for Google Play Store and App Store
filtered_reviews1 = filtered_reviews[filtered_reviews['source'] == 'Google Play']
filtered_reviews2 = filtered_reviews[filtered_reviews['source'] == 'App Store']

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
plt.bar(filtered_reviews1['rating'].value_counts().index, filtered_reviews1['rating'].value_counts().values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Reviews per Rating (Google Play Store)')
st.pyplot(plt)

# Plot bar graph for App Store reviews
plt.figure(figsize=(8, 6))
plt.bar(filtered_reviews2['rating'].value_counts().index, filtered_reviews2['rating'].value_counts().values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Reviews per Rating (App Store)')
st.pyplot(plt)
