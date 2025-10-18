"""
Extraccion de informacion
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API")


def extraccion_data(endpoint):
    """
    Extrae la información del API usando requests.get con timeout seguro.
    """
    try:
        headers = {
            "x-api-key": API_KEY,
            "Accept": "application/json"
        }
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        print("Extracción", endpoint, "exitosa")
        return response.json()
    except requests.Timeout:
        print(f"Error: la petición a {endpoint} tardó demasiado y se canceló")
    except requests.HTTPError as e:
        print(f"Error HTTP: {e}")
    except requests.RequestException as e:
        print(f"Error en la petición: {e}")
