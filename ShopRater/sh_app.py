#!/bin/env python3

# All data processing libraries
import cdata.apachehbase as mod
import numpy as np
import pandas as pd
from scipy import stats

# All graphing libraries
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager

# All machine learning libraries
from sklearn import metrics
from sklearn import model_selection
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

import streamlit as st

'''
# Shopee Product Analytics

This is a tool to view item data that was mined from all Shopee categories.
The list of categories are available on the left and can be used to select the product category you would like to see.
'''


def load_df(cat):
    # Import e-commerce data
    # return pd.read_csv("data/mega.csv")
    cat = cat.replace("'", "''")
    conn = mod.connect("Server=[::1];Port=8080;")
    query = r"SELECT Item:Category as 'Category', Item:Label as 'Label', Item:Stars as 'Stars', Item:Ratings as 'Ratings', Item:Sold as 'Sold', Item:PriceMin as 'PriceMin', Item:PriceMax as 'PriceMax', Item:Stock as 'Stock', Seller:Name as 'Seller', Seller:Ratings as 'SellerRatings', Seller:Products as 'Products', Seller:ResponseRate as 'ResponseRate', Seller:ResponseTime as 'ResponseTime', Seller:Joined as 'Joined', Seller:Followers as 'Followers', Item:URL as 'URL', FROM Shopee_Items WHERE Item:Category = ('" + \
        cat + r"')"
    return pd.read_sql(query, conn)


df_cat = [r"Automotive", r"Baby & Toys", r"Cameras & Drones", r"Computer & Accessories", r"Fashion Accessories", r"Games, Books & Hobbies", r"Gaming & Consoles", r"Groceries & Pets", r"Health & Beauty", r"Home Appliances", r"Home & Living",
          r"Men's Bags & Wallets", r"Men's Clothing", r"Men's Shoes", r"Mobile & Gadgets", r"Muslim Fashion", r"Sports & Outdoor", r"Tickets & Vouchers", r"Travel & Luggage", r"Watches", r"Women's Bags", r"Women's Clothing", r"Women's Shoes", r"Others"]

option_df = st.sidebar.selectbox(
    'Choose the product category', df_cat)

df = load_df(option_df)

# Remove all non-latin characters from the label
df['Label'] = df['Label'].str.replace(r"[^a-zA-Z0-9_\s]+", " ").str.strip()

'''
# Rating prediction tool

This is a tool to perform training and testing of the selected product category.
Once the training has been completed, the accuracy score will be shown.
You could then input your own data to see the rating that would predicted if you had an item in this product category.

'''


def predict(df):
    # Perform normalization of the data
    df_ln = df.copy()

    # Prepare the data for learning by removing variables with non-numerical values
    df_ln.drop(['Category'], axis=1, inplace=True)
    df_ln.drop(['Label'], axis=1, inplace=True)
    df_ln.drop(['Seller'], axis=1, inplace=True)
    df_ln.drop(['ResponseTime'], axis=1, inplace=True)
    df_ln.drop(['Joined'], axis=1, inplace=True)
    df_ln.drop(['URL'], axis=1, inplace=True)
    # Get a data description of the normalized data set
    # st.table(df_ln.describe())

    # Break down the variables into X and Y, with Y being the expected outcome
    normalize = pd.DataFrame(preprocessing.normalize(df_ln))
    X = normalize.iloc[:, [1, 2, 3, 4, 6, 8, 9]].values
    y = normalize.iloc[:, [0]].values

    # Divide the data into 80% for training and 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)

    # Initialize the random forrest regressor for training
    rnd_f = RandomForestRegressor(n_estimators=200, random_state=0)

    # Fit the training data into the model for training
    rnd_f.fit(X_train, y_train.ravel())
    # We then perform the prediction using the test data
    pred_y = rnd_f.predict(X_test)

    # Print the prediction score or accuracy
    st.write("Prediction accuracy: " +
             str(round(metrics.r2_score(y_test, pred_y) * 100, 4)) + '%')

    sprice = st.text_input('Minimum Price (RM)', 10)
    bprice = st.text_input('Maximum Price (RM)', 50)
#    stock = st.text_input('Available Stock', 1000)
    sold = st.text_input('Stock Sold', 100)
    iratings = st.text_input('Item Ratings', 100)
    sratings = st.text_input('Seller Ratings', 100)
#    products = st.text_input('Product Calatog', 1000)
    sresponse = float(st.text_input('Seller Response Rate (%)', 90)) / 100.0
    followers = st.text_input('Followers', 5)

    sample = {'Ratings': [iratings],
              'Sold': [sold],
              'PriceMin': [sprice],
              'PriceMax': [bprice],
              # 'Stock': [stock],
              'SellerRatings': [sratings],
              # 'Products': [products],
              'ResponseRate': [sresponse],
              'Followers': [followers]}
    df_u = pd.DataFrame(sample)
    pred_u = rnd_f.predict(pd.DataFrame(preprocessing.normalize(df_u)))
    npv = (1 - pred_u[0]) * 5
    st.text("\nItem rating estimate (Stars): " + str(round(npv, 2)))


predict(df)

'''
# Product attributes analysis

This section provides typical analysis of the features for the data provided by this category.
We do some basic exploration of the data to view key statistics of the data series, including number of non-missing values, mean, standard deviation, min, max, and quantiles.
'''

if st.checkbox('Show data description'):
    '''
    View the first 10 rows of this dataset.
    '''
    st.write(df.head(10))
    '''
    Get a data description of the dataset for this category.
    '''
    st.write(df.describe())
    '''
    Identify attributes that contain null values
    '''
    st.text(df.isnull().sum())

# Remove the URL an ID field, since we do not need it
df.drop(['URL'], axis=1, inplace=True)

# Correlation analysis between attributes in the data set
df_corr = df.corr().stack().reset_index().rename(
    columns={0: 'correlation', 'level_0': 'Y', 'level_1': 'X'})
df_corr['correlation_label'] = df_corr['correlation'].map('{:.3f}'.format)

if st.checkbox('Show correlation sample'):
    '''
    The pairwise correlation of all attributes in the data set.
    '''
    st.table(df_corr.head())

# Visualize the correlation using a heat map
base = alt.Chart(df_corr).encode(
    x='X:O',
    y='Y:O'
)

# Text layer with correlation labels
# Colors are for easier readability
text = base.mark_text().encode(
    text='correlation_label',
    color=alt.condition(
        alt.datum.correlation > 0.5,
        alt.value('white'),
        alt.value('black')
    )
)

'''
Visualization of the correlation of features using a heat map. The magnitude of correlation between the attributes are strong.
'''
# The correlation heatmap itself
cor_plot = base.mark_rect().encode(
    color='correlation:Q'
)

# The '+' means overlaying the text and rect layer
st.altair_chart(cor_plot + text, use_container_width=True)

'''
Plots showing the distribution of data for each variable.
'''
# Histogram plots of all variables
df.hist(alpha=0.5, figsize=(15, 15))
plt.tight_layout()
st.pyplot()

'''
Plots showing the density of data for each variable.
'''
# Density plots of all variables
df.plot(kind='density', subplots=True, layout=(
    4, 3), sharex=False, figsize=(15, 15))
st.pyplot()

'''
Lastly, the box plots of the variables to see the outliers (extreme values) and concentration of the data.
'''
# Box plots of all variables
df.plot(kind='box', subplots=True, layout=(4, 3),
        sharex=False, sharey=False, figsize=(15, 15))
st.pyplot()
