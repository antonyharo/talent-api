from flask import Blueprint, jsonify, request
from app.services.google_gemini import GoogleGeminiClient

ask_gemini_bp = Blueprint("ask_gemini", __name__)


@ask_gemini_bp.route("", methods=["POST"])
def upload():
    data = request.get_json()

    # Validação da entrada
    if not data or "message" not in data:
        return jsonify({"error": "O campo 'message' é obrigatório."}), 400

    message = data["message"]

    if not isinstance(message, str) or not message.strip():
        return (
            jsonify({"error": "O campo 'message' deve ser uma string não vazia."}),
            400,
        )

    try:
        # Instancia o cliente do Google Gemini
        gemini_client = GoogleGeminiClient()

        # Gera a resposta
        response = gemini_client.generate_response(message)

        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
