
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    pass
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    
    recipes = db.relationship(
        'Recipe',
        backref='user',
        cascade='all, delete-orphan'
    )

    
    serialize_rules = ('-recipes.user',)

    
    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    
    @validates('username')
    def validate_username(self, key, value):
        if not value or value.strip() == '':
            raise ValueError("Username must be provided.")
        return value


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    
    serialize_rules = ('-user.recipes',)


    pass
    @validates('instructions') 
    def validate_instructions(self, key, value):
        if value is not None and len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value