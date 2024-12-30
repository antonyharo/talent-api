from flask import Blueprint, jsonify, request

user_bp = Blueprint("user", __name__)

@user_bp.route("/", methods=["GET"])
def get_users():
    return jsonify({"message": "List of users"})

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    return jsonify({"message": "User created", "data": data}), 201
