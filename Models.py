from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    ProfilePicture = db.Column(db.String(255))
    Bio = db.Column(db.Text)
    ContactDetails = db.Column(db.String(255))

    posts = db.relationship('Post', backref='author')
    clubs_owned = db.relationship('Club', back_populates='owner', cascade='all, delete-orphan')  # Fixed
    memberships = db.relationship('Membership', back_populates='user')
    movies_watched = db.relationship('WatchedMovie', backref='viewer')
    comments = db.relationship('Comment', backref='commenter')
    likes = db.relationship('Like', backref='liker')
    notifications = db.relationship('Notification', backref='receiver')

club_movies = db.Table(
    'club_movies',
    db.Column('ClubID', db.Integer, db.ForeignKey('clubs.ClubID', ondelete="CASCADE"), primary_key=True),
    db.Column('MovieID', db.Integer, db.ForeignKey('movies.MovieID', ondelete="CASCADE"), primary_key=True)
)

class Movie(db.Model):
    __tablename__ = 'movies'
    MovieID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Genre = db.Column(db.String(255))
    Director = db.Column(db.String(255))
    ReleaseYear = db.Column(db.Integer)
    Synopsis = db.Column(db.Text)
    ImagePath = db.Column(db.String(255))

    posts = db.relationship('Post', backref='movie')
    watchers = db.relationship('WatchedMovie', backref='movie')

class Post(db.Model):
    __tablename__ = 'posts'
    PostID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_posts_users'), nullable=False)
    MovieID = db.Column(db.Integer, db.ForeignKey('movies.MovieID', name='fk_posts_movies'), nullable=False)
    Review = db.Column(db.Text)
    Rating = db.Column(db.Float)
    ImagePath = db.Column(db.String(255))

    comments = db.relationship('Comment', backref='post')
    likes = db.relationship('Like', backref='post')

class Club(db.Model):
    __tablename__ = 'clubs'
    ClubID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Genre = db.Column(db.String(255), nullable=False)
    OwnerID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_clubs_users'), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    Description = db.Column(db.Text, nullable=True)
    ImageURL = db.Column(db.String(255), nullable=True)

    # Relationships
    members = db.relationship('Membership', back_populates='club', cascade='all, delete-orphan')
    owner = db.relationship('User', back_populates='clubs_owned')  # Fixed relationship
    movies = db.relationship('Movie', secondary=club_movies, backref='clubs')  # Many-to-Many Relationship

    
class Membership(db.Model):
    __tablename__ = 'memberships'
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_memberships_users'), primary_key=True)
    ClubID = db.Column(db.Integer, db.ForeignKey('clubs.ClubID', name='fk_memberships_clubs'), primary_key=True)

    user = db.relationship('User', back_populates='memberships')
    club = db.relationship('Club', back_populates='members')

class Follow(db.Model):
    __tablename__ = 'follows'
    FollowerID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_follows_users_follower'), primary_key=True)
    FolloweeID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_follows_users_followee'), primary_key=True)
# Define association table BEFORE the Club and Movie models



class WatchedMovie(db.Model):
    __tablename__ = 'watched_movies'
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_watched_movies_users'), primary_key=True)
    MovieID = db.Column(db.Integer, db.ForeignKey('movies.MovieID', name='fk_watched_movies_movies'), primary_key=True)
    ImagePath = db.Column(db.String(255))

class Comment(db.Model):
    __tablename__ = 'comments'
    CommentID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID', name='fk_comments_posts'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_comments_users'), nullable=False)
    CommentText = db.Column(db.Text)

class Like(db.Model):
    __tablename__ = 'likes'
    LikeID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID', name='fk_likes_posts'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_likes_users'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    NotificationID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_notifications_users'), nullable=False)
    Content = db.Column(db.Text)
    IsRead = db.Column(db.Boolean, default=False)

class SharedPost(db.Model):
    __tablename__ = 'shared_posts'
    SharedPostID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_shared_posts_users'), nullable=False)
    OriginalPostID = db.Column(db.Integer, db.ForeignKey('posts.PostID', name='fk_shared_posts_posts'), nullable=False)

    user = db.relationship('User', backref='shared_posts')
    original_post = db.relationship('Post', backref='shared_by')

class PrivatePost(db.Model):
    __tablename__ = 'private_posts'
    PostID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_private_posts_users'), nullable=False)
    MovieID = db.Column(db.Integer, db.ForeignKey('movies.MovieID', name='fk_private_posts_movies'), nullable=False)
    Title = db.Column(db.String(255), nullable=False)
    Genre = db.Column(db.String(255))
    Director = db.Column(db.String(255))
    ReleaseYear = db.Column(db.Integer)
    Synopsis = db.Column(db.Text)
    ImagePath = db.Column(db.String(255))

    user = db.relationship('User', backref='private_posts')
    movie = db.relationship('Movie', backref='private_posts')
