from flask import Blueprint, jsonify, request
import google.generativeai as genai
from app.config import Config
import time
import os

cv_analyzer_bp = Blueprint("cv_analyzer", __name__)

genai.configure(api_key=Config.GEMINI_API_KEY)

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
    processed_files = []
    for file in files:
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(file.name)
        if file.state.name != "ACTIVE":
            raise Exception(f"O arquivo {file.name} falhou no processamento.")
        processed_files.append(file)
    return processed_files


@cv_analyzer_bp.route("", methods=["POST"])
def cv_analyzer():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    files = request.files.getlist("file")
    if not files:
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    if not all(is_valid_pdf(file.filename) for file in files):
        return jsonify({"error": "Todos os arquivos devem estar no formato PDF."}), 400

    try:
        create_upload_directory()
        file_paths = []

        # Salvar todos os arquivos localmente
        for file in files:
            file_path = os.path.join("uploads", file.filename)
            save_uploaded_file(file, file_path)
            file_paths.append(file_path)

        # Enviar os arquivos para o Gemini e aguardar processamento
        gemini_files = [
            upload_to_gemini(path, mime_type="application/pdf") for path in file_paths
        ]
        processed_files = wait_for_file_processing(gemini_files)

        # Criar sessão de chat com os arquivos
        chat_session = MODEL.start_chat(
            history=[{"role": "user", "parts": processed_files}]
        )

        response = chat_session.send_message(
            f"""
            **Contexto:**
            Você é uma Inteligência Artificial especializada em análise de currículos, projetada para avaliar candidatos com base exclusivamente nas informações fornecidas no currículo. Sua tarefa é identificar as qualificações e características de cada candidato, considerando aspectos como experiência profissional, habilidades técnicas e interpessoais, formação acadêmica, idiomas, conquistas, soft skills e alinhamento com a cultura organizacional. A análise deve ser realizada de forma criteriosa, independentemente do nível de detalhamento presente no currículo.

            **Instruções para Análise:**

            1. **Coleta e Processamento de Dados:**
            - **Experiência Profissional:** Extraia informações sobre tempo de atuação, setores, cargos e responsabilidades descritas no currículo. Caso haja informações limitadas, considere a ausência de detalhes como um dado relevante para a análise.
            - **Habilidades Técnicas e Interpessoais:** Identifique as competências técnicas e interpessoais mencionadas no currículo. Se essas competências não forem especificadas, registre a ausência como parte da análise.
            - **Formação Acadêmica e Certificações:** Verifique o nível de escolaridade, cursos complementares e certificações. Caso estas informações sejam incompletas ou ausentes, destaque isso na análise.
            - **Idiomas e Proficiência:** Extraia informações sobre idiomas e proficiência caso estejam presentes. A falta de menção a idiomas deve ser registrada como um dado relevante.
            - **Projetos e Conquistas:** Identifique quaisquer projetos ou conquistas mencionados, incluindo resultados tangíveis ou diferenciais. Se essas informações estiverem ausentes, isso deve ser considerado na avaliação.
            - **Soft Skills e Cultura Organizacional:** Avalie os aspectos relacionados a habilidades interpessoais, como liderança, comunicação e trabalho em equipe, com base nas informações fornecidas. A falta dessas informações deve ser registrada como uma lacuna na análise.

            2. **Análise dos Candidatos:**
            - **Resumo de Cada Perfil:** Forneça um resumo objetivo de cada candidato com base nas informações extraídas do currículo, destacando suas qualificações, pontos fortes e áreas de experiência.
            - **Lacunas e Oportunidades de Desenvolvimento:** Identifique quaisquer lacunas evidentes no currículo, como a ausência de informações sobre habilidades específicas, idiomas ou realizações. Registre essas ausências de forma objetiva.

            3. **Geração de Resultados:**
            - **Relatório Detalhado de Candidatos:** Apresente um relatório estruturado com a descrição das qualificações de cada candidato, incluindo pontos fortes, habilidades, experiências e lacunas identificadas.
            - **Tabela Markdown de Comparação:** Gere uma tabela Markdown que destaque as principais competências, experiência e formação de cada candidato.
            - **Insights Acionáveis:** Forneça insights sobre as forças e fraquezas de cada perfil, com base nas informações presentes no currículo.

            **Saída Esperada:**
            - Relatório com a **análise detalhada** de cada candidato
            - **Tabela Markdown** comparando as qualificações e informações extraídas dos currículos.
            - **Lacunas registradas** de forma objetiva, sem suposições, refletindo a ausência de informações.
            - **Sugestões de aprimoramento** com base nas informações fornecidas no currículo.
            """
        )

        return jsonify({"response": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
