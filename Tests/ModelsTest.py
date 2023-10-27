
from Models import User, db
from Models import Movie
from Models import Post
from sqlite3 import IntegrityError


import pytest

class TestCodeUnderTest:

    # Creating a User object with valid input should successfully create a new user in the database
    def test_create_user_with_valid_input(self):
        user = User(Username='test_user', Password='password', Email='test@example.com')
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(Username='test_user').first() is not None

    # Creating a Movie object with valid input should successfully create a new movie in the database
    def test_create_movie_with_valid_input(self):
        movie = Movie(Title='test_movie', Genre='Action', Director='John Doe', ReleaseYear=2020)
        db.session.add(movie)
        db.session.commit()
        assert Movie.query.filter_by(Title='test_movie').first() is not None

    # Creating a Post object with valid input should successfully create a new post in the database
    def test_create_post_with_valid_input(self):
        user = User(Username='test_user', Password='password', Email='test@example.com')
        db.session.add(user)
        db.session.commit()
        post = Post(UserID=user.UserID, MovieID=1, Review='Great movie!', Rating=4.5)
        db.session.add(post)
        db.session.commit()
        assert Post.query.filter_by(Review='Great movie!').first() is not None

    # Creating a User object with a duplicate username should raise an IntegrityError
    def test_create_user_with_duplicate_username(self):
        user1 = User(Username='test_user', Password='password', Email='test1@example.com')
        db.session.add(user1)
        db.session.commit()
        user2 = User(Username='test_user', Password='password', Email='test2@example.com')
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()

    # Creating a User object with a duplicate email should raise an IntegrityError
    def test_create_user_with_duplicate_email(self):
        user1 = User(Username='test1_user', Password='password', Email='test@example.com')
        db.session.add(user1)
        db.session.commit()
        user2 = User(Username='test2_user', Password='password', Email='test@example.com')
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()

    