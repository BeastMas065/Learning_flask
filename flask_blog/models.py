from flask import current_app
from flask_blog import db, login_manager
from datetime import datetime ,timezone
from flask_login import UserMixin
from itsdangerous import TimedSerializer as serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,  primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), default = 'default.jpg', nullable = False)
    password = db.Column(db.String(60), nullable = False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, timer=180):
        s = serializer(current_app.config['SECRET_KEY'],)
        return s.dumps({'user_id' : self.id})
    
    @staticmethod
    def verify_token(token):
        s = serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=180)
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)      

    def __repr__(self):
        return f'user("{self.username}")'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    dateposted = db.Column(db.DateTime, nullable = False, default=lambda: datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
