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

    jobTitle = request.form.get("jobTitle", "")
    jobDescription = request.form.get("jobDescription", "")

    try:
        create_upload_directory()
        file_paths = []

        # Salvar todos os arquivos localmente
        for file in files:
            print(file)
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
            Você é uma Inteligência Artificial especializada em análise comparativa de currículos, projetada para avaliar candidatos com base nas informações fornecidas e compará-los com a vaga disponível. Sua tarefa é analisar os perfis dos candidatos e determinar o grau de adequação de cada um em relação à oportunidade disponível.  

            **"Informações da Vaga:"**  

            - **Título da Vaga:** {jobTitle}  
            - **Descrição da Vaga:** {jobDescription}  

            Se algum dos dados acima estiver incompleto ou ausente, utilize informações típicas para esse tipo de cargo.  

            ---

            ### **📌 Instruções para Análise**  

            #### **1️⃣ Coleta e Processamento de Dados:**  
            Para cada candidato, extraia e analise as seguintes informações:  

            - **🏢 Experiência Profissional:**  
            - Tempo de atuação, setores, cargos ocupados e principais responsabilidades.  
            - Caso as informações sejam limitadas ou ausentes, registre isso na análise.  

            - **🛠 Habilidades Técnicas (Hard Skills):**  
            - Tecnologias, ferramentas, metodologias e conhecimentos técnicos relevantes.  
            - Caso não sejam especificadas, registre a ausência como um dado relevante.  

            - **💡 Habilidades Comportamentais (Soft Skills):**  
            - Competências interpessoais como liderança, trabalho em equipe e comunicação.  
            - Se não forem mencionadas, destaque essa ausência.  

            - **🎓 Formação Acadêmica e Certificações:**  
            - Graduação, pós-graduação, certificações e cursos complementares.  
            - Caso essas informações estejam incompletas ou ausentes, isso deve ser registrado.  

            - **🌍 Idiomas e Proficiência:**  
            - Idiomas mencionados e o nível de fluência.  
            - A ausência dessa informação deve ser registrada.  

            - **🏆 Conquistas e Projetos:**  
            - Resultados tangíveis, projetos relevantes ou diferenciais competitivos.  
            - Caso essa informação não esteja presente, identifique como uma lacuna.  

            - **🏢 Fit Cultural:**  
            - Como o candidato se encaixa na cultura organizacional, com base nas informações fornecidas.  
            - Se não houver dados suficientes para análise, registre a ausência.  

            ---

            #### **2️⃣ Análise Comparativa dos Candidatos:**  
            - **🎯 Resumo do Perfil:**  
            - Forneça um resumo conciso de cada candidato, destacando suas principais qualificações e diferenciais.  

            - **⚖️ Grau de Adequação à Vaga:**  
            - Compare as competências e experiências dos candidatos com os requisitos da vaga.  
            - Avalie a aderência de cada candidato utilizando uma escala de estrelas (⭐).  

                - **🔍 Lacunas e Oportunidades de Desenvolvimento:**  
                - Identifique ausências importantes que possam impactar a adequação do candidato à vaga.  

                ---

                #### **3️⃣ Geração de Resultados:**  
                - **📋 Relatório Estruturado:**  
                - Um resumo detalhado das qualificações e características de cada candidato.  
                - Pontos fortes e diferenciais para a vaga em questão.  
                - Principais lacunas identificadas.  

                - **📊 Tabela Markdown Comparativa:**  
                - Tabela destacando habilidades, experiência, formação acadêmica e alinhamento com a vaga.  

                - **💡 Insights Acionáveis:**  
                - Recomendações sobre quais candidatos estão mais preparados para a vaga e quais aspectos podem ser aprimorados.  

                ---

                ### **📋 Formato de Saída Esperado:**  

                ```
                📝 **Análise Comparativa de Candidatos para a Vaga: VAGA X**  

                ## 🔹 Candidatos Avaliados:

                ### **📌 Candidato 1: [Nome]**
                🎯 **Resumo do Perfil:**  
                Profissional com experiência em [setor], especializado em [principais habilidades]. Possui forte conhecimento em [tecnologias], além de habilidades em [soft skills relevantes].  

                🏢 **Experiência Profissional:**  
                | Cargo | Empresa | Tempo | Principais Conquistas |
                |--------|-----------|--------|----------------------|
                | [Cargo Atual] | [Empresa] | [X anos] | [Conquista relevante] |
                | [Cargo Anterior] | [Empresa] | [X anos] | [Conquista relevante] |

                🛠 **Habilidades Técnicas:**  
                | Habilidade | Nível |
                |------------|--------|
                | [Skill Técnica 1] | ⭐⭐⭐⭐⭐ |
                | [Skill Técnica 2] | ⭐⭐⭐⭐ |
                | [Skill Técnica 3] | ⭐⭐⭐ |

                💡 **Habilidades Comportamentais:**  
                | Habilidade | Nível |
                |------------|--------|
                | Liderança | ⭐⭐⭐⭐⭐ |
                | Comunicação | ⭐⭐⭐⭐ |
                | Trabalho em equipe | ⭐⭐⭐⭐ |

                🎓 **Formação Acadêmica:**  
                - **[Graduação em Área Relacionada]** – [Universidade], Ano  
                - **[Pós-graduação/MBA em Área Relevante]** – [Universidade], Ano  
                - **Certificações:** [Certificação relevante 1], [Certificação relevante 2]  

                🌍 **Idiomas:**  
                - **Inglês:** Fluente ⭐⭐⭐⭐⭐  
                - **Espanhol:** Intermediário ⭐⭐⭐  

                🏆 **Diferenciais:**  
                - Experiência internacional  
                - Participação em projetos inovadores  

                🏢 **Fit Cultural:**  
                [Descrição de como o candidato se encaixa na cultura da empresa e no setor]  

                📊 **Grau de Adequação à Vaga:** ⭐⭐⭐⭐☆  

                ---

                ### **📌 Candidato 2: [Nome]**  
                (Conteúdo semelhante ao Candidato 1)  

                ---

                ## **📊 Comparação de Candidatos**  

                Caso haja somente um candidato, faça um resumo das habilidades dele neste formato de tabela:

                | Critério | Candidato 1 | Candidato 2 | Candidato 3 |
                |----------|------------|------------|------------|
                | Experiência na área | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
                | Hard Skills | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
                | Soft Skills | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
                | Formação Acadêmica | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
                | Idiomas | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
                | Fit Cultural | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
                | Adequação Geral | ⭐⭐⭐⭐☆ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

                ---

                ### **💡 Conclusão e Recomendações**  
                📌 **Candidato mais adequado:** [Nome do candidato com melhor aderência]  
                📌 **Pontos fortes do candidato líder:** [Resumo dos principais diferenciais]  
                📌 **Sugestões para os outros candidatos:** [Áreas de melhoria e desenvolvimento]  
                ```

                ---

                ### **🔹 Regras de Formatação:**  
                - **Análise objetiva e detalhada** de cada candidato.  
                - **Tabelas para experiência e habilidades** para facilitar a comparação.  
                - **Escala de estrelas (⭐) para avaliação de competências**.  
                - **Sem introduções genéricas** como "Aqui está sua análise". Apenas apresente os resultados diretamente.  

                ---

                Com essa adaptação, o prompt agora gera análises estruturadas e comparativas, ajudando na escolha do candidato mais qualificado para a vaga! 🚀
            """
        )

        return jsonify({"response": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
