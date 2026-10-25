import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import logging
from pandas import DataFrame
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import exceptions
import requests
from bs4 import BeautifulSoup
from functools import wraps
from flask import request, redirect, url_for
from flask import session

# Setting up the Firebase Admin SDK
cred = credentials.Certificate(os.environ.get('FIREBASE_CREDENTIALS', 'firebase-adminsdk.json'))
firebase_admin.initialize_app(cred)
FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '')
FIREBASE_SENDER_ID = os.environ.get('FIREBASE_SENDER_ID', '')

def get_image_url(url_ta):
    base_url = "https://www.tripadvisor.com"
    full_url = base_url + url_ta
    response = requests.get(full_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tag = soup.find('img', {'class': 'basicImg'})
        if image_tag:
            return image_tag['src']
    return None

logging.basicConfig(filename='app.log', level=logging.DEBUG)


df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'london_TA_data.csv')) 

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)


@app.context_processor
def firebase_config():
    return dict(firebase_api_key=FIREBASE_API_KEY, firebase_app_id=FIREBASE_APP_ID, firebase_sender_id=FIREBASE_SENDER_ID)

users = {}  # In-memory user storage (not recommended for production)

# Extract unique cuisine types
cuisines = set()
for i in df['Cuisine Style']:
    if isinstance(i, list):
        cuisines.update([cuisine.strip() for cuisine in i])
sorted_cuisines = sorted(cuisines)


def parse_cuisine_style(cuisine_style_str):
    if not pd.isna(cuisine_style_str):
        return re.findall(r'\w+', cuisine_style_str)
    else:
        return []

df['Cuisine Style'] = df['Cuisine Style'].apply(parse_cuisine_style)
df['Ranking'].fillna(df['Ranking'].mean(), inplace=True)
df['Rating'].fillna(df['Rating'].mean(), inplace=True)

def rating_to_stars(rating):
    full_stars = int(rating)
    half_stars = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_stars

    return {
        "full_stars": full_stars,
        "half_stars": half_stars,
        "empty_stars": empty_stars,
    }



def convert_price_range(price_range):
    if price_range == '$':
        return 1
    elif price_range == '$$ - $$$':
        return 2
    elif price_range == '$$$$':
        return 3
    else:
        return None

df['Price Range'] = df['Price Range'].apply(convert_price_range)
df['Price Range'].fillna(df['Price Range'].mean(), inplace=True)

mlb = MultiLabelBinarizer()
cuisine_encoded = mlb.fit_transform(df['Cuisine Style'])
print("Cuisine Encoded contains NaN:", np.isnan(cuisine_encoded).any().any())

scaler = MinMaxScaler()
numeric_features = df[['Ranking', 'Rating', 'Price Range']].copy()

# Fill missing values with the mean
numeric_features['Ranking'] = numeric_features['Ranking'].fillna(numeric_features['Ranking'].mean())
numeric_features['Rating'] = numeric_features['Rating'].fillna(numeric_features['Rating'].mean())
numeric_features['Price Range'] = numeric_features['Price Range'].fillna(numeric_features['Price Range'].mean())

scaler = MinMaxScaler()

print(numeric_features[numeric_features.isna().any(axis=1)])

# Ensure no NaN values remain
assert not np.isnan(numeric_features).any().any(), "Numeric features still contain NaN values"

numeric_features_scaled = scaler.fit_transform(numeric_features)


cuisine_weight = 3
ranking_weight = 1
rating_weight = 1
price_range_weight = 2


assert not np.isnan(cuisine_encoded).any().any(), "Cuisine_encoded still contains NaN values"

weighted_feature_matrix = np.hstack([

    cuisine_weight * cuisine_encoded,
    ranking_weight * numeric_features_scaled[:, 0].reshape(-1, 1),
    rating_weight * numeric_features_scaled[:, 1].reshape(-1, 1),
    price_range_weight * numeric_features_scaled[:, 2].reshape(-1, 1),
])

cosine_sim = cosine_similarity(weighted_feature_matrix)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route called")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Email: {email}, Password: {password}")  # Debugging line

        data = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        verify_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
        response = requests.post(verify_url, data=data)
        print(f"Response status code: {response.status_code}")  # Debugging line

        if response.status_code == 200:
            user_data = response.json()
            uid = user_data['localId']
            id_token = user_data['idToken']
            session_cookie_duration = 60 * 60 * 24 * 14  # 14 days in seconds
            session_cookie = auth.create_session_cookie(id_token, expires_in=session_cookie_duration)
            session['session_cookie'] = session_cookie
            print("Session cookie: ", session_cookie)  # Debugging line
            session['user_id'] = uid
            next_url = request.args.get('next', url_for('myprofile'))
            print("Session cookie and user_id set:", session['session_cookie'], session['user_id'])
            return redirect(next_url)
        else:
            flash('Invalid email or password.')

    print("Render login template")  # Added print statement
    return render_template('login.html')





