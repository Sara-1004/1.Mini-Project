movies_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\movies.dat'
ratings_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\ratings.dat'
users_file = r'C:\Users\Admin\Documents\ml-1m[1]\ml-1m\users.dat'

# Initialize dictionaries to store data
movies = {}
user_data = {}
ratings_data = {}
with open(movies_file, 'r') as f:
    for line in f:
        movie_id, title, genres = line.strip().split('::')
        movies[int(movie_id)] = genres.split('|')
with open(users_file, 'r') as f:
    for line in f:
        user_id, gender, age, occupation, zip_code = line.strip().split('::')
        user_data[int(user_id)] = {'gender': gender, 'age': age, 'occupation': occupation}
with open(ratings_file, 'r') as f:
    for line in f:
        user_id, movie_id, rating, timestamp = map(int, line.strip().split('::'))
        if movie_id not in ratings_data:
            ratings_data[movie_id] = {'ratings': [], 'user_ids': []}
        ratings_data[movie_id]['ratings'].append(rating)
        ratings_data[movie_id]['user_ids'].append(user_id)

genre_rating_count = {}
genre_rating_sum = {}
genre_movie_count = {}
for movie_id, movie_info in ratings_data.items():
    avg_rating = sum(movie_info['ratings']) / len(movie_info['ratings'])
    for genre in movies[movie_id]:
        if genre not in genre_rating_count:
            genre_rating_count[genre] = 0
            genre_rating_sum[genre] = 0
            genre_movie_count[genre] = 0
        genre_rating_count[genre] += 1
        genre_rating_sum[genre] += avg_rating
        genre_movie_count[genre] += 1

# Calculate average rating per genre
genre_avg_rating = {genre: genre_rating_sum[genre] / genre_rating_count[genre] for genre in genre_rating_count}

#most popular genres by user demographics
age_groups = {1: 'Under 18', 18: '18-24', 25: '25-34', 35: '35-44', 45: '45-49', 50: '50-55', 56: '56+'}
occupation_groups = {
    1: 'academic/educator', 2: 'artist', 3: 'clerical/admin', 4: 'college/grad student', 
    5: 'customer service', 6: 'doctor/health care', 7: 'executive/managerial', 8: 'farmer', 
    9: 'homemaker', 10: 'K-12 student', 11: 'lawyer', 12: 'programmer', 13: 'retired', 
    14: 'sales/marketing', 15: 'scientist', 16: 'self-employed', 17: 'technician/engineer', 
    18: 'tradesman/craftsman', 19: 'unemployed', 20: 'writer'
}

# Group ratings by age and occupation
age_group_ratings = {}
occupation_group_ratings = {}

for user_id, user_info in user_data.items():
    user_age_group = age_groups.get(int(user_info['age']), 'Unknown')
    user_occupation = occupation_groups.get(int(user_info['occupation']), 'Unknown')
    
    for movie_id, movie_info in ratings_data.items():
        if user_id in movie_info['user_ids']:
            for genre in movies[movie_id]:
                if user_age_group not in age_group_ratings:
                    age_group_ratings[user_age_group] = {genre: 0 for genre in movies[movie_id]}
                if user_occupation not in occupation_group_ratings:
                    occupation_group_ratings[user_occupation] = {genre: 0 for genre in movies[movie_id]}
                
                age_group_ratings[user_age_group][genre] += 1
                occupation_group_ratings[user_occupation][genre] += 1

import matplotlib.pyplot as plt
import seaborn as sns

# Plot Genre Rating Distribution
plt.figure(figsize=(10, 6))
sns.barplot(x=list(genre_avg_rating.keys()), y=list(genre_avg_rating.values()))
plt.title("Average Rating by Genre")
plt.xticks(rotation=45)
plt.xlabel("Genre")
plt.ylabel("Average Rating")
plt.show()

# Plot Popular Genres by Age Group
age_group_genres = {age: sum(age_group_ratings[age].values()) for age in age_group_ratings}
plt.figure(figsize=(10, 6))
sns.barplot(x=list(age_group_genres.keys()), y=list(age_group_genres.values()))
plt.title("Popular Genres by Age Group")
plt.xticks(rotation=45)
plt.xlabel("Age Group")
plt.ylabel("Number of Ratings")
plt.show()

# Heatmap: Correlation between Genre and User Activity (Age Group and Occupation)
genre_data_for_heatmap = []
for age_group in age_group_ratings:
    genre_data_for_heatmap.append(list(age_group_ratings[age_group].values()))
    
plt.figure(figsize=(12, 8))
sns.heatmap(genre_data_for_heatmap, annot=True, cmap="coolwarm", xticklabels=movies.keys(), yticklabels=age_group_ratings.keys())
plt.title("Correlation between Genre, User Activity, and Ratings")
plt.show()
