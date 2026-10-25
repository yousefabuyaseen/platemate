import pandas as pd

original_data = pd.read_csv("/Users/yaseen/Desktop/TA_restaurants_curated.csv")
london_data = original_data[original_data['City'] == 'London']

# Keep only the desired columns
london_data = london_data[['Name', 'City', 'Cuisine Style', 'Ranking', 'Rating', 'Price Range', 'Number of Reviews', 'Reviews', 'URL_TA', 'ID_TA']]

# Save the filtered data to a new CSV file
london_data.to_csv("london_TA_data.csv", index=False)
import pandas as pd

original_data = pd.read_csv("/Users/yaseen/Desktop/TA_restaurants_curated.csv")
london_data = original_data[original_data['City'] == 'London']

# Keep only the desired columns
london_data = london_data[['Name', 'City', 'Cuisine Style', 'Ranking', 'Rating', 'Price Range', 'Number of Reviews', 'Reviews', 'URL_TA', 'ID_TA']]

# Save the filtered data to a new CSV file
london_data.to_csv("london_TA_data.csv", index=False)

print(/Users/yaseen/Documents/PMFYP/london_TA_data.csv.shape)
