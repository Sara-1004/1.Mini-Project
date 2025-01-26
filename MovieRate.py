import dash
from dash import dcc, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px

movies_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\movies.dat'
ratings_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\ratings.dat'
users_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\users.dat'

movies = {}
ratings = []
users = {}

with open(movies_file, 'r', encoding='ISO-8859-1') as f:
    for line in f:
        movie_id, title, genres = line.strip().split('::')
        genres_list = genres.split('|')
        movies[int(movie_id)] = {'title': title, 'genres': genres_list}

with open(ratings_file, 'r', encoding='ISO-8859-1') as f:
    for line in f:
        user_id, movie_id, rating, timestamp = line.strip().split('::')
        ratings.append((int(user_id), int(movie_id), float(rating)))

with open(users_file, 'r', encoding='ISO-8859-1') as f:
    for line in f:
        user_id, gender, age, occupation, zip_code = line.strip().split('::')
        users[int(user_id)] = {'gender': gender, 'age': int(age), 'occupation': occupation}

genre_ratings = {}
year_ratings = {}

for user_id, movie_id, rating in ratings:
    movie = movies[movie_id]
    for genre in movie['genres']:
        if genre not in genre_ratings:
            genre_ratings[genre] = {'count': 0, 'rating_sum': 0}
        genre_ratings[genre]['count'] += 1
        genre_ratings[genre]['rating_sum'] += rating

    year = movie['title'][-5:-1]
    if year not in year_ratings:
        year_ratings[year] = {'count': 0, 'rating_sum': 0}
    year_ratings[year]['count'] += 1
    year_ratings[year]['rating_sum'] += rating

gender_genre_count = {'M': {}, 'F': {}}
for user_id, movie_id, rating in ratings:
    user = users[user_id]
    gender = user['gender']
    movie = movies[movie_id]
    for genre in movie['genres']:
        if genre not in gender_genre_count[gender]:
            gender_genre_count[gender][genre] = 0
        gender_genre_count[gender][genre] += 1

heatmap_data = []
for user_id, movie_id, rating in ratings:
    user = users[user_id]
    gender = user['gender']
    movie = movies[movie_id]
    for genre in movie['genres']:
        heatmap_data.append([genre, rating, gender])

heatmap_df = pd.DataFrame(heatmap_data, columns=['Genre', 'Rating', 'Gender'])

app = dash.Dash(__name__)

dropdown_options = [
    {'label': 'Average Ratings by Genre', 'value': 'genre'},
    {'label': 'Average Ratings by Year', 'value': 'year'},
    {'label': 'Popular Genres by Gender', 'value': 'gender'},
    {'label': 'Heatmap: Genre vs Rating vs Gender', 'value': 'heatmap'}
]

app.layout = html.Div([
    html.H1("Movie Ratings Dashboard"),
    dcc.Dropdown(
        id='graph-dropdown',
        options=dropdown_options,
        value='genre',
        style={'width': '50%'}
    ),
    dcc.Graph(id='graph-container')
])

@app.callback(
    dash.dependencies.Output('graph-container', 'figure'),
    [dash.dependencies.Input('graph-dropdown', 'value')]
)
def update_graph(selected_value):
    if selected_value == 'genre':
        genres = list(genre_ratings.keys())
        avg_ratings = [genre_ratings[genre]['rating_sum'] / genre_ratings[genre]['count'] for genre in genres]

        figure = go.Figure(data=[go.Bar(
            x=genres, 
            y=avg_ratings, 
            marker_color='skyblue'
        )])
        figure.update_layout(
            title='Average Ratings by Genre',
            xaxis_title='Genres',
            yaxis_title='Average Rating',
            xaxis_tickangle=-45
        )

    elif selected_value == 'year':
        years = list(year_ratings.keys())
        avg_year_ratings = [year_ratings[year]['rating_sum'] / year_ratings[year]['count'] for year in years]

        figure = go.Figure(data=[go.Bar(
            x=years, 
            y=avg_year_ratings, 
            marker_color='lightgreen'
        )])
        figure.update_layout(
            title='Average Ratings by Year',
            xaxis_title='Year',
            yaxis_title='Average Rating',
            xaxis_tickangle=-45
        )

    elif selected_value == 'gender':
        male_genres = gender_genre_count['M']
        female_genres = gender_genre_count['F']

        male_genre_names = list(male_genres.keys())
        male_genre_counts = list(male_genres.values())
        female_genre_names = list(female_genres.keys())
        female_genre_counts = list(female_genres.values())

        x = np.arange(len(male_genre_names))

        figure = go.Figure(data=[
            go.Bar(x=x - 0.2, y=male_genre_counts, name='Male', marker_color='blue'),
            go.Bar(x=x + 0.2, y=female_genre_counts, name='Female', marker_color='orange')
        ])
        figure.update_layout(
            title='Popular Genres by Gender',
            xaxis_title='Genres',
            yaxis_title='Genre Count',
            xaxis=dict(tickmode='array', tickvals=x, ticktext=male_genre_names),
            barmode='group'
        )

    elif selected_value == 'heatmap':
        fig = px.density_heatmap(heatmap_df, x="Genre", y="Rating", color="Gender",
                                 category_orders={"Gender": ["M", "F"]},
                                 title="Heatmap: Genre vs Rating vs Gender")
        figure = fig

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)


