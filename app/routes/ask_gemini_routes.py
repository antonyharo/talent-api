from flask import Blueprint, jsonify, request
import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

ask_gemini_bp = Blueprint("ask_gemini", __name__)

GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=GENERATION_CONFIG,
)


@ask_gemini_bp.route("/", methods=["POST"])
def upload():
    # Verifica se os dados estão no formato JSON
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "O campo 'message' é obrigatório."}), 400

    message = data["message"]

    try:
        chat_session = MODEL.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        message,
                    ],
                },
            ]
        )

        response = chat_session.send_message(message)

        return jsonify({"response": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
