from flask import Blueprint, jsonify, request
from app.services.google_gemini import GoogleGeminiClient

best_profile_bp = Blueprint("best_profile", __name__)


@best_profile_bp.route("", methods=["POST"])
def best_profile():
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
            Você é um especialista em recrutamento e seleção que gera perfis de candidatos ideais para oportunidades de emprego.  

            **"Crie o perfil do candidato ideal para a seguinte vaga:"**  

            - **Nome da vaga:** {job_title}  
            - **Nível do cargo:** {job_level}  
            - **Setor da vaga:** {job_sector}  
            - **Descrição da vaga:** {job_description}  
            - **Faixa salarial:** {job_salary}  

            Se algum dos dados acima estiver incompleto ou ausente, preencha as lacunas com informações típicas para esse tipo de cargo.  

            Com base nesses dados, crie um perfil completo e detalhado, incluindo:  

            1. **🎯 Breve resumo do perfil**  
            - Introdução do candidato destacando pontos fortes, diferenciais e principais características.  

            2. **🎓 Formação acadêmica**  
            - Graduação, pós-graduação e certificações relevantes.  
            - Caso não haja detalhes, sugira formações comuns para esse cargo.  

            3. **🏢 Experiência profissional**  
            - Cargos anteriores, empresas, tempo de experiência e principais conquistas.  
            - Caso não especificado, use referências típicas do setor.  

            4. **🛠 Habilidades técnicas (Hard Skills)**  
            - Ferramentas, linguagens, metodologias e conhecimentos específicos.  
            - Apresente cada uma com uma classificação de 1 a 5 estrelas (⭐).  

            5. **💡 Habilidades comportamentais (Soft Skills)**  
            - Características interpessoais valorizadas para esse cargo.  
            - Avalie cada uma com estrelas (⭐).  

            6. **🌍 Idiomas e outras competências diferenciais**  
            - Idiomas falados e nível de fluência.  
            - Experiências internacionais, projetos voluntários ou qualquer diferencial estratégico.  

            7. **🏢 Fit cultural**  
            - Como o candidato se encaixa nos valores e cultura da empresa.  
            - Caso não especificado, crie um perfil compatível com o setor.  

            8. **📊 Indicadores de desempenho e métricas**  
            - Principais KPIs e resultados atingidos ao longo da carreira.  
            - Exemplos: Redução de custos, aumento de produtividade, crescimento de receita.  

            9. **📈 Principais conquistas e prêmios**  
            - Reconhecimentos recebidos ao longo da carreira.  
            - Participação em projetos inovadores ou cases de sucesso.  

            10. **🔧 Ferramentas e softwares dominados**  
            - Tecnologias relevantes para o cargo e nível de domínio de cada uma.  
            - Apresentar em uma tabela com estrelas para avaliação.  

            11. **🧩 Estilo de trabalho e perfil comportamental**  
            - Como o candidato trabalha em equipe, estilo de liderança e capacidade de adaptação.  

            12. **🚀 Planos de carreira e objetivos profissionais**  
            - Ambições e expectativas para o futuro dentro da área.  

            ### **📋 Formato de saída esperado:**  

            🎯 **Resumo do perfil:** Profissional experiente em [setor], com sólida expertise em [principais habilidades]. Possui forte capacidade de liderança, inovação e entrega de resultados [...].  

            🎓 **Formação Acadêmica:**  
            - **[Graduação em Área Relacionada]** – [Universidade], Ano  
            - **[Pós-graduação/MBA em Área Relevante]** – [Universidade], Ano  
            - **Certificações:** [Certificação relevante 1], [Certificação relevante 2]  

            🏢 **Experiência Profissional:**  
            | Cargo | Empresa | Tempo | Conquistas |
            |--------|-----------|--------|--------------|
            | [Cargo Atual] | [Empresa] | [X anos] | [Conquista relevante] |
            | [Cargo Anterior] | [Empresa] | [X anos] | [Conquista relevante] |

            🛠 **Habilidades Técnicas (Hard Skills):**  
            | Habilidade | Nível |
            |------------|--------|
            | [Skill Técnica 1] | ⭐⭐⭐⭐⭐ |
            | [Skill Técnica 2] | ⭐⭐⭐⭐ |
            | [Skill Técnica 3] | ⭐⭐⭐⭐ |

            💡 **Habilidades Comportamentais (Soft Skills):**  
            | Habilidade | Nível |
            |------------|--------|
            | Liderança | ⭐⭐⭐⭐⭐ |
            | Comunicação | ⭐⭐⭐⭐ |
            | Trabalho em equipe | ⭐⭐⭐⭐ |

            🌍 **Idiomas:**  
            - **Inglês:** Fluente ⭐⭐⭐⭐⭐  
            - **Espanhol:** Avançado ⭐⭐⭐⭐  

            🏆 **Diferenciais:**  
            - Experiência internacional  
            - Certificações especializadas  
            - Participação em projetos de inovação  

            📊 **Indicadores de Desempenho e Métricas:**  
            - Aumento de produtividade em 25% através da implementação de [Processo/Metodologia].  
            - Redução de custos operacionais em 30% na empresa [Nome da empresa].  

            📈 **Principais Conquistas e Prêmios:**  
            - Eleito "Melhor Profissional do Ano" na empresa [Nome da empresa] em [Ano].  
            - Criador de um projeto inovador que resultou em [Impacto positivo].  

            🔧 **Ferramentas e Softwares Dominados:**  
            | Ferramenta | Nível |
            |------------|--------|
            | [Software/Ferramenta 1] | ⭐⭐⭐⭐⭐ |
            | [Software/Ferramenta 2] | ⭐⭐⭐⭐ |
            | [Software/Ferramenta 3] | ⭐⭐⭐⭐ |

            🧩 **Estilo de Trabalho e Perfil Comportamental:**  
            - Profissional proativo, focado em resultados e apaixonado por inovação.  
            - Habilidade para trabalhar sob pressão e resolver problemas complexos.  

            🚀 **Planos de Carreira e Objetivos Profissionais:**  
            - Deseja continuar se especializando na área de [Área específica] e contribuir para o crescimento estratégico da empresa.  

            ---

            ### **🔹 Regras de Formatação:**  
            - **Estrutura visual clara e organizada** com tabelas, listas e emojis.  
            - **Classificação de habilidades e ferramentas com estrelas (⭐).**  
            - **Nenhuma introdução ou explicação**, apenas a entrega direta do perfil ideal.  
        """

    gemini_client = GoogleGeminiClient()

    response = gemini_client.generate_response(message)

    return response
