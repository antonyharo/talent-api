import google.generativeai as genai
from app.config import Config


class GoogleGeminiClient:
    def __init__(self):
        # Configura a chave da API do Google Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)

        # Definir a configuração de geração
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # Inicializar o modelo de geração
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
        )

    def generate_response(self, message):
        try:
            # Iniciar o chat com o modelo
            chat_session = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [message],
                    },
                ]
            )

            # Enviar a mensagem e obter a resposta
            response = chat_session.send_message(message)
            return {"response": response.text}, 200

        except Exception as e:
            return {"error": str(e)}, 500
