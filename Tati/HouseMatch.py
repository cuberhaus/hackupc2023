import numpy as np
import json
import pandas as pd
import ast


def extract_features(house):
    feat_list = []
    feat_list.append(house['city'])
    feat_list.append(house['neighborhood'])
    feat_list.append(house['region'])
    feat_list.append(house['price'])
    feat_list.append(house['square_meters'])
    feat_list.append(house['bedrooms'])
    feat_list.append(house['bathrooms'])

    # Style
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
    x = x[:-1]
    y = y[1][:-1]

    # Identify the categorical and numerical features
    categorical = np.array([True, True, True, True, True, False, False, False, False, False, False, False, False])
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

    # Edit None to be string
    df['r1r6_property'] = df['r1r6_property'].fillna(0)
    df['r1r6_kitchen'] = df['r1r6_kitchen'].fillna(0)
    df['r1r6_bathroom'] = df['r1r6_bathroom'].fillna(0)
    df['r1r6_interior'] = df['r1r6_interior'].fillna(0)
    df['style'] = df['style'].fillna("Not set")

    # Get just the columns we need
    clean_df = df[
        ['city', 'neighborhood', 'region', 'style', 'property_type', 'price', 'square_meters', 'bedrooms', 'bathrooms',
         'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom', 'r1r6_interior', 'images']]

    return clean_df


def range_vec(df):
    range_vec = df[['price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom',
                    'r1r6_interior']]
    return range_vec

def ponderate_attributes(my_preferences, new_info):
    preferences = []
    attributes = ['price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom',
                    'r1r6_interior']
    for attribute in attributes:
        preferences.append(my_preferences[attribute] * 0.8 + new_info[attribute] * 0.2)

    print(preferences)
    return preferences


def find_nearest(old_house, df):
    min_distance = -1
    dist_temp = -1
    new_house = None
    for house in df.iterrows():
        dist_temp = gower_distance(old_house, house)
        if dist_temp != 0.0:
            if dist_temp < min_distance or min_distance == -1:
                min_distance = dist_temp
                new_house = house[1]
    print('Minima distancia: ' + str(min_distance))

    return new_house


df = format_table()
ponderate_attributes(df.iloc[5][5:-1], df.iloc[4][5:-1])
