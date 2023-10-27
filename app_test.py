import pytest
from app import app
from Models import *


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
        assert response.get_json() == {'message': 'Registration Successful!'}
        user = User.query.filter_by(Username='test_user').first()
        assert user is not None

def test_login(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })
        assert response.status_code == 200
        assert response.get_json() == {'message': 'Login Successful!'}

        response_invalid = client.post('/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        assert response_invalid.status_code == 401
        assert response_invalid.get_json() == {'message': 'Invalid Credentials!'}

def test_profile(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.get(f'/profile/{user.UserID}')
        assert response.status_code == 200
        assert response.get_json()['Username'] == 'test_user'

        response = client.get('/profile/test_user')
        assert response.status_code == 200
        assert response.get_json()['Username'] == 'test_user'

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
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        client.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })

        response = client.post('/post_movie', json={
            'movie_title': 'Test Movie',
            'Review': 'Great Movie!',
            'Rating': 5,
            'ImagePath': 'http://path/to/image'
        })
        assert response.status_code == 201
        assert response.get_json() == {'message': 'Movie posted successfully!'}

def test_get_movies(client):
    with app.app_context():
        response = client.get('/movies')
        assert response.status_code == 200

def test_track_movie(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        client.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })

        movie = Movie(Title='Test Movie')
        db.session.add(movie)
        db.session.commit()

        response = client.post('/add_watched_movie', json={'movie_id': movie.MovieID})
        assert response.status_code == 200
        assert response.get_json() == {'message': 'Movie added to watched movies successfully!'}

def test_post_watched_movie(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)

        movie = Movie(Title='Test Movie', Genre='Test', Director='Director', ReleaseYear=2000, Synopsis='Synopsis', ImagePath='http://path/to/image')
        db.session.add(movie)
        
        db.session.commit()

        client.post('/login', json={'username': 'test_user', 'password': 'test_password'})

        response = client.post('/post_watched_movie', json={
            'movie_id': movie.MovieID,
            'user_id': user.UserID
        })
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Post added successfully'}

def test_get_watched_movies(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        response = client.get(f'/watched_movies/{user.UserID}')
    assert response.status_code == 200

def test_create_club(client):
    with app.app_context():
        user = User(Username='test_user', Password='test_password', Email='test@email.com')
        db.session.add(user)
        db.session.commit()

        client.post('/login', json={'username': 'test_user', 'password': 'test_password'})

        response = client.post('/create_club', json={
            'club_name': 'Test Club',
            'genre': 'Drama',
            'owner_id': user.UserID
        })
    assert response.status_code == 201
    assert response.get_json() == {'message': 'Club "Test Club" created successfully!'}

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
