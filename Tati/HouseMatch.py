import numpy as np
import json
import pandas as pd
import ast

f = open('../restbai/hackupc2023_restbai__dataset_sample.json', encoding='utf-8')
data = json.load(f)

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

    #R1R6
    feat_list.append(house['image_data']['r1r6']['property'])
    feat_list.append(house['image_data']['r1r6']['kitchen'])
    feat_list.append(house['image_data']['r1r6']['bathroom'])
    feat_list.append(house['image_data']['r1r6']['interior'])

    #Style
    feat_list.append(house['image_data']['style']['label'])
    feat_list.append(house['property_type'])

    print(feat_list)

# Define the Gower distance function
def gower_distance(x, y, weight=None):
    """
    Compute the Gower distance between two samples x and y.
    """

    x = extract_features(x)
    y = extract_features(y)

    # Identify the categorical and numerical features
    categorical = np.array([True, True, True, False, False, False, False, False, False, False, False, True, True])
    numerical = np.logical_not(categorical)

    # Compute the distance for the categorical features
    dist_cat = np.sum(x[categorical] != y[categorical]) / np.sum(categorical)

    # Compute the distance for the numerical features
    dist_num = np.sum(np.abs(x[numerical] - y[numerical]) / range_vec[numerical])

    # Combine the distances for the different feature types, using the optional weights
    if weight is None:
        weight = np.ones(len(x))
    dist = np.sum(weight * (categorical * dist_cat + numerical * dist_num)) / np.sum(weight)

    print(dist)

    return dist


def data_to_table():
    df = pd.read_json('../restbai/hackupc2023_restbai__dataset_sample.json')
    df = df.transpose()

    val_property = []
    val_kitchen = []
    val_bathroom = []
    val_interior = []

    for row in df['image_data']:
        # print(row['r1r6']['property'])
        val_property.append(row['r1r6']['property'])
        val_kitchen.append(row['r1r6']['kitchen'])
        val_bathroom.append(row['r1r6']['bathroom'])
        val_interior.append(row['r1r6']['interior'])

    df['r1r6_property'] = val_property
    df['r1r6_kitchen'] = val_kitchen
    df['r1r6_bathroom'] = val_bathroom
    df['r1r6_interior'] = val_interior

    df.to_csv('database.csv', index=False)

    return df

def format_table():
    df = data_to_table()
    df['r1r6_property'] = df['r1r6_property'].fillna("Not set")
    df['r1r6_kitchen'] = df['r1r6_kitchen'].fillna("Not set")
    df['r1r6_bathroom'] = df['r1r6_bathroom'].fillna("Not set")
    df['r1r6_interior'] = df['r1r6_interior'].fillna("Not set")
    range_vec = df[['price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom', 'r1r6_interior']]
    print(range_vec)

gower_distance(data['303464'], data['303464'])
#format_table()