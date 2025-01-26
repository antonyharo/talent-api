from flask import Blueprint, jsonify, request
from app.services.google_gemini import GoogleGeminiClient

jobs_comparator_bp = Blueprint("jobs_comparator", __name__)


@jobs_comparator_bp.route("", methods=["POST"])
def jobs_comparator():
    data = request.get_json()

    # Validação da entrada
    if not data or "jobs" not in data:
        return jsonify({"error": "O campo 'jobs' é obrigatório."}), 400

    jobs = data["jobs"]

    if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
        return (
            jsonify({"error": "O campo 'jobs' deve ser uma lista de objetos válidos."}),
            400,
        )

    # Formatar as vagas para a mensagem
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append(
            f"- Título: {job.get('title', 'Informação não disponível')}\n"
            f"  Descrição: {job.get('description', 'Informação não disponível')}\n"
            f"  Salário (opcional): {job.get('salary', 'Informação não disponível')}\n"
        )

    formatted_jobs_str = "\n\n".join(formatted_jobs)

    message = (
        "Você é uma IA especializada em análise e comparação de oportunidades de emprego. "
        "Analise as seguintes vagas:\n\n"
        f"{formatted_jobs_str}\n\n"
        "### Critérios de Avaliação:\n"
        "- **Crescimento e Desenvolvimento**: Planos de carreira, aprendizado, estabilidade na empresa.\n"
        "- **Cultura e Ambiente de Trabalho**: Alinhamento com valores pessoais, gestão, estilo de trabalho.\n"
        "- **Segurança e Condições**: Modelo de contrato, estabilidade e infraestrutura.\n"
        "- **Relevância na Carreira**: Contribuição para os objetivos profissionais a longo prazo.\n"
        "- **Intangíveis**: Desafios interessantes, impacto no estilo de vida, alinhamento com interesses pessoais.\n\n"
        "### Resultado:\n"
        "Organize as informações em uma tabela Markdown para facilitar a comparação. "
        "Use o seguinte formato como modelo para a tabela:\n"
        "| Coluna 1      | Coluna 2      | Coluna 3      |\n"
        "|---------------|---------------|---------------|\n"
        "| Valor 1       | Valor 2       | Valor 3       |\n"
        "| Outro valor 1 | Outro valor 2 | Outro valor 3 |\n\n"
        "Destaque os pontos fortes e fracos de cada vaga e sugira a melhor escolha com base nos critérios fornecidos."
    )

    # Instancia o cliente do Google Gemini
    gemini_client = GoogleGeminiClient()

    # Gera a resposta
    response = gemini_client.generate_response(message)

    return response
