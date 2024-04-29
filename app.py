import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google_play_scraper import app, Sort, reviews_all

# Streamlit UI
st.title('👥 App Store and Playstore Reviews - Sentiment Analysis')

# Sidebar image
st.sidebar.image('ml.png', width=150)

# Function to fetch Google Play reviews
def fetch_reviews():
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

# Load reviews data
reviews_data = fetch_reviews()

# Function to filter reviews based on sidebar inputs
def filter_reviews(reviews_data, min_rating, start_date, end_date, keyword, included_rating=None):
    filtered_reviews = reviews_data[(reviews_data['rating'] >= min_rating) &
                                    (reviews_data['review_date'] >= start_date) &
                                    (reviews_data['review_date'] <= end_date)]
    if keyword:
        filtered_reviews = filtered_reviews[filtered_reviews['review_description'].str.contains(keyword, case=False)]
    if included_rating is not None:
        filtered_reviews = filtered_reviews[filtered_reviews['rating'] == included_rating]
    return filtered_reviews

# Sidebar filters
st.sidebar.header('Filters')
min_rating = int(st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0))
included_rating = None  # Initialize included rating
if st.sidebar.checkbox('Include Selected Rating'):
    included_rating = int(st.sidebar.selectbox('Include Rating', [1, 2, 3, 4, 5], index=0))
start_date = pd.Timestamp(st.sidebar.date_input('Start Date', pd.to_datetime('2024-04-01')))
end_date = pd.Timestamp(st.sidebar.date_input('End Date', pd.to_datetime('2024-05-31')))
keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Apply filters
filtered_reviews = filter_reviews(reviews_data, min_rating, start_date, end_date, keyword, included_rating)

# Count number of reviews per rating
rating_counts = filtered_reviews['rating'].value_counts().sort_index()

# Ensure that all ratings are present, even if there are no reviews for them
rating_counts = rating_counts.reindex(range(1, 6), fill_value=0)

# Display filtered reviews
# Display filtered reviews with increased table length
# Display filtered reviews with increased table width
st.write('Filtered Reviews:')
with st.dataframe(filtered_reviews.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1), height=800, width=1000):
    st.write(filtered_reviews)

# Plot bar graph
plt.figure(figsize=(8, 6))
plt.bar(rating_counts.index, rating_counts.values, color='skyblue')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Number of Reviews per Rating')
st.pyplot(plt)
