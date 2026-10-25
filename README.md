<div align="center">

<img src="static/logo-no-background.png" width="260" alt="PlateMate">

**A personalised restaurant recommendation engine for London.**

![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web%20app-000000?style=flat-square&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-cosine%20similarity-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Auth-FFCA28?style=flat-square&logo=firebase&logoColor=black)
![University of Westminster](https://img.shields.io/badge/University%20of%20Westminster-Final%20Year%20Project%202023-5B2C83?style=flat-square)

[Portfolio](https://www.yousef.studio/)

</div>

![PlateMate home page](screenshots/home.png)

## About

PlateMate was my final-year project at the University of Westminster (2023). Name a restaurant you love, or a cuisine, and
it recommends places across London that are genuinely similar. It doesn't just sort by star rating.

## How the recommendations work

1. **Data:** around 18,000 London restaurants from TripAdvisor (`london_TA_data.csv`), cleaned with `scraper.py`.
2. **Features:** cuisine styles are multi-hot encoded with `MultiLabelBinarizer`, and ranking, rating and price range are
   scaled with `MinMaxScaler`.
3. **Weighting:** the features are combined into one weighted matrix. Cuisine counts ×3, price ×2, and rating and ranking ×1,
   so "feels like the same kind of place" matters most.
4. **Similarity:** a **cosine similarity** matrix compares every restaurant with every other one.
5. **Search:** fuzzy matching (`fuzzywuzzy`) forgives typos in restaurant names. If no restaurant matches, PlateMate treats the
   search as a cuisine and returns the best-rated places for it.
6. **Results:** the nine closest restaurants, each with a similarity score, star rating, cuisine tags and a link to TripAdvisor.

![Top Picks results for "italian"](screenshots/top-picks.png)

## Features

- **Top Picks:** personalised recommendations with a similarity percentage
- **Find Restaurants:** search London restaurants on an interactive map
- **Accounts:** register, log in, reset your password, edit your profile and delete your account (Firebase Authentication)
- **Save restaurants** to your profile
- Light and dark mode

![Find Restaurants map](screenshots/find-restaurants.png)

## Project structure

```
app.py               Flask app: routes, auth and the recommendation engine
similaritymatrix.py  builds the feature matrix and cosine similarities
scraper.py           cleans and enriches the TripAdvisor data
platemate.py         data exploration and merging
templates/           Jinja pages (home, top picks, find restaurants, profile, auth)
static/              CSS, JavaScript and images
*.csv                restaurant datasets
```

## Run it

```bash
pip install -r requirements.txt
export FIREBASE_CREDENTIALS=/path/to/your-firebase-adminsdk.json   # Firebase Console → Service accounts
export FIREBASE_API_KEY=...       # Firebase Console → Project settings → your web app
export FIREBASE_APP_ID=...
export FIREBASE_SENDER_ID=...
python app.py
```

Then open http://localhost:5000. No keys are stored in this repo. They are all read from environment variables.