def check_authentication():
    print("Checking authentication...")  # Added print statement
    if 'user_id' in session:
        try:
            print("User_id found in session:", session['user_id'])
            decoded_claims = auth.verify_session_cookie(session['session_cookie'])
            print("Decoded claims: ", decoded_claims)  # Debugging line
            return True
        except (auth.InvalidSessionCookieError, ValueError) as e:
            print("Error: ", e)  # Debugging line
            return False
    print("Authentication failed.")  # Added print statement
    return False


@app.route('/store_user_id', methods=['GET', 'POST'])
def store_user_id():
    if request.method == 'POST':
        user_id = request.json['user_id']
        session['user_id'] = user_id
        return jsonify(success=True)

    user_id = request.args.get('user_id')
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('myprofile'))

    return jsonify(success=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Checking login...")  # Added print statement
        is_authenticated = check_authentication()
        if not is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not email or not username or not password or not confirm_password:
            flash('Please fill in all fields.')
        elif password != confirm_password:
            flash('Passwords do not match.')
        else:
            try:
                user = auth.create_user(
                    email=email,
                    display_name=username,
                    password=password,
                )
                flash('Registration successful. You can now log in.')
                return redirect(url_for('login'))
            except ValueError as e:
                flash('Invalid email format.')
                return render_template('register.html')
            except Exception as e:
                flash('An error occurred: {}'.format(e))
                return render_template('register.html')
    return render_template('register.html')



@app.route('/')
def home():
    return render_template('home.html')


def get_recommendations(index, cosine_sim=cosine_sim, num_recommendations=9, similarity_threshold=0.5):
    sim_scores = list(enumerate(cosine_sim[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [score for score in sim_scores if score[1] > similarity_threshold]
    sim_scores = sim_scores[1:num_recommendations+1]

    restaurant_indices = [i[0] for i in sim_scores]
    restaurant_scores = [round(i[1] * 100, 2) for i in sim_scores]  # Convert to percentages and round to 2 decimal places
    recommendations = df.iloc[restaurant_indices][['Name', 'URL_TA', 'Rating', 'Cuisine Style', 'ID_TA', 'Reviews']]  
    recommendations['Similarity Score'] = restaurant_scores
    return recommendations


def get_index_by_name(restaurant_name):
    ratios = [fuzz.ratio(restaurant_name.lower(), name.lower()) for name in df['Name']]
    max_ratio = max(ratios)
    if max_ratio >= 80:
        return ratios.index(max_ratio)
    else:
        return None



def get_top_cuisine_restaurants(cuisine, count=9):
    lower_cuisine = cuisine.lower()
    cuisine_restaurants = df[df['Cuisine Style'].apply(lambda x: any(lower_cuisine == item.lower() for item in x))]
    top_cuisine_restaurants = cuisine_restaurants.nlargest(count, 'Rating')
    return top_cuisine_restaurants

@app.route('/top_picks', methods=['GET', 'POST'])
@app.route('/top_picks', methods=['GET', 'POST'])
def top_picks():
    recommended_restaurants = pd.DataFrame()
    error = None
    idx = None  # Initialize idx as None
    if idx is not None:
        recommended_restaurants = get_recommendations(idx, num_recommendations=9)
        recommended_restaurants['Image URL'] = recommended_restaurants['URL_TA'].apply(get_image_url)
    if request.method == 'POST':
        search_term = request.form['search_term'].strip().lower()

        if search_term:
            idx = get_index_by_name(search_term)
            if idx is not None:
                recommended_restaurants = get_recommendations(idx, num_recommendations=9)
            else:
                top_cuisine_restaurants = get_top_cuisine_restaurants(search_term, count=9)
                if not top_cuisine_restaurants.empty:
                    recommended_restaurants = top_cuisine_restaurants
                else:
                    error = f"No restaurant named '{search_term}' or cuisine type '{search_term}' found. Please try another name or cuisine type."
        else:
            error = "Please provide a restaurant name or a cuisine type."

    return render_template('toppicks.html', recommended_restaurants=recommended_restaurants, error=error, cuisines=sorted_cuisines, rating_to_stars=rating_to_stars)





@app.route('/test_recommendations/<restaurant_name>')
def test_recommendations(restaurant_name):
    recommendations = get_recommendations(restaurant_name)
    return pd.DataFrame(recommendations).to_html() if recommendations else "No recommendations found."

@app.route('/find_restaurants', methods=['GET', 'POST'])
def find_restaurants():
    if request.method == 'POST':

        pass
    return render_template('findrestaurants.html')


@app.route('/myprofile')
def my_profile():
    return render_template('myprofile.html')


@app.route('/edit_profile')
def edit_profile():
    return render_template('editprofile.html')

@app.route('/delete_account')
def delete_account():
    return render_template('deleteaccount.html')


if __name__ == '__main__':
    app.run(debug=True)