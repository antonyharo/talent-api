from flask import Blueprint, jsonify

hello_world_bp = Blueprint("hello_world", __name__)


@hello_world_bp.route("/", methods=["GET"])
def upload():
    try:
        return jsonify({"response": "Hello, World!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
