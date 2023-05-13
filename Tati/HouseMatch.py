import numpy as np
import json
import pandas as pd
import ast


df = []
range_vec = []

def extract_features(house):
    feat_list = []
    feat_list.append(house['city'])
    feat_list.append(house['neighborhood'])
    feat_list.append(house['region'])
    feat_list.append(house['price'])
    feat_list.append(house['square_meters'])
    feat_list.append(house['bedrooms'])
    feat_list.append(house['bathrooms'])

    #Style
    feat_list.append(house['image_data']['style']['label'])
    feat_list.append(house['property_type'])

    feat_list.append(house['r1r6_property'])
    feat_list.append(house['r1r6_kitchen'])
    feat_list.append(house['r1r6_bathroom'])
    feat_list.append(house['r1r6_interior'])

# Define the Gower distance function
def gower_distance(x, y, weight=None):
    """
    Compute the Gower distance between two samples x and y.
    """

    # Identify the categorical and numerical features
    categorical = np.array([True, True, True, True, True, False, False, False, False, False, False, False, False, ])
    numerical = np.logical_not(categorical)

    # Compute the distance for the categorical features
    dist_cat = np.sum(x[categorical] != y[categorical]) / np.sum(categorical)

    # Compute the distance for the numerical features
    range_vec = x[numerical].max() - x[numerical].min()
    dist_num = np.sum(np.abs(x[numerical] - y[numerical]) / range_vec)

    # Combine the distances for the different feature types, using the optional weights
    if weight is None:
        weight = np.ones(len(x))
    dist = np.sum(weight * (categorical * dist_cat + numerical * dist_num)) / np.sum(weight)

    print(dist)
    return dist

# Add nested values as columns
def data_to_table():
    df = pd.read_json('../restbai/hackupc2023_restbai__dataset_sample.json')
    df = df.transpose()

    val_property = []
    val_kitchen = []
    val_bathroom = []
    val_interior = []
    val_style = []

    for row in df['image_data']:
        # print(row['r1r6']['property'])
        val_property.append(row['r1r6']['property'])
        val_kitchen.append(row['r1r6']['kitchen'])
        val_bathroom.append(row['r1r6']['bathroom'])
        val_interior.append(row['r1r6']['interior'])
        val_style.append(row['style']['label'])

    df['r1r6_property'] = val_property
    df['r1r6_kitchen'] = val_kitchen
    df['r1r6_bathroom'] = val_bathroom
    df['r1r6_interior'] = val_interior
    df['style'] = val_style


    df.to_csv('database.csv', index=False)

    return df

def format_table():
    # Add all relevant colums into the table
    df = data_to_table()

    #Edit None to be string
    df['r1r6_property'] = df['r1r6_property'].fillna(0)
    df['r1r6_kitchen'] = df['r1r6_kitchen'].fillna(0)
    df['r1r6_bathroom'] = df['r1r6_bathroom'].fillna(0)
    df['r1r6_interior'] = df['r1r6_interior'].fillna(0)
    df['style'] = df['style'].fillna("Not set")

    #Get just the columns we need
    clean_df = df[['city', 'neighborhood', 'region', 'style', 'property_type', 'price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom', 'r1r6_interior',]]

    #columns
    global range_vec
    range_vec = df[['price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom', 'r1r6_interior']]
    return clean_df

df = format_table()
gower_distance(df.iloc[3],df.iloc[3])

#format_table()