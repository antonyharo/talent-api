import os
import time
from flask import Blueprint, jsonify, request
import google.generativeai as genai
from app.config import Config


# Configuração do Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

cv_analyzer_bp = Blueprint("cv_analyzer", __name__)

# Constantes de configuração
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


def create_upload_directory(directory: str = "uploads"):
    """Cria o diretório de uploads, se não existir."""
    os.makedirs(directory, exist_ok=True)


def save_uploaded_file(file, path: str):
    """Salva o arquivo enviado no caminho especificado."""
    file.save(path)


def is_valid_pdf(filename: str) -> bool:
    """Verifica se o arquivo é um PDF válido."""
    return filename.lower().endswith(".pdf")


def upload_to_gemini(path: str, mime_type: str = None):
    """Envia o arquivo para o Gemini."""
    return genai.upload_file(path, mime_type=mime_type)


def wait_for_file_processing(files):
    """Aguarda o processamento dos arquivos enviados para o Gemini."""
    for file in files:
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(file.name)
        if file.state.name != "ACTIVE":
            raise Exception(f"O arquivo {file.name} falhou no processamento.")


def generate_resume_analysis(job_description: str, gemini_file):
    """Gera a análise crítica do currículo com base na descrição da vaga."""
    chat_session = MODEL.start_chat(history=[{"role": "user", "parts": [gemini_file]}])

    response = chat_session.send_message(
        f"""
        **INSTRUÇÕES IMPORTANTES!**
        - Você é um analisador de currículos;
        - Use o bom senso e as melhores práticas críticas para fazer a análise do currículo;
        - Baseie sua análise na descrição da vaga a seguir: {job_description};
        - Seja claro e conciso nas suas palavras;
        - Determine pontos chave, críticos, positivos, negativos e que podem melhorar a respeito do currículo e do próprio candidato;
        - Em hipótese alguma forneça os cabeçalhos genéricos do tipo: 'Claro, está aqui a análise...', não transpareça nenhum tipo de traço que é um chatbot, apenas gere o que foi pedido;
        - Seja crítico e detalhista;
        - Forneça uma análise detalhada e em formato markdown com os tópicos devidamente separados.
        
        Conforme as instruções acima, gere uma análise crítica robusta, longa e detalhada do currículo anexado.
        No final de sua análise, construa uma tabela de pontos fortes, pontos fracos, diferencias e observações do currículo.
        """
    )

    return response.text


@cv_analyzer_bp.route("", methods=["POST"])
def upload():
    # Validação do arquivo
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    if not is_valid_pdf(file.filename):
        return jsonify({"error": "Somente arquivos PDF são suportados."}), 400

    # Validação da descrição da vaga
    job_description = request.form.get("job")
    if not job_description:
        return jsonify({"error": "A descrição da vaga é obrigatória."}), 400

    try:
        # Salva o arquivo no diretório de uploads
        create_upload_directory()
        file_path = os.path.join("uploads", file.filename)
        save_uploaded_file(file, file_path)

        # Envia o arquivo para o Gemini e aguarda o processamento
        gemini_file = upload_to_gemini(file_path, mime_type="application/pdf")
        wait_for_file_processing([gemini_file])

        # Gera a análise crítica do currículo
        analysis_response = generate_resume_analysis(job_description, gemini_file)

        return jsonify({"response": analysis_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
