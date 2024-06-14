from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import *

db_host = "localhost"

keycloak_host = "localhost"
realm_id = "myrealm"
client_id = "backend"
client_secret = "xcwOYqFbt3cPr39JLapu5Di6XTO8qQqk"

app = Flask(__name__)
CORS(app)

def create_db_engine():
    return create_engine(f"mariadb+pymysql://user:password@{db_host}:3306/database")
def validate_token(token):
    response = requests.post(
        f"http://localhost:8080/realms/{realm_id}/protocol/openid-connect/token/introspect",
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "token": token
        }
    ).json()
    return response.get("active")

@app.route("/", methods=["GET", "POST"])
def validate_token_route():
    data = request.json
    is_valid = validate_token(data["token"])
    return make_response(jsonify({"active": is_valid}), 200)

@app.route("/recipe/all", methods=["GET"])
def get_recipes():
    engine = create_db_engine()

    with Session(engine) as session:
        recipes = session.scalars(select(Recipe))

        result = []
        for recipe in recipes:
            result.append({})
            result[-1]["id"] = recipe.id
            result[-1]["title"] = recipe.title
            result[-1]["products"] = recipe.products
            result[-1]["cook_time_in_m"] = recipe.cook_time_in_m
            result[-1]["date_time"] = recipe.date_time

        session.commit()

    return make_response({
        "message": "Recipes was fetched successfully",
        "recipes": result
    }, 200)

@app.route("/recipe", methods=["POST"])
def add_recipe():
    data = request.json

    if 'token' not in data:
        return make_response(jsonify({"error": "Token is missing"}), 400)

    response = requests.post(f"http://{keycloak_host}:8080/realms/{realm_id}/protocol/openid-connect/token/introspect",
                            {
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "token": data["token"]
                            }
                            ).json()

    if not response["active"]:
        return make_response({"error": "Invalid token"}, 401)

    engine = create_db_engine()

    with Session(engine) as session:
        session.add(
            Recipe(
                title=data["title"],
                products=data["usedProducts"],
                cook_time_in_m=data["timeForCooking"]
            )
        )
        session.commit()

    return make_response({"message": "Recipe was added successfully"}, 200)

@app.route("/recipe/<int:recipe_id>/<string:token>", methods=["DELETE"])
def delete_recipe(recipe_id, token):
    response = requests.post(f"http://{keycloak_host}:8080/realms/{realm_id}/protocol/openid-connect/token/introspect", 
                            {
                                "client_id": client_id, 
                                "client_secret": client_secret, 
                                "token": token
                            }
                            ).json()

    if response["active"] == False:
        return make_response(jsonify({"error": "Invalid token"}), 401)
    
    engine = create_db_engine()

    with Session(engine) as session:
        recipe = session.scalar(select(Recipe).where(Recipe.id == recipe_id))

        if recipe is None:
            return make_response({"message": "Recipe not found"}, 404)

        session.delete(recipe)

        session.commit()

    return make_response({"message": "Note was deleted successfully"}, 200)

Recipe.metadata.create_all(create_db_engine())

if __name__ == "__main__":
    app.run(port=5002, host="0.0.0.0", debug=True)
