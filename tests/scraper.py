import requests

def scrape_data():
    api_url = "http://127.0.0.1:5000/scrape"
    request_data = {
        "search_term": "developer",
        "location": "New York",
        "site_name": ["indeed"],
        "use_tor": False,
        "results_wanted": 10
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Realiza a requisição POST
        response = requests.post(api_url, json=request_data, headers=headers)
        response.raise_for_status()  # Levanta uma exceção para status de erro HTTP
        print("Resposta do servidor:", response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}, Resposta do servidor: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Erro na requisição: {req_err}")

# Chama a função principal
if __name__ == "__main__":
    scrape_data()
