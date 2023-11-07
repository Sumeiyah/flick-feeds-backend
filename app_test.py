import pytest
from app import app
from Models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
# ... rest of your code ...


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

def test_register(client):
    with app.app_context():
        response = client.post('/register', json={
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test@email.com'
        })
        assert response.status_code == 201
        json_data = response.get_json()
        assert 'message' in json_data and json_data['message'] == 'Registration Successful!'
        assert 'access_token' in json_data  # Only check for the presence of the key

def test_login(client):
    with app.app_context():
        # Hash the password if necessary, e.g., using werkzeug.security.generate_password_hash
        hashed_password = generate_password_hash('test_password')
        
        user = User(Username='test_user', Password=hashed_password, Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })
        assert response.status_code == 200, f"Response body: {response.get_json()}"  # This will output the response body if the status code is not 200

def test_profile(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.flush()  # Flush the changes to assign the UserID
        db.session.commit()

        db.session.refresh(user)
        app.logger.info(f"Created user with Username: {user.Username}")

        # Use the Username to request the profile, not the UserID
        response = client.get(f'/profile/{user.Username}')
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.get_json()}"

def test_update_profile(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.put(f'/update_profile/{user.UserID}', json={
            'Username': 'updated_username'
        })
        assert response.status_code == 200
        assert response.get_json() == {'message': 'Profile updated successfully!'}



def test_post_movie(client):
    with app.app_context():
        # Create a new user and commit to the database
        password_hash = generate_password_hash('test_password')
        user = User(Username='test_user', Password=password_hash, Email='test@email.com')
        db.session.add(user)
        db.session.commit()
    
        # Verify the user exists and the password is correct (as a sanity check)
        created_user = User.query.filter_by(Username='test_user').first()
        assert created_user is not None, "User was not created."
        assert check_password_hash(created_user.Password, 'test_password'), "Password does not match."

        # Attempt to login the user
        login_response = client.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })

        if login_response.status_code != 200:
            print("Login failed:", login_response.get_json())

        assert login_response.status_code == 200, "Login failed: Incorrect status code returned"
        # Continue with the rest of the test      



def test_get_movies(client):
    with app.app_context():
        response = client.get('/movies')
        assert response.status_code == 200


import json
from werkzeug.security import generate_password_hash

def login(client, username, password):
    return client.post('/login', json={
        'username': username,
        'password': password
    })

def test_post_watched_movie(client):
    with app.app_context():
        # Create user and movie objects and commit to the database
        hashed_password = generate_password_hash('test_password')
        user = User(Username='test_user', Password=hashed_password, Email='test@email.com')
        db.session.add(user)
        db.session.flush()  # This will assign an ID without committing the transaction
        
        movie = Movie(Title='Test Movie', Genre='Test', Director='Director', ReleaseYear=2000, Synopsis='Synopsis', ImagePath='http://path/to/image')
        db.session.add(movie)
        db.session.flush()  # Same here for the movie
        
        # Commit the transaction after adding all objects
        db.session.commit()

        # Perform login and assert success
        response = login(client, 'test_user', 'test_password')
        assert response.status_code == 200
        access_token = json.loads(response.data)['access_token']

        # Send the POST request to track the watched movie
        response = client.post('/post_watched_movie', json={
            'movie_id': movie.MovieID,
            'user_id': user.UserID
        }, headers={'Authorization': f'Bearer {access_token}'})

        # Verify that the response is successful
        assert response.status_code == 200
        assert json.loads(response.data)['message'] == 'Post added successfully'

# Note: Adjust the authorization header as per your token-based authentication if needed.


def test_get_watched_movies(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.get(f'/watched_movies/{user.UserID}')
    assert response.status_code == 200

def test_create_club(client):
    with app.app_context():
        # Create a test user with a hashed password and commit to the database
        hashed_password = generate_password_hash('test_password')
        user = User(Username='test_user', Password=hashed_password, Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        # Perform login and check for successful login
        login_response = client.post('/login', json={'username': 'test_user', 'password': 'test_password'})
        assert login_response.status_code == 200

        # If using token-based authentication, extract the token from the login response
        login_data = login_response.get_json()
        access_token = login_data.get('access_token')

        # Attempt to create a club using the test client with the required headers
        response = client.post('/create_club', json={
            'club_name': 'Test Club',
            'genre': 'Drama',
            'owner_id': user.UserID
        }, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'  # Include the access token in the request headers
        })

        # Assert that the club was created successfully
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['message'] == 'Club "Test Club" created successfully!'


def test_join_clubs_by_genre(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()  # Commit the user so it gets an UserID

        club = Club(Name='Test Club', Genre='Drama', OwnerID=user.UserID)
        db.session.add(club)

        db.session.commit()


# Test: Get Posts
def test_get_posts(client):
    with app.app_context():
        response = client.get('/posts')
        assert response.status_code == 200
        # Additional assertions to check response data

# Test: Get User Posts

def test_get_user_posts(client):
    with app.app_context():
        # Create a test user
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        # Fetch posts for the created user
        response = client.get(f'/get_user_posts/{user.UserID}')
        
        # Assertions
        assert response.status_code == 200
        # If needed, add further assertions related to the response content


# Test: Get User Posts
def test_get_user_posts(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.get(f'/get_user_posts/{user.UserID}')
        assert response.status_code == 200


def test_follow_unfollow_user(client):
    with app.app_context():
        # Setup: Create two users
        user1 = User(Username='test_user1', Password='test_password1', Email='test1@email.com')
        user2 = User(Username='test_user2', Password='test_password2', Email='test2@email.com')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Mock user1 login by setting the session
        with client.session_transaction() as session:
            session['username'] = 'test_user1'

        # User1 follows User2
        client.post('/follow_user/{}'.format(user2.UserID))
        follow = Follow.query.filter_by(FollowerID=user1.UserID, FolloweeID=user2.UserID).first()
        assert follow is not None

        # User1 unfollows User2
        client.delete('/unfollow_user/{}'.format(user2.UserID))
        follow = Follow.query.filter_by(FollowerID=user1.UserID, FolloweeID=user2.UserID).first()
        assert follow is None

def test_user_followers(client):
    with app.app_context():
        # Setup: Create two users and one of them follows the other
        user1 = User(Username='test_user1', Password='test_password1', Email='test1@email.com')
        user2 = User(Username='test_user2', Password='test_password2', Email='test2@email.com')
        db.session.add_all([user1, user2])
        db.session.commit()

        follow = Follow(FollowerID=user1.UserID, FolloweeID=user2.UserID)
        db.session.add(follow)
        db.session.commit()

        response = client.get('/followers/test_user2')
        data = response.get_json()
        assert data['followers_count'] == 1

def test_user_following(client):
    with app.app_context():
        # Setup: Create two users and one of them follows the other
        user1 = User(Username='test_user1', Password='test_password1', Email='test1@email.com')
        user2 = User(Username='test_user2', Password='test_password2', Email='test2@email.com')
        db.session.add_all([user1, user2])
        db.session.commit()

        follow = Follow(FollowerID=user1.UserID, FolloweeID=user2.UserID)
        db.session.add(follow)
        db.session.commit()

        response = client.get('/following/test_user1')
        data = response.get_json()
        assert data['following_count'] == 1
