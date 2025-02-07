# Talent API - Documentação Completa

A **Talent API** é uma plataforma poderosa para análise, comparação e busca de oportunidades de trabalho, bem como para aprimoramento de perfis profissionais. A API conta com endpoints para interação com modelos de IA, avaliação de currículos, busca de vagas e análises comparativas.

## Endpoints, Parâmetros e Respostas Esperadas

### 1. **ask-gemini**

**Descrição:**
Endpoint para interação com o modelo de IA **Gemini**, que pode fornecer informações gerais, responder perguntas ou auxiliar em tarefas específicas.

**Requisição:**

```bash
curl -X POST http://localhost:5000/gemini \
-H "Content-Type: application/json" \
-d '{"message": "Olá! Me fale um pouco sobre você!"}'
```

**Resposta Esperada:**

```json
{
    "response": "Olá! Sou o Gemini, um modelo de IA projetado para auxiliar em diversas tarefas..."
}
```

### 2. **best-profile**

**Descrição:**
Gera um perfil ideal para uma determinada vaga com base em requisitos e critérios definidos, destacando habilidades, experiência e competências desejadas.

**Requisição:**

```bash
curl -X POST "http://localhost:5000/best-profile" \
 -H "Content-Type: application/json" \
 -d '{
"job": {
"title": "Desenvolvedor Backend",
"level": "Pleno",
"sector": "Tecnologia",
"description": "Desenvolvimento e manutenção de APIs REST utilizando Python e Django.",
"salary": "R$ 8.000 – R$ 12.000"
}
}'
```

**Resposta Esperada:**

```json
{
    "ideal_profile": {
        "skills": ["Python", "Django", "Banco de Dados SQL", "APIs REST"],
        "experience": "Mínimo de 3 anos trabalhando com desenvolvimento backend.",
        "certifications": [
            "AWS Certified Developer",
            "Certified Django Developer"
        ]
    }
}
```

### 3. **cv-analyzer**

**Descrição:**
Análise e comparação de currículos, destacando pontos fortes e áreas de melhoria, além de fornecer um ranking dos candidatos.

**Requisição:**

```bash
curl -X POST http://localhost:5000/cv-analyzer \
-F "file=@tests/test.pdf" \
-F "file=@uploads/data-science-cv-example.pdf"
```

**Resposta Esperada:**

```json
{
    "ranking": [
        {
            "candidate": "test.pdf",
            "score": 85,
            "strengths": ["Experiência sólida", "Certificações relevantes"],
            "improvements": ["Falta de projetos práticos"]
        },
        {
            "candidate": "data-science-cv-example.pdf",
            "score": 78,
            "strengths": ["Boa formação acadêmica"],
            "improvements": ["Pouca experiência prática"]
        }
    ]
}
```

### 4. **jobs-comparator**

**Descrição:**
Compara diferentes vagas de emprego, fornecendo insights sobre cada uma, destacando vantagens e desvantagens, e criando um ranking de melhor oportunidade.

**Requisição:**

```bash
curl -X POST http://localhost:5000/jobs-comparator \
-H "Content-Type: application/json" \
-d '{
"jobs": [
  {
    "title": "Profissional Líder Técnico de Engenharia de Dados",
    "salary": "R$ 8.000,00",
    "description": "Colaboração com times de Data Science e negócios, automação de processos..."
  },
  {
    "title": "Analista de Dados",
    "salary": "R$ 6.500,00",
    "description": "Buscamos um profissional apaixonado por tecnologia e transformação digital."
  }
]}'
```

**Resposta Esperada:**

```json
{
    "ranking": [
        {
            "title": "Profissional Líder Técnico de Engenharia de Dados",
            "score": 90,
            "pros": ["Salário competitivo", "Oportunidade de liderança"],
            "cons": ["Alta carga de responsabilidades"]
        },
        {
            "title": "Analista de Dados",
            "score": 80,
            "pros": ["Ambiente de crescimento", "Menor pressão de liderança"],
            "cons": ["Salário abaixo da média do mercado"]
        }
    ]
}
```

### 5. **jobs**

**Descrição:**
Busca vagas de emprego em diversas plataformas, permitindo filtros personalizados como localização, tipo de emprego e prazo de publicação.

**Requisição:**

```bash
curl -X POST http://localhost:5000/jobs/ \
 -H "Content-Type: application/json" \
 -d '{
"search_term": "Software Engineer",
"location": "New York",
"site_name": "linkedin",
"distance": 50,
"job_type": "full-time",
"is_remote": false,
"results_wanted": 10,
"offset": 0,
"hours_old": 72
}'
```

**Resposta Esperada:**

```json
{
  "message": "Found 10 jobs",
  "jobs": [
    {
      "title": "Software Engineer",
      "company": "TechCorp",
      "location": "New York, NY",
      "salary": "$120,000 - $150,000",
      "description": "Desenvolvimento de soluções escaláveis para plataforma cloud..."
    },
    ...
  ]
}
```
