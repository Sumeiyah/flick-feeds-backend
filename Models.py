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
    Genre = db.Column(db.String(255))
    OwnerID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_clubs_users'), nullable=False)

    members = db.relationship('Membership', backref='club')

class Membership(db.Model):
    __tablename__ = 'memberships'
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_memberships_users'), primary_key=True)
    ClubID = db.Column(db.Integer, db.ForeignKey('clubs.ClubID', name='fk_memberships_clubs'), primary_key=True)

class Follow(db.Model):
    __tablename__ = 'follows'
    FollowerID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_follows_users_follower'), primary_key=True)
    FolloweeID = db.Column(db.Integer, db.ForeignKey('users.UserID', name='fk_follows_users_followee'), primary_key=True)

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

