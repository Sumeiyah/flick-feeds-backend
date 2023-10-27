from app import app, db, User, Movie, Post, Club, Membership, Follow, WatchedMovie, Comment, Like, Notification
import requests
import random

API_KEY = "c75ff8a0"
BASE_URL = "http://www.omdbapi.com/?apikey=" + API_KEY
NUM_MOVIES = 100

def fetch_movie_data(s):
    response = requests.get(BASE_URL + "&s=" + s)
    if response.status_code == 200:
        return response.json().get('Search', [])
    return []

def fetch_movie_data(search_term, page=1):
    response = requests.get(BASE_URL + "&s=" + search_term + "&page=" + str(page))
    if response.status_code == 200:
        return response.json().get('Search', [])
    return []

def create_movies():
    movies_added = 0
    current_page = 1
    while movies_added < 40:
        movies_data = fetch_movie_data("movie", current_page)
        for movie_data in movies_data:
            movie_details_response = requests.get(BASE_URL + "&i=" + movie_data['imdbID'])
            if movie_details_response.status_code == 200:
                movie_details = movie_details_response.json()
                movie = Movie(
                    Title=movie_details['Title'],
                    Genre=movie_details['Genre'],
                    Director=movie_details['Director'],
                    ReleaseYear=movie_details['Year'],
                    Synopsis=movie_details['Plot'],
                    ImagePath=movie_details['Poster']
                )
                db.session.add(movie)
                movies_added += 1
                if movies_added >= 40:
                    break
        current_page += 1
    db.session.commit()




def generate_unique_phone(starting=1234567890, step=1):
    while True:
        yield starting
        starting += step

phone_generator = generate_unique_phone()

def create_users():
    # Real people names
    names = ["Alice", "Bob", "Charlie", "Daisy", "Edward", "Fiona", "George", "Hannah", "Ivan", "Julia"]
    # Unique bios
    bios = ["Movie buff since 2000.", "Cinephile and critic.", "Watching movies is my escape.", 
            "Nothing better than a classic.", "Horror movies enthusiast.", "Always up for a movie night.",
            "Rom-coms are my jam.", "Passionate about filmmaking.", "Documentaries tell the best stories.",
            "Always in search of the next best flick."]

    # Placeholder image URLs
    image_urls = [
        "https://wallpapers.com/images/high/profile-picture-f67r1m9y562wdtin.webp",  # Placeholder image of a kitten
        "https://i.pinimg.com/736x/78/19/03/781903479f25950d913b5ba6a6da89ad.jpg",  # Placeholder image of a kitten
        "https://pxbar.com/wp-content/uploads/2023/08/instagram-girls-dp.jpg",  # Placeholder image of Nicolas Cage
        "https://pxbar.com/wp-content/uploads/2023/08/girls-instagram-dp.jpg",  # Another placeholder image of Nicolas Cage
        "https://pxbar.com/wp-content/uploads/2023/08/insta-dp-for-girls.jpg",  # Placeholder image of a bear
        "https://pxbar.com/wp-content/uploads/2023/08/dp-images-for-girls.jpg",  # Another placeholder image of a bear
        "https://pxbar.com/wp-content/uploads/2023/08/instagram-dp-for-girls.jpg",  # Placeholder image of a kitten
        "https://pxbar.com/wp-content/uploads/2023/08/instagram-dp-girl.jpg",  # Placeholder GIF of Nicolas Cage
        "https://pxbar.com/wp-content/uploads/2023/08/profile-picture-girl-girl-pic-for-instagram-profile.jpg",  # Placeholder image of a bear
        "https://pxbar.com/wp-content/uploads/2023/08/girl-photo-dp.jpg"   # Placeholder image of a kitten
    ]
    for i, name in enumerate(names):
        user = User(
            Username=name.lower(),
            Password='password',
            Email=f"{name.lower()}@example.com",
            ProfilePicture=image_urls[i],
            Bio=bios[i],
            ContactDetails=f"+1-{next(phone_generator)}"  # Using the phone generator to create unique phone numbers
        )
        db.session.add(user)
    db.session.commit()


import random

def create_posts():
    users = User.query.all()
    movies = Movie.query.all()
    
    # Sample set of reviews
    reviews = [
        "Loved this movie!",
        "It was alright, could've been better.",
        "Didn't really enjoy it.",
        "One of my favorites this year!",
        "Decent watch. Would recommend.",
        "Amazing storyline and cast.",
        "A bit disappointing, had higher expectations.",
        "Absolutely brilliant!",
        "Quite boring, unfortunately.",
        "An absolute masterpiece!"
    ]

    for user in users:
        for movie in movies:
            # Select a random review from the list
            random_review = random.choice(reviews)
            # Generate a random rating between 1 and 5
            random_rating = round(random.uniform(1, 5), 1)  # This generates a float between 1 and 5, rounded to 1 decimal place

            post = Post(
                UserID=user.UserID,
                MovieID=movie.MovieID,
                Review=random_review,
                Rating=random_rating,
                ImagePath=movie.ImagePath
            )
            db.session.add(post)
    db.session.commit()

def create_clubs():
    genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller']
    users = User.query.all()
    for genre in genres:
        club = Club(
            Name="{} Lovers Club".format(genre),
            Genre=genre,
            OwnerID=users[genres.index(genre)].UserID
        )
        db.session.add(club)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_users()
        create_movies()
        create_posts()
        create_clubs()
        
