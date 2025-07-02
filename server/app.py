#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    pass
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        errors = {}

        if not username:
            errors['username'] = ['Username is required.']

        if not password:
            errors['password'] = ['Password is required.']

        
        if errors:
            return {'errors': errors}, 422

        try:
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio,
            )
            new_user.password_hash = password

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return {
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {'errors': {'username': ['Username already taken.']}}, 422

        except ValueError as ve:
            return {'errors': {'validation': [str(ve)]}}, 422


class CheckSession(Resource):
    pass
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = db.session.get(User, user_id)  
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
            else:
                session.pop('user_id', None)

        return {'error': 'Unauthorized'}, 401
   
class Login(Resource):
    pass
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        
        user = db.session.query(User).filter_by(username=username).first()

        if user and user.authenticate(password):  
            session['user_id'] = user.id

            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200

        return {'error': 'Invalid username or password'}, 401
    
    

class Logout(Resource):
    pass
    def delete(self):
        user_id = session.get('user_id')

        if user_id is None:
            return {'error': 'Unauthorized'}, 401

        
        session.pop('user_id', None)
        return '', 204
   

class RecipeIndex(Resource):
    pass
    def get(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        return [
            {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            } for recipe in recipes
        ], 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes = data.get('minutes_to_complete')

        
        user = db.session.get(User, session['user_id'])

        try:
            new_recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes,
                user=user
            )

            db.session.add(new_recipe)
            db.session.commit()

            return {
                'id': new_recipe.id,
                'title': new_recipe.title,
                'instructions': new_recipe.instructions,
                'minutes_to_complete': new_recipe.minutes_to_complete,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
            }, 201

        except ValueError as ve:
            return { 'errors': { 'validation': [str(ve)] } }, 422

        except IntegrityError:
            db.session.rollback()
            return { 'errors': { 'database': ['Could not save recipe.'] } }, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)