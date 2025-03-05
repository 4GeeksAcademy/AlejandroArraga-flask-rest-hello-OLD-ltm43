"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, FavoritesPeople, FavoritesPlanets

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoints para People
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    results = list(map(lambda person: person.serialize(), people))
    return jsonify({"msg": "Lista de todos los personajes", "people": results}), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify({"msg": f"Información del personaje con ID {people_id}", "person": person.serialize()}), 200

# Endpoints para Planets
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    results = list(map(lambda planet: planet.serialize(), planets))
    return jsonify({"msg": "Lista de todos los planetas", "planets": results}), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get_or_404(planet_id)
    return jsonify({"msg": f"Información del planeta con ID {planet_id}", "planet": planet.serialize()}), 200

# Endpoints para Users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    results = list(map(lambda user: user.serialize(), users))
    return jsonify({"msg": "Lista de todos los usuarios", "users": results}), 200

# Endpoints para Favorites
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1 
    favorites_people = FavoritesPeople.query.filter_by(user_id=user_id).all()
    favorites_planets = FavoritesPlanets.query.filter_by(user_id=user_id).all()

    people_favorites = list(map(lambda fav: fav.people.serialize(), favorites_people))
    planets_favorites = list(map(lambda fav: fav.planet.serialize(), favorites_planets))

    return jsonify({
        "msg": f"Favoritos del usuario con ID {user_id}",
        "people_favorites": people_favorites,
        "planets_favorites": planets_favorites
    }), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_favorite(people_id):
    user_id = 1  
    new_favorite = FavoritesPeople(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": f"Personaje con ID {people_id} añadido a favoritos"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):
    user_id = 1  
    new_favorite = FavoritesPlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": f"Planeta con ID {planet_id} añadido a favoritos"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    user_id = 1  
    favorite = FavoritesPeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"msg": f"No se encontró el favorito con people_id {people_id}"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Personaje con ID {people_id} eliminado de favoritos"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    user_id = 1  
    favorite = FavoritesPlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": f"No se encontró el favorito con planet_id {planet_id}"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Planeta con ID {planet_id} eliminado de favoritos"}), 200

# Test endpoint
@app.route('/test', methods=['GET'])
def test():
    response_body = {
        "msg": "Esto es una prueba"
    }
    return jsonify(response_body), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)