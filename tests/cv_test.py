import requests
import os

# URL do seu endpoint Flask
url = "http://127.0.0.1:5000/cv"  # Substitua com a URL correta do seu servidor Flask

# Caminho para o arquivo PDF de exemplo
file_path = (
    "/home/antony/projetos/talent-api/tests/test.pdf"  # Substitua com o caminho correto
)

# Descrição da vaga
job = "Estamos buscando um desenvolvedor backend com experiência em Python e Flask, conhecimentos em bancos de dados relacionais e boas práticas de desenvolvimento."  # Substitua com a descrição real

# Verificar se o arquivo existe antes de tentar abri-lo
if not os.path.exists(file_path):
    print(f"Erro: o arquivo {file_path} não foi encontrado.")
else:
    # Abrir o arquivo PDF para envio
    with open(file_path, "rb") as file:
        # Enviar a requisição POST com o arquivo e a descrição
        files = {"file": (os.path.basename(file_path), file, "application/pdf")}
        data = {"job": job}

        response = requests.post(url, files=files, data=data)

    # Exibir a resposta da API
    if response.status_code == 201:
        print("Resposta da API:", response.json())
    else:
        print(f"Erro {response.status_code}: {response.text}")
