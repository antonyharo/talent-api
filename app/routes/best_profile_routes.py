from flask import Blueprint, jsonify, request
from app.services.google_gemini import GoogleGeminiClient

best_profile_bp = Blueprint("best_profile", __name__)


@best_profile_bp.route("", methods=["POST"])
def best_profile():
    try:
        data = request.get_json()

        # Validação da entrada
        if not data or not isinstance(data, dict):
            return (
                jsonify({"error": "Os dados enviados devem estar no formato JSON."}),
                400,
            )

        job = data.get("job")
        if not job or not isinstance(job, dict):
            return (
                jsonify({"error": "O campo 'job' é obrigatório e deve ser um objeto."}),
                400,
            )

        # Obtendo dados da vaga com valores padrão para evitar erros
        job_title = job.get("title", "Nome Desconhecido")
        job_level = job.get("level", "Nível Desconhecido")
        job_sector = job.get("sector", "Setor Desconhecido")
        job_description = job.get("description", "Descrição Desconhecida")
        job_salary = job.get("salary", "Faixa Salarial Indisponível")

        # Construção da mensagem para a IA
        message = f"""
        *Você é um especialista que gera perfis de candidatos ideias para oportunidades de emprego.*
        *"Quero que você crie o perfil do candidato ideal para uma vaga de emprego. Aqui estão os detalhes que eu tenho:"*  

        - **Nome da vaga**: {job_title}  
        - **Nível do cargo**: {job_level}  
        - **Setor da vaga**: {job_sector}   
        - **Descrição da vaga**: {job_description}
        - **Faixa salarial**: {job_salary}  

        *"Se algum dos dados acima estiver incompleto, incorreto ou ausente, preencha as lacunas com informações típicas para esse tipo de cargo. Com base nesses dados, crie um candidato ideal, incluindo:"*  

        1. **Nome fictício e um breve resumo do perfil** (como se fosse a introdução de um currículo)  
        2. **Formação acadêmica** (graduação, pós-graduação, certificações relevantes – se não houver detalhes, sugira as mais comuns para o cargo)  
        3. **Experiência profissional** (cargos anteriores, empresas onde trabalhou, tempo de experiência – use referências típicas se os dados estiverem ausentes)  
        4. **Habilidades técnicas (Hard Skills)** (ferramentas, linguagens, metodologias – baseadas na vaga ou no que é comum para esse cargo)  
        5. **Habilidades comportamentais (Soft Skills)** (trabalho em equipe, liderança, criatividade – se não especificado, escolha as mais valorizadas no setor)  
        6. **Idiomas e outras competências diferenciais** (se não informado, sugerir baseando-se no mercado)  
        7. **Fit cultural** (como o candidato se encaixa nos valores e cultura da empresa – se não informado, assumir um perfil compatível com o setor)  

        *"Se houver dados contraditórios ou desorganizados, priorize as informações mais relevantes e crie um perfil coeso e bem estruturado."*  
        *Não esboce nenhum traço de chatbots típicos em sua análise (EM HIPOTÉSE ALGUMA: "Analise e breve resumo do perfil solicitado:", "Claro, está aqui a ánalise...", etc), apenas entregue o perfil ideal sem nenhuma observação ou mensagem introdutória.*
        """

        gemini_client = GoogleGeminiClient()
        response = gemini_client.generate_response(message)

        return jsonify({"response": response}), 200

    except Exception as e:
        print(f"Erro no endpoint best_profile: {e}")
        return (
            jsonify(
                {
                    "error": "Erro interno no servidor. Por favor, tente novamente mais tarde."
                }
            ),
            500,
        )
