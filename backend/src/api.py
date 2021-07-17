import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# Headers 
@app.after_request
def after_request(response):
    response.headers.add('Access-Conrool-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Conrool-Allow-Methods','PAST, PUT, PATCH, GET, OPTION')
    return response

# helpers
def drinks_short():
    drinks = Drink.query.all()
    all_drinks = [drink.short() for drink in drinks]
    return all_drinks

def drinks_long():

    drinks = Drink.query.all()
    all_drinks = [drink.long() for drink in drinks]
    return all_drinks

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():

    try:
        drinks = drinks_short()

    except:
        abort(404)

    return jsonify({
        'success': True,
        'drinks':drinks
        })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinsk_detail(jwt):

    try:
        drinks = drinks_long()

    except:
        abort(404)

    return jsonify({
        'success':True,
        'drinks': drinks,
        'status_code': 200
        }), 200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_driks(jwt):

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if (title is None) or (recipe is None):
        abort(400)

    try:
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.title = title
        new_drink.recipe = json.dumps(recipe)

        new_drink.insert()

        drink = [new_drink.long()]
        drinks = drinks_long()

        return jsonify({
            'success': True,
            'drinks': drink,
            'status_code':200,
            }), 200

    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, drink_id):

    if not drink_id:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if (title is None) and (recipe is None):
        abort(400)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        if title:
            drink.title = title
        if recipe:   
            drink.recipe = json.dumps(recipe)

        drink.update()

        drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drink,
            'status_code': 200
            }), 200
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):

    if not drink_id:
        abort(404)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'status_code': 200,
            'delete': drink_id
            }), 200
    except:
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error_handler(AuthError):
            return (jsonify(
                {
                    "error": AuthError.status_code,
                    "message": AuthError.error["description"],
                    "success": False,
                }
            ), AuthError.status_code,)

