import pandas as pd
import csv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

# Load the merged DataFrame
merged_df = pd.read_csv("/Users/yaseen/Documents/PMFYP/merged_data.csv")

# Drop unnecessary columns
features = merged_df.drop(
    ['Borough', 'Lng_x', 'Lat_x', 'Lng_y', 'Lat_y', 'Area'], axis=1)

# Encode categorical columns
le = LabelEncoder()
features['category'] = le.fit_transform(features['category'])
features['categori'] = le.fit_transform(features['categori'])
features['name_y'] = le.fit_transform(features['name_y'])

# One-hot encode the encoded columns
onehot = OneHotEncoder(sparse=False)
encoded_cols = onehot.fit_transform(
    features[['category', 'categori', 'name_y']])
encoded_cols_df = pd.DataFrame(encoded_cols, columns=onehot.get_feature_names_out([
                               'category', 'categori', 'name_y']))

# Drop original encoded columns and replace with one-hot encoded columns
features = features.drop(['category', 'categori', 'name_y'], axis=1)
features = pd.concat([features, encoded_cols_df], axis=1)

# Compute the cosine similarity matrix
cosine_sim = cosine_similarity(features)

# Examine the cosine similarity matrix
print(cosine_sim)


with open('/Users/yaseen/Documents/PMFYP/top_100.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] == 'Newham':
            print(row)

# Load CSV files
london_df = pd.read_csv("/Users/yaseen/Documents/PMFYP/London_df.csv")
top_100 = pd.read_csv("/Users/yaseen/Documents/PMFYP/top_100.csv")
venues_df = pd.read_csv("/Users/yaseen/Documents/PMFYP/venues_df.csv")

# Merge the DataFrames
merged_df = pd.merge(london_df, top_100, on='Borough')
merged_df = pd.merge(merged_df, venues_df, on='Borough')

# Export the merged DataFrame as a CSV file
merged_df.to_csv("/Users/yaseen/Documents/PMFYP/merged_data.csv", index=False)

# Examine the merged DataFrame
print("\nMerged DataFrame:")
print(merged_df.head())

# Obtain basic information about the merged DataFrame
print("\nMerged DataFrame Info:")
print(merged_df.info())

