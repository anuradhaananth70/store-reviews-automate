import streamlit as st
import pandas as pd
import numpy as np
from google_play_scraper import app, Sort, reviews_all

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

# Streamlit UI
st.title('👥 PLaystore and App Store Review - Sentiment Analysis')

# Sidebar filters
st.sidebar.header('Filters')
min_rating = st.sidebar.selectbox('Minimum Rating', [1, 2, 3, 4, 5], index=0)
keyword = st.sidebar.text_input('Keyword in Review Description', '')

# Apply filters
filtered_reviews = reviews_data[(reviews_data['rating'] >= min_rating) &
                                (reviews_data['review_description'].str.contains(keyword, case=False))]

# Display filtered reviews
st.write('Filtered Reviews:')
with st.dataframe(filtered_reviews.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else 'background: lightgrey' for i in x], axis=1)):
    st.write(filtered_reviews)
