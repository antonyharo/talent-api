from flask import Blueprint, jsonify, request
import os
import time
import google.generativeai as genai
from app.config import Config

# Configurar a API do Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

# Inicializar Blueprint
cv_bp = Blueprint("cv", __name__)

# Configuração do modelo
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


# Funções auxiliares
def upload_to_gemini(path, mime_type=None):
    """Envia o arquivo para o Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Arquivo enviado: '{file.display_name}' como: {file.uri}")
    return file


def wait_for_files_active(files):
    """Aguarda o processamento dos arquivos enviados para o Gemini."""
    print("Aguardando processamento dos arquivos...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"O arquivo {file.name} falhou no processamento.")
    print("...todos os arquivos estão prontos.")

@cv_bp.route("/", methods=["POST"])
def upload():
    # Verificar se o arquivo foi enviado
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Somente arquivos PDF são suportados."}), 400

    # Verificar se a descrição da vaga foi enviada
    job = request.form.get("job")
    if not job:
        return jsonify({"error": "A descrição da vaga é obrigatória."}), 400

    # Salvar o arquivo localmente
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    try:
        # Enviar para o Gemini
        gemini_file = upload_to_gemini(file_path, mime_type="application/pdf")

        # Esperar que o arquivo esteja ativo
        wait_for_files_active([gemini_file])

        # Iniciar a sessão de chat com o arquivo e a descrição da vaga
        chat_session = MODEL.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        gemini_file,
                        job,  # Passar a descrição da vaga como parte do contexto
                    ],
                },
            ]
        )

        # Enviar uma mensagem ao modelo
        response = chat_session.send_message(
            f"""
            **INSTRUÇÕES IMPORTANTES!**
            - Você é um analisador de currículos;
            - Use o bom senso e as melhores práticas críticas para fazer a análise do currículo;
            - Baseie sua análise na descrição da vaga a seguir: {job};
            - Seja claro e conciso nas suas palavras;
            - Determine pontos chave, críticos, positivos, negativos e que podem melhorar a respeito do currículo e do próprio candidato;
            - Em hipótese alguma forneça os cabeçalhos genéricos do tipo: 'Claro, está aqui a análise...', não transpareça nenhum tipo de traço que é um chatbot, apenas gere o que foi pedido;
            - Seja crítico e detalhista;
            - Forneça uma análise detalhada e em formato markdown com os tópicos devidamente separados.

            Conforme as instruções acima, gere uma análise crítica robusta, longa e detalhada do currículo anexado.
            No final de sua análise, construa uma tabela de pontos fortes, pontos fracos, diferencias e observações do currículo.
            """
        )

        return jsonify({"response": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
