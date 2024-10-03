from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id: int) -> 'User':
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    password = db.Column(db.String(64))
    profile_image = db.Column(db.String(20), default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)
    likes = db.relationship('Like', backref='author', lazy='dynamic')
 
    def like_post(self, post: 'Post') -> None:
        if not self.has_liked_post(post):
            like = Like(author_id=self.id, post_id=post.id)
    
    def unlike_post(self, post: 'Post') -> None:
        if self.has_liked_post(post):
            Like.query.filter_by(author_id=self.id, post_id=post.id).delete()
        
    def has_liked_post(self, post: 'Post') -> bool:
        return Like.query.filter(Like.author_id == self.id, Like.post_id == post.id).count() > 0

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rent = db.Column(db.String(100))
    location = db.Column(db.String(200))
    status = db.Column(db.String(200), nullable=False)
    furnishes = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    whatsapp = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.String(100), nullable=False)
    bathrooms = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100))
    outside_features = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.Date, index=True, default=datetime.utcnow().date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return '{}'.format(self.id)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self) -> str:
        return '<Like {}>'.format(self.body)


def init_db() -> None:
    db.create_all()


if __name__ == '__main__':
    init_db()
