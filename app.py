from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
from Models import *
from flask_jwt_extended import create_access_token
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from flask_migrate import Migrate
from flask import make_response
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity



app = Flask(__name__)
CORS(app,supports_credentials=True, origins=["http://localhost:3000","http://127.0.0.1:5000"], methods=['GET', 'POST', 'PATCH', 'DELETE','PUT','OPTIONS'], allow_headers=['Authorization', 'Content-Type', 'x-access-token'], expose_headers=['Authorization'])
app.config['SECRET_KEY'] = 'c9cb13901b374ed2b4d9735e0e0a5fde'
app.config['JWT_SECRET_KEY'] = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NzM1YWI0MTc4OTlhOWNmMWU3Y2I4YWE1NWEzOWZiMyIsInN1YiI6IjY1M2E3YzEzOGEwZTliMDE0ZTAxMDVkMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.sOUXsDXdzl34G4Vmhx59ToCqMpkOxFSfrsB8xcxGVEo'  
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zite.db'
migrate = Migrate(app, db)
db.init_app(app)



from flask import session
# Enable logging for all levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# Ensure Flask logs through the built-in WSGI server (stream handler)
if not app.debug:
    app.logger.info('Flask app running in Production Mode (logging enabled)')
# User Authentication and Profile Management

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if user already exists
    existing_user = User.query.filter_by(Username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(data['password'])

    new_user = User(
        Username=data['username'],
        Password=hashed_password,
        Email=data['email'],
        ProfilePicture='https://i.stack.imgur.com/34AD2.jpg',
        Bio="Hey there I'm a new Flick-Feeds user!"
    )

    db.session.add(new_user)
    db.session.commit()

    # Set the username in the session
    session['username'] = new_user.Username

    # Create a token for the new user
    access_token = create_access_token(identity=new_user.Username)

    return jsonify({
        'message': 'Registration Successful!',
        'access_token': access_token
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(Username=data['username']).first()
    
    if user and check_password_hash(user.Password, data['password']):
        # Set the username in the session
        session['username'] = user.Username

        # Generate token and return full user details
        access_token = create_access_token(identity=user.Username)

        # Log the success message and access token to the backend terminal
        app.logger.info(f"Login Successful for {user.Username}")
        app.logger.info(f"Access Token: {access_token}")

        return jsonify({
            'message': 'Login Successful!',
            'access_token': access_token,
            'user': {
                'UserID': user.UserID,
                'Username': user.Username,
                'Email': user.Email,
                'ProfilePicture': user.ProfilePicture,
                'Bio': user.Bio,
                'ContactDetails': user.ContactDetails
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid Credentials!'}), 401


@app.route('/current_user', methods=['GET', 'OPTIONS'])
def current_user():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, x-access-token'
        return response

    # Handle GET request here
    return "Current User Data"

@app.route('/protected_endpoint', methods=['GET'])
@jwt_required()  # Ensure the JWT is valid
def protected_endpoint():
    current_user = get_jwt_identity()  # Retrieve the username from the token
    user = User.query.filter_by(Username=current_user).first()

    if not user:
        return jsonify({"message": "User not found!"}), 404

    return jsonify({"message": f"Welcome, {user.Username}!"})


@app.route('/profile/<string:username>', methods=['GET'])
def profile_by_username(username):
    # View user profile by username route
    user = User.query.filter_by(Username=username).first()
    if user:
        return jsonify({
            'UserID': user.UserID,
            'Username': user.Username,
            'Email': user.Email,
            'ProfilePicture': user.ProfilePicture,
            'Bio': user.Bio,
            'ContactDetails': user.ContactDetails
            # Add other user attributes as needed
        }), 200
    return jsonify({'message': 'User not found!'}), 404


@app.route('/update_profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if user:
        data = request.get_json()
        
        # Update user attributes as needed
        user.Username = data.get('username', user.Username)
        user.Email = data.get('email', user.Email)
        user.ProfilePicture = data.get('profilePicture', user.ProfilePicture)
        user.Bio = data.get('bio', user.Bio)
        user.ContactDetails = data.get('contactDetails', user.ContactDetails)

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200
    else:
        return jsonify({'message': 'User not found!'}), 404
    
@app.route('/search_users', methods=['GET'])
@jwt_required()
def search_users():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'users': []}), 200

    users = User.query.filter(User.Username.ilike(f'%{query}%')).all()
    current_user = get_jwt_identity()
    current_user_obj = User.query.filter_by(Username=current_user).first()

    result = []
    for user in users:
        if user.Username != current_user:
            is_following = Follow.query.filter_by(FollowerID=current_user_obj.UserID, FolloweeID=user.UserID).first() is not None
            result.append({
                'UserID': user.UserID,
                'Username': user.Username,
                'ProfilePicture': user.ProfilePicture,
                'followers_count': Follow.query.filter_by(FolloweeID=user.UserID).count(),
                'is_following': is_following
            })
    return jsonify({'users': result}), 200



# Movies and Posts
@app.route('/post_movie', methods=['POST'])
def post_movie():
    # Post a watched movie route
    user = User.query.filter_by(Username=session['username']).first()
    if not user:
        return jsonify({'message': 'User not found or not logged in!'}), 401

    data = request.get_json()

    # Check for required fields
    required_fields = ['movie_title', 'Review', 'Rating', 'ImagePath']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Missing {field}'}), 400

    movie_title = data['movie_title']
    review = data['Review']
    rating = data['Rating']
    image_path = data['ImagePath'] if data['ImagePath'] else "https://w7.pngwing.com/pngs/116/765/png-transparent-clapperboard-computer-icons-film-movie-poster-angle-text-logo-thumbnail.png"

    # Check if the movie already exists in the database
    movie = Movie.query.filter_by(Title=movie_title).first()
    if not movie:
        # If the movie doesn't exist, create a new one with the provided ImagePath
        movie = Movie(
            Title=movie_title,
            ImagePath=image_path  # Set the ImagePath here
        )
        db.session.add(movie)
        db.session.flush()  # To get the generated MovieID for the new movie, if required.

    # Create the post
    post = Post(
        UserID=user.UserID,
        MovieID=movie.MovieID, 
        Review=review, 
        Rating=rating,
        ImagePath=image_path
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({'message': 'Movie posted successfully!'}), 201


@app.route('/movies', methods=['GET'])
def get_movies():
    # Get all movies route
    movies = Movie.query.all()
    movie_list = []

    for movie in movies:
        movie_data = {
            'MovieID': movie.MovieID,
            'Title': movie.Title,
            'Genre': movie.Genre,
            'Director': movie.Director,
            'ReleaseYear': movie.ReleaseYear,
            'Synopsis': movie.Synopsis,
            'ImagePath': movie.ImagePath
        }
        movie_list.append(movie_data)

    return jsonify({'movies': movie_list}), 200

# Track a Watched Movie
@app.route('/add_watched_movie', methods=['POST'])
def track_movie():
    # Track a watched movie route
    user = User.query.filter_by(Username=session['username']).first()
    if user:
        data = request.get_json()
        movie = Movie.query.get(data['movie_id'])  # Query the Movie entity by movie_id
        if not movie:
            return jsonify({'message': 'Movie not found!'}), 404
        # Use the image path from the queried movie
        image_path = movie.ImagePath
        watched_movie = WatchedMovie(UserID=user.UserID, MovieID=data['movie_id'], ImagePath=image_path)
        db.session.add(watched_movie)
        db.session.commit()
        return jsonify({'message': 'Movie added to watched movies successfully!'}), 200


@app.route('/post_watched_movie', methods=['POST'])
def add_watched_movie():
    # Add a watched movie as a post route
    if 'username' not in session:
        return jsonify({'message': 'You must be logged in to add watched movies as posts!'}), 401

    current_user = User.query.filter_by(Username=session['username']).first()
    if not current_user:
        return jsonify({'message': 'Current user not found!'}), 404

    data = request.get_json()
    movie_id = data.get('movie_id')
    user_id = data.get('user_id')

    # Check if the movie and user exist
    movie = Movie.query.get(movie_id)
    user = User.query.get(user_id)

    if not movie:
        return jsonify({'message': 'Movie not found!'}), 404

    if not user:
        return jsonify({'message': 'User not found!'}), 404
     
    # Create a new PrivatePost entry with the movie details
    post = PrivatePost(
        UserID=user.UserID,
        MovieID=movie.MovieID,
        Title=movie.Title,
        Genre=movie.Genre,
        Director=movie.Director,
        ReleaseYear=movie.ReleaseYear,
        Synopsis=movie.Synopsis,
        ImagePath=movie.ImagePath
    )

    # Commit the new post to the database
    db.session.add(post)
    db.session.commit()

    return jsonify({'message': 'Post added successfully'}), 200


@app.route('/watched_movies/<string:username>', methods=['GET'])
def get_watched_movies(username):
    # Check if the user exists
    user = User.query.filter_by(Username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    # Retrieve all watched movies for the user
    watched_movies = WatchedMovie.query.filter_by(UserID=user.UserID).all()

    # Serialize the watched movies to JSON
    watched_movies_data = []
    for watched_movie in watched_movies:
        movie_data = {
            'MovieID': watched_movie.MovieID,
            'Title': watched_movie.movie.Title,
            'Genre': watched_movie.movie.Genre,
            'Director': watched_movie.movie.Director,
            'ReleaseYear': watched_movie.movie.ReleaseYear,
            'Synopsis': watched_movie.movie.Synopsis,
            'ImagePath': watched_movie.ImagePath
        }
        watched_movies_data.append(movie_data)

    return jsonify({'watched_movies': watched_movies_data}), 200

# Movie Clubs

@app.route('/clubs', methods=['GET'])
def get_all_clubs():
    clubs = Club.query.all()

    genre_statements = {
        'Action': 'Welcome to the Action Club, where adrenaline never stops!',
        'Adventure': 'Embark on epic journeys with fellow adventurers!',
        'Comedy': 'Laugh out loud in the funniest club around!',
        'Drama': 'Dive deep into stories that stir your emotions.',
        'Fantasy': 'Enter a world of magic, myths, and legends!',
        'Horror': 'Welcome to Horror, your spookiest of clubs!',
        'Mystery': 'Solve mysteries and uncover hidden secrets here.',
        'Romance': 'Find love in the sweetest stories of the Romance Club!',
        'Sci-Fi': 'Explore futuristic worlds and cutting-edge science fiction!',
        'Thriller': 'Keep your heart racing with thrilling adventures!'
    }

    clubs_data = []
    for club in clubs:
        # Use the `user` attribute to fetch member information
        members = [{'UserID': member.UserID, 'Username': member.user.Username} 
                   for member in club.members]

        club_data = {
            'ClubID': club.ClubID,
            'Name': club.Name,
            'Genre': club.Genre,
            'OwnerUsername': club.owner.Username if club.owner else 'Unknown',
            'CreatedAt': club.CreatedAt.strftime('%Y-%m-%d') if club.CreatedAt else 'Unknown',
            'Description': genre_statements.get(club.Genre, 'Welcome to your club!'),
            'Members': members  # Corrected members list
        }
        clubs_data.append(club_data)

    return jsonify({'clubs': clubs_data}), 200



@app.route('/user_clubs/<string:username>', methods=['GET'])
def get_user_clubs(username):
    user = User.query.filter_by(Username=username).first()

    if not user:
        return jsonify({'message': 'User not found!'}), 404

    user_clubs = (db.session.query(Club)
                  .join(Membership, Membership.ClubID == Club.ClubID)
                  .filter(Membership.UserID == user.UserID)
                  .all())

    genre_statements = {
        'Action': 'Welcome to the Action Club, where adrenaline never stops!',
        'Adventure': 'Embark on epic journeys with fellow adventurers!',
        'Comedy': 'Laugh out loud in the funniest club around!',
        'Drama': 'Dive deep into stories that stir your emotions.',
        'Fantasy': 'Enter a world of magic, myths, and legends!',
        'Horror': 'Welcome to Horror, your spookiest of clubs!',
        'Mystery': 'Solve mysteries and uncover hidden secrets here.',
        'Romance': 'Find love in the sweetest stories of the Romance Club!',
        'Sci-Fi': 'Explore futuristic worlds and cutting-edge science fiction!',
        'Thriller': 'Keep your heart racing with thrilling adventures!'
    }

    clubs_data = []
    for club in user_clubs:
        members = [{'UserID': member.UserID, 'Username': member.member.Username} 
                   for member in club.members]

        club_data = {
            'ClubID': club.ClubID,
            'Name': club.Name,
            'Genre': club.Genre,
            'OwnerUsername': club.owner.Username,
            'Description': genre_statements.get(club.Genre, 'Welcome to your club!'),
            'Members': members
        }
        clubs_data.append(club_data)

    return jsonify({'clubs': clubs_data}), 200




@app.route('/create_club', methods=['POST'])
@jwt_required()
def create_club():
    username = get_jwt_identity()
    user = User.query.filter_by(Username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid data format!'}), 400

    # Check if club already exists
    existing_club = Club.query.filter_by(Name=data['club_name']).first()
    if existing_club:
        return jsonify({'message': 'Club already exists!'}), 400

    # Use the provided description, or set a default
    description = data.get('description') or f"A new club for {data['genre']} lovers!"

    club = Club(
        Name=data['club_name'],
        Genre=data['genre'],
        OwnerID=user.UserID,
        Description=description  # Save the description here
    )
    db.session.add(club)
    db.session.commit()

    # Automatically make the creator a member of the club
    membership = Membership(UserID=user.UserID, ClubID=club.ClubID)
    db.session.add(membership)
    db.session.commit()

    return jsonify({'message': f'Club "{data["club_name"]}" created successfully!'}), 201



@app.route('/join_clubs_by_genre/<string:genre>', methods=['POST'])
def join_clubs_by_genre(genre):
    # Join movie clubs by genre route
    user = User.query.filter_by(Username=session['username']).first()
    if user:
        clubs = Club.query.filter_by(Genre=genre).all()
        if clubs:
            for club in clubs:
                existing_membership = Membership.query.filter_by(UserID=user.UserID, ClubID=club.ClubID).first()
                if existing_membership:
                    # Membership already exists for this user and club, skip it
                    continue
                
                membership = Membership(UserID=user.UserID, ClubID=club.ClubID)
                db.session.add(membership)
            
            db.session.commit()
            return jsonify({'message': f'Joined {len(clubs)} clubs in the {genre} genre successfully!'}), 200
        else:
            return jsonify({'message': f'No clubs found in the {genre} genre.'}), 404
    else:
        return jsonify({'message': 'User not found!'}), 404

@app.route('/join_club/<int:club_id>', methods=['POST'])
@jwt_required()
def join_club(club_id):
    username = get_jwt_identity()  # Get the logged-in user's username from the JWT
    user = User.query.filter_by(Username=username).first()
    if user:
        # Check if user is already a member
        existing_membership = Membership.query.filter_by(UserID=user.UserID, ClubID=club_id).first()
        if existing_membership:
            return jsonify({'message': 'You are already a member of this club!'}), 400

        membership = Membership(UserID=user.UserID, ClubID=club_id)
        db.session.add(membership)
        db.session.commit()
        return jsonify({'message': 'Joined club successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404

from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/leave_club/<int:club_id>', methods=['DELETE'])
@jwt_required()  # Ensures the route is protected
def leave_club(club_id):
    # Get the current user from the JWT token
    current_user = get_jwt_identity()
    
    # Fetch the user from the database
    user = User.query.filter_by(Username=current_user).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    # Verify if the user is a member of the specified club
    membership = Membership.query.filter_by(UserID=user.UserID, ClubID=club_id).first()
    if not membership:
        return jsonify({'message': 'You are not a member of this club!'}), 403

    # Remove membership
    db.session.delete(membership)
    db.session.commit()

    # Check if the club still has any members
    remaining_members = Membership.query.filter_by(ClubID=club_id).count()
    if remaining_members == 0:
        # If no members left, delete the club
        club = Club.query.get(club_id)
        db.session.delete(club)
        db.session.commit()
        return jsonify({'message': 'You left the club, and it has been deleted since no members remain.'}), 200

    return jsonify({'message': 'You have successfully left the club!'}), 200
@app.route('/delete_club/<int:club_id>', methods=['DELETE'])
@jwt_required()
def delete_club(club_id):
    username = get_jwt_identity()
    user = User.query.filter_by(Username=username).first()

    club = Club.query.filter_by(ClubID=club_id).first()
    if club.OwnerID != user.UserID:
        return jsonify({'message': 'Unauthorized to delete this club'}), 403

    db.session.delete(club)
    db.session.commit()
    return jsonify({'message': 'Club deleted successfully!'}), 200




# Posts and Interactions

@app.route('/posts', methods=['GET'])
def get_posts():
    # Get all posts route
    posts = Post.query.all()
    post_list = []
    for post in posts:
        # Serialize comments including the username of the commenter
        comments_list = []
        for comment in post.comments:
            user = User.query.filter_by(UserID=comment.UserID).first()
            if user:
                comments_list.append({
                    'Username': user.Username,
                    'CommentText': comment.CommentText
                      # Fetch the Username from the User model
                })

        # Count the number of likes for the post
        likes_count = len(post.likes)

         # Fetch the post author's username
        author = User.query.filter_by(UserID=post.UserID).first()
        
        # Serialize the post data including the comments and likes count
        post_data = {
            'PostID': post.PostID,
            'UserID': post.UserID,
            'Author': author.Username if author else 'Unknown',
            'MovieID': post.MovieID,
            'Review': post.Review,
            'Rating': post.Rating,
            'ImagePath': post.ImagePath,
            'Comments': comments_list,
            'Likes': likes_count
        }
        post_list.append(post_data)
        
    return jsonify({'posts': post_list}), 200



@app.route('/get_user_posts/<string:username>', methods=['GET'])
def get_user_posts(username):
    # Get posts and shared posts from a specific user
    user = User.query.filter_by(Username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    # Retrieve all original posts by the user
    posts = Post.query.filter_by(UserID=user.UserID).all()

    # Retrieve all shared posts by the user
    shared_posts = SharedPost.query.filter_by(UserID=user.UserID).all()

    post_list = []

    # Process original posts
    for post in posts:
        movie = Movie.query.get(post.MovieID)
        post_data = {
            'PostID': post.PostID,
            'UserID': post.UserID,
            'MovieID': post.MovieID,
            'Title': movie.Title if movie else 'Unknown',
            'Review': post.Review,
            'Rating': post.Rating,
            'ImagePath': post.ImagePath,
            'Author': {
                'UserID': user.UserID,
                'Username': user.Username,
                'ProfilePicture': user.ProfilePicture
            }
        }
        post_list.append(post_data)

    # Process shared posts
    for shared in shared_posts:
        original_post = Post.query.get(shared.OriginalPostID)
        if original_post:
            movie = Movie.query.get(original_post.MovieID)
            shared_post_data = {
                'PostID': shared.SharedPostID,
                'OriginalPostID': shared.OriginalPostID,
                'UserID': shared.UserID,
                'MovieID': original_post.MovieID,
                'Title': movie.Title if movie else 'Unknown',
                'Review': original_post.Review,
                'Rating': original_post.Rating,
                'ImagePath': original_post.ImagePath,
                'Author': {
                    'UserID': original_post.author.UserID,
                    'Username': original_post.author.Username,
                    'ProfilePicture': original_post.author.ProfilePicture
                }
            }
            post_list.append(shared_post_data)

    return jsonify({'posts': post_list}), 200



@app.route('/share_post/<int:post_id>', methods=['GET', 'POST'])
def share_post(post_id):
    # Share a post route
    if request.method == 'GET':
        # Fetch the post by its ID
        post = Post.query.get(post_id)

        if post:
            # Prepare the detailed post information
            post_info = {
                'PostID': post.PostID,
                'Review': post.Review,
                'Rating': post.Rating,
                'ImagePath': post.ImagePath,
                'Author': {
                    'UserID': post.author.UserID,
                    'Username': post.author.Username,
                    'ProfilePicture': post.author.ProfilePicture
                },
                'Movie': None,
                'Comments': [],
                'Likes': []
            }

            # If the post is related to a movie, include movie information
            if post.movie:
                post_info['Movie'] = {
                    'MovieID': post.movie.MovieID,
                    'Title': post.movie.Title,
                    'Genre': post.movie.Genre,
                    'Director': post.movie.Director,
                    'ReleaseYear': post.movie.ReleaseYear,
                    'Synopsis': post.movie.Synopsis,
                    'ImagePath': post.movie.ImagePath
                }

            # Fetch and include comments and likes associated with the post
            comments = Comment.query.filter_by(PostID=post.PostID).all()
            likes = Like.query.filter_by(PostID=post.PostID).all()

            for comment in comments:
                post_info['Comments'].append({
                    'CommentID': comment.CommentID,
                    'CommentText': comment.CommentText,
                    'Commenter': {
                        'UserID': comment.commenter.UserID,
                        'Username': comment.commenter.Username
                    }
                })

            for like in likes:
                post_info['Likes'].append({
                    'LikeID': like.LikeID,
                    'Liker': {
                        'UserID': like.liker.UserID,
                        'Username': like.liker.Username
                    }
                })

            return jsonify(post_info), 200

        return jsonify({'message': 'Post not found!'}), 404

    elif request.method == 'POST':
        # Check if the user is authenticated
        if 'username' not in session:
            return jsonify({'message': 'You must be logged in to share posts!'}), 401

    user = User.query.filter_by(Username=session['username']).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    # Check if the post with the specified post_id exists
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    # Create a new shared post for the user with all columns of the original post
    shared_post = SharedPost(
        UserID=user.UserID,
        OriginalPostID=post.PostID  # Link the shared post to the original post
    )
    db.session.add(shared_post)
    db.session.commit()

    # Include all columns from the original post in the response
    shared_post_info = {
        'SharedPostID': shared_post.SharedPostID,
        'UserID': shared_post.UserID,
        'OriginalPostID': shared_post.OriginalPostID,
        # Include other columns from the original post here
        'Review': post.Review,
        'Rating': post.Rating,
        'ImagePath': post.ImagePath,
        'Author': {
            'UserID': post.author.UserID,
            'Username': post.author.Username,
            'ProfilePicture': post.author.ProfilePicture
        },
        'Movie': None,
        'Comments': [],
        'Likes': []
    }

    # If the post is related to a movie, include movie information
    if post.movie:
        shared_post_info['Movie'] = {
            'MovieID': post.movie.MovieID,
            'Title': post.movie.Title,
            'Genre': post.movie.Genre,
            'Director': post.movie.Director,
            'ReleaseYear': post.movie.ReleaseYear,
            'Synopsis': post.movie.Synopsis,
            'ImagePath': post.movie.ImagePath
        }

    # Fetch and include comments and likes associated with the original post
    comments = Comment.query.filter_by(PostID=post.PostID).all()
    likes = Like.query.filter_by(PostID=post.PostID).all()

    for comment in comments:
        shared_post_info['Comments'].append({
            'CommentID': comment.CommentID,
            'CommentText': comment.CommentText,
            'Commenter': {
                'UserID': comment.commenter.UserID,
                'Username': comment.commenter.Username
            }
        })

    for like in likes:
        shared_post_info['Likes'].append({
            'LikeID': like.LikeID,
            'Liker': {
                'UserID': like.liker.UserID,
                'Username': like.liker.Username
            }
        })

    return jsonify(shared_post_info), 201

# Like a Post
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    # Like a post route
    if 'username' in session:
        user = User.query.filter_by(Username=session['username']).first()
        if user:
            post = Post.query.get(post_id)
            if post:
                like = Like(PostID=post.PostID, UserID=user.UserID)
                db.session.add(like)
                db.session.commit()
                return jsonify({'message': 'Liked post successfully!'}), 200
            return jsonify({'message': 'Post not found!'}), 404
        return jsonify({'message': 'User not found!'}), 404
    else:
        return jsonify({'message': 'You must be logged in to like a post!'}), 401

# Comment on a Post
@app.route('/comment_on_post/<int:post_id>', methods=['POST'])
def comment_on_post(post_id):
    # Comment on a post route
    if 'username' in session:
        user = User.query.filter_by(Username=session['username']).first()
        if user:
            data = request.get_json()
            comment = Comment(PostID=post_id, UserID=user.UserID, CommentText=data['comment_text'])
            db.session.add(comment)
            db.session.commit()
            return jsonify({'message': 'Commented successfully!'}), 200
        return jsonify({'message': 'User not found!'}), 404
    else:
        return jsonify({'message': 'You must be logged in to comment!'}), 401



@app.route('/follow_user/<int:followee_id>', methods=['POST'])
@jwt_required()
def follow_user(followee_id):
    username = get_jwt_identity()  # Get logged-in user's username
    user = User.query.filter_by(Username=username).first()

    # Validate current user and prevent self-following
    if not user or user.UserID == followee_id:
        return jsonify({'message': "You can't follow yourself or invalid user."}), 400

    followee = User.query.get(followee_id)  # Ensure followee exists
    if not followee:
        return jsonify({'message': 'User to follow does not exist.'}), 404

    existing_follow = Follow.query.filter_by(FollowerID=user.UserID, FolloweeID=followee_id).first()
    if existing_follow:
        return jsonify({'message': 'You are already following this user.'}), 400

    # Create new follow relationship
    follow = Follow(FollowerID=user.UserID, FolloweeID=followee_id)
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'Followed successfully!'}), 200



# Unfollow a user
@app.route('/unfollow_user/<int:followee_id>', methods=['DELETE'])
@jwt_required()
def unfollow_user(followee_id):
    username = get_jwt_identity()
    user = User.query.filter_by(Username=username).first()

    # Validate current user
    if not user:
        return jsonify({'message': 'Unauthorized action.'}), 401

    follow = Follow.query.filter_by(FollowerID=user.UserID, FolloweeID=followee_id).first()
    if not follow:
        return jsonify({'message': 'You are not following this user.'}), 404

    # Delete follow relationship
    db.session.delete(follow)
    db.session.commit()
    return jsonify({'message': 'Unfollowed successfully!'}), 200



# Get followers count
@app.route('/followers/<string:username>', methods=['GET'])
def followers_count(username):
    user = User.query.filter_by(Username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    count = db.session.query(func.count(Follow.FollowerID)).filter(Follow.FolloweeID == user.UserID).scalar()
    return jsonify({'followers_count': count}), 200


# Get following count
@app.route('/following/<string:username>', methods=['GET'])
def following_count(username):
    user = User.query.filter_by(Username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    count = db.session.query(func.count(Follow.FolloweeID)).filter(Follow.FollowerID == user.UserID).scalar()
    return jsonify({'following_count': count}), 200

@app.route('/follow_status/<int:followee_id>', methods=['GET'])
@jwt_required()
def follow_status(followee_id):
    username = get_jwt_identity()  # Extract username from JWT
    user = User.query.filter_by(Username=username).first()
    
    if user:
        is_following = Follow.query.filter_by(FollowerID=user.UserID, FolloweeID=followee_id).first() is not None
        return jsonify({"is_following": is_following}), 200
    
    return jsonify({"error": "Unauthorized!"}), 401



if __name__ == '__main__':
    app.run(debug=True)
