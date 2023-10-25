from flask_sqlalchemy import SQLAlchemy

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
    clubs_owned = db.relationship('Club', backref='owner')
    memberships = db.relationship('Membership', backref='member')
    movies_watched = db.relationship('WatchedMovie', backref='viewer')
    comments = db.relationship('Comment', backref='commenter')
    likes = db.relationship('Like', backref='liker')
    notifications = db.relationship('Notification', backref='receiver')

class Movie(db.Model):
    __tablename__ = 'movies'
    MovieID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Genre = db.Column(db.String(255))
    Director = db.Column(db.String(255))
    ReleaseYear = db.Column(db.Integer)
    Synopsis = db.Column(db.Text)

    posts = db.relationship('Post', backref='movie')
    watchers = db.relationship('WatchedMovie', backref='movie')

class Post(db.Model):
    __tablename__ = 'posts'
    PostID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    MovieID = db.Column(db.Integer, db.ForeignKey('movies.MovieID'), nullable=False)
    Review = db.Column(db.Text)
    Rating = db.Column(db.Float)

    comments = db.relationship('Comment', backref='post')
    likes = db.relationship('Like', backref='post')

class Club(db.Model):
    __tablename__ = 'clubs'
    ClubID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Genre = db.Column(db.String(255))
    OwnerID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)

    members = db.relationship('Membership', backref='club')

class Membership(db.Model):
    __tablename__ = 'memberships'
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)
    ClubID = db.Column(db.Integer, db.ForeignKey('clubs.ClubID'), primary_key=True)

class Follow(db.Model):
    __tablename__ = 'follows'
    FollowerID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)
    FolloweeID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)

class WatchedMovie(db.Model):
    __tablename__ = 'watched_movies'
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)
    MovieID = db.Column(db.Integer, db.ForeignKey('movies.MovieID'), primary_key=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    CommentID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CommentText = db.Column(db.Text)

class Like(db.Model):
    __tablename__ = 'likes'
    LikeID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    NotificationID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Content = db.Column(db.Text)
    IsRead = db.Column(db.Boolean, default=False)
