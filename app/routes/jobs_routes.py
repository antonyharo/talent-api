from flask import Blueprint, jsonify, request
import csv
from jobspy import scrape_jobs
import logging
import requests
import math
import pandas as pd

from app.config import Config

# Inicializar Blueprint
jobs_bp = Blueprint("jobs", __name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def renew_tor_ip_with_socks():
    try:
        session = requests.Session()
        session.proxies = {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050",
        }
        ip = session.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
        logging.info(f"Tor IP renewed successfully: {ip}")
        return session
    except Exception as e:
        logging.error(f"Error renewing Tor IP with socks: {e}")
        return None

def get_real_ip(session):
    try:
        ip = session.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
        logging.info(f"IP from ipify: {ip}")
        return ip
    except Exception as e:
        logging.error(f"Error getting IP: {e}")
        return None

def format_proxies(proxies):
    if not proxies:
        return None
    formatted_proxies = []
    for proxy in proxies:
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            formatted_proxies.append(f"http://{proxy}")  # default http
        else:
            formatted_proxies.append(proxy)
    return formatted_proxies

@jobs_bp.route("/", methods=["POST"])
def search_jobs():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Parâmetros obrigatórios
        if "search_term" not in data or "location" not in data:
            return (
                jsonify(
                    {"error": "Missing required parameters: search_term and location"}
                ),
                400,
            )

        search_term = data["search_term"]
        location = data["location"]

        # Parâmetros opcionais com valores padrão
        site_name = data.get(
            "site_name", ["indeed", "linkedin", "vagas", "glassdoor", "google"]
        )
        google_search_term = data.get("google_search_term")
        distance = data.get("distance", 50)
        job_type = data.get("job_type")
        proxies = data.get("proxies")
        is_remote = data.get("is_remote", False)
        results_wanted = data.get("results_wanted", 20)
        easy_apply = data.get("easy_apply", False)
        description_format = data.get("description_format", "markdown")
        offset = data.get("offset", 0)
        hours_old = data.get("hours_old", 72)
        verbose = data.get("verbose", 2)
        linkedin_fetch_description = data.get("linkedin_fetch_description", False)
        linkedin_company_ids = data.get("linkedin_company_ids")
        country_indeed = data.get("country_indeed", "USA")
        enforce_annual_salary = data.get("enforce_annual_salary", False)
        ca_cert = data.get("ca_cert")
        use_tor = data.get("use_tor", False)
        candidate_id = data.get("candidate_id")  # Get the candidate_id

        if not google_search_term:
            google_search_term = f"{search_term} jobs near {location} since yesterday"

        logging.info(f"Starting job scraping with parameters: {data}")

        if isinstance(site_name, str):
            site_name = [site_name]

        formatted_proxies = None
        tor_session = None
        proxy_dict = None

        if proxies:
            formatted_proxies = format_proxies(proxies)
            logging.info(f"Proxies after format: {formatted_proxies}")

        if use_tor:
            tor_session = renew_tor_ip_with_socks()
            if not tor_session:
                logging.info(f"Not using tor proxy, due to an error.")
                formatted_proxies = formatted_proxies if formatted_proxies else None
            else:
                logging.info(f"Using tor proxy.")
                proxy_dict = {
                    "http": "socks5://127.0.0.1:9050",
                    "https": "socks5://127.0.0.1:9050",
                }
                if formatted_proxies:
                    for proxy in formatted_proxies:
                        if proxy.startswith("http://"):
                            proxy_dict["http"] = proxy
                        elif proxy.startswith("https://"):
                            proxy_dict["https"] = proxy

        elif formatted_proxies:
            proxy_dict = {}
            for proxy in formatted_proxies:
                if proxy.startswith("http://"):
                    proxy_dict["http"] = proxy
                elif proxy.startswith("https://"):
                    proxy_dict["https"] = proxy

        if tor_session:
            ip_address = get_real_ip(tor_session)
            logging.info(f"Getting IP using tor_session: {ip_address}")
        elif proxy_dict:
            ip_address = get_real_ip(requests.Session())
            logging.info(f"Getting IP using formatted_proxies: {ip_address}")
        else:
            ip_address = get_real_ip(requests.Session())
            logging.info(f"Getting IP using standard Session: {ip_address}")

        logging.info(f"IP used for the search: {ip_address}")
        jobs = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location,
            distance=distance,
            job_type=job_type,
            proxies=proxy_dict,
            is_remote=is_remote,
            results_wanted=results_wanted,
            easy_apply=easy_apply,
            description_format=description_format,
            offset=offset,
            hours_old=hours_old,
            verbose=verbose,
            linkedin_fetch_description=linkedin_fetch_description,
            linkedin_company_ids=linkedin_company_ids,
            country_indeed=country_indeed,
            enforce_annual_salary=enforce_annual_salary,
            ca_cert=ca_cert,
            session=tor_session if tor_session else None,
        )

        # Substituir valores NaN por None no DataFrame
        jobs = jobs.where(pd.notnull(jobs), None)

        # Adicionar candidate_id ao DataFrame, se presente
        if candidate_id:
            jobs["candidate_id"] = candidate_id

        jobs_json = jobs.to_dict(orient="records")
        response_data = {"message": f"Found {len(jobs)} jobs", "jobs": jobs_json}

        if ip_address:
            response_data["ip_address"] = ip_address

        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
