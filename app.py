from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# Initialize Flask app
app = Flask(__name__)

# Load and preprocess the dataset
df = pd.read_csv(r"data/spotify_songs.csv")
df.drop(columns=['acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                  'duration_ms', 'language', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness'], inplace=True)
data = df[['track_name', 'track_artist', 'lyrics', 'playlist_name']]

def combine_features(row):
    return str(row['track_name']) + ' ' + str(row['track_artist']) + ' ' + str(row['lyrics'])
data['combined_features'] = data.apply(combine_features, axis=1)

# Initialize TF-IDF Vectorizer and Nearest Neighbors model
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data['combined_features'])
nn_model = NearestNeighbors(metric='cosine', algorithm='brute')
nn_model.fit(tfidf_matrix)

def get_music_recommendations(track_name, n=8):
    input_vector = tfidf_vectorizer.transform([track_name])
    distances, indices = nn_model.kneighbors(input_vector, n_neighbors=n + 1)
    similar_tracks = data.iloc[indices.flatten()[1:]]
    return similar_tracks[['track_name', 'track_artist','lyrics']].to_dict(orient='records')

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    if request.method == 'POST':
        track_name = request.form.get('track_name')
        if track_name:
            recommendations = get_music_recommendations(track_name, n=5)
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
