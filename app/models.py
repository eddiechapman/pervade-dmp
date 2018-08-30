from time import time
import jwt
from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    awards = db.relationship('Award', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Award(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pi_name = db.Column(db.String(300))
    contact = db.Column(db.String(1000))
    pi_email = db.Column(db.String(128))
    organization = db.Column(db.String(1000))
    program = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    abstract = db.Column(db.Text)
    award_number = db.Column(db.Integer)
    title_pervasive_data = db.Column(db.Boolean, nullable=True)
    title_data_science = db.Column(db.Boolean, nullable=True)
    title_big_data = db.Column(db.Boolean, nullable=True)
    title_case_study = db.Column(db.Boolean, nullable=True)
    title_data_synonyms = db.Column(db.Text, nullable=True)
    title_not_relevant = db.Column(db.Boolean, nullable=True)
    abstract_pervasive_data = db.Column(db.Boolean, nullable=True)
    abstract_data_science = db.Column(db.Boolean, nullable=True)
    abstract_big_data = db.Column(db.Boolean, nullable=True)
    abstract_case_study = db.Column(db.Boolean, nullable=True)
    abstract_data_synonyms = db.Column(db.Text, nullable=True)
    abstract_not_relevant = db.Column(db.Boolean, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return '<Award id:{0}'.format(
            self.id
        )

