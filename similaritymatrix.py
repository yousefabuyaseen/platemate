import pandas as pd
from flask import Flask, render_template, request
import ast
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

london_data = pd.read_csv("/Users/yaseen/Documents/PMFYP/london_TA_data.csv")

def parse_cuisine_style(cuisine_style_str):
    if not pd.isna(cuisine_style_str):
        return re.findall(r'\w+', cuisine_style_str)
    else:
        return []

london_data['Cuisine Style'] = london_data['Cuisine Style'].apply(parse_cuisine_style)
london_data['Ranking'].fillna(london_data['Ranking'].mean(), inplace=True)
london_data['Rating'].fillna(london_data['Rating'].mean(), inplace=True)
london_data['Price Range'].fillna(london_data['Price Range'].mean(), inplace=True)

mlb = MultiLabelBinarizer()
cuisine_encoded = mlb.fit_transform(london_data['Cuisine Style'])

scaler = MinMaxScaler()
numeric_features = london_data[['Ranking', 'Rating', 'Price Range']]
numeric_features_scaled = scaler.fit_transform(numeric_features)

# Apply feature weights
cuisine_weight = 1.0
ranking_weight = 0.2
rating_weight = 0.3
price_range_weight = 0.1

weighted_feature_matrix = np.hstack([
    cuisine_weight * cuisine_encoded,
    ranking_weight * numeric_features_scaled[:, 0].reshape(-1, 1),
    rating_weight * numeric_features_scaled[:, 1].reshape(-1, 1),
    price_range_weight * numeric_features_scaled[:, 2].reshape(-1, 1),
])

cosine_sim = cosine_similarity(weighted_feature_matrix)

def get_recommendations(index, cosine_sim=cosine_sim, num_recommendations=10, similarity_threshold=0.6):
    sim_scores = list(enumerate(cosine_sim[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [score for score in sim_scores if score[1] > similarity_threshold]
    sim_scores = sim_scores[1:num_recommendations+1]

    restaurant_indices = [i[0] for i in sim_scores]
    restaurant_scores = [i[1] for i in sim_scores]
    recommendations = london_data.iloc[restaurant_indices][['Name']]
    recommendations['Similarity Score'] = restaurant_scores
    return recommendations

def get_index_by_name(restaurant_name):
    ratios = [fuzz.ratio(restaurant_name.lower(), name.lower()) for name in london_data['Name']]
    max_ratio = max(ratios)
    if max_ratio >= 80:
        return ratios.index(max_ratio)
    else:
        return None

restaurant_name = ""

while True:
    restaurant_name = input("Please enter a restaurant name (or type 'exit' to quit): \n")
    
    if restaurant_name.lower() == 'exit':
        break
    
    index = get_index_by_name(restaurant_name)
    if index is not None:
        recommended_restaurants = get_recommendations(index)
        print(recommended_restaurants)
    else:
        print("No match found for restaurant name:", restaurant_name)

if __name__ == '__main__':
    app.run(debug=True)
