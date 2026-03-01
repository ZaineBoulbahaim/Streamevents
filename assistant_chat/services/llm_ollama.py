import requests
import json

# URL de la API de Ollama que corre localmente en tu máquina
OLLAMA_URL = "http://localhost:11434/api/generate"

# Modelo que usaremos, puedes cambiarlo por "mistral:7b" para comparar
OLLAMA_MODEL = "llama3.1:8b"
# OLLAMA_MODEL = "mistral:7b"


def generate(prompt: str) -> str:
    """
    Envía un prompt al modelo LLM local (Ollama) y devuelve su respuesta completa.
    Versión sin stream: espera a que el modelo termine antes de devolver nada.

    Args:
        prompt: El texto completo que le enviamos al modelo

    Returns:
        str: La respuesta generada por el modelo en texto plano
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,             # Espera la respuesta completa de una vez
        "options": {
            "temperature": 0.1,      # Temperatura baja = menos alucinaciones
            "top_p": 0.9,            # Diversidad del vocabulario
            "num_ctx": 2048          # Tamaño del contexto en tokens
        }
    }

    # Enviamos la petición HTTP POST a Ollama
    respuesta = requests.post(OLLAMA_URL, json=payload, timeout=60)
    respuesta.raise_for_status()

    # Ollama devuelve: {"response": "texto generado", "model": ..., ...}
    datos = respuesta.json()
    return datos.get("response", "").strip()


def generate_stream(prompt: str):
    """
    Versión con stream: genera tokens uno a uno usando un generador de Python.
    En lugar de esperar la respuesta completa, envía cada palabra
    en cuanto el modelo la genera.

    Args:
        prompt: El texto completo que le enviamos al modelo

    Yields:
        str: Cada token (palabra o fragmento) generado por el modelo
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,              # Activamos el stream
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_ctx": 2048
        }
    }

    # stream=True en requests significa que lee la respuesta línea a línea
    # sin esperar a que llegue completa
    with requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True) as resposta:
        resposta.raise_for_status()

        # Ollama envía una línea JSON por cada token generado
        # Ejemplo línea: {"response": "Hola", "done": false}
        for linea in resposta.iter_lines():
            if linea:
                # Convertimos la línea JSON a diccionario
                chunk = json.loads(linea.decode("utf-8"))

                # Extraemos el token generado
                token = chunk.get("response", "")

                if token:
                    # yield envía el token inmediatamente sin esperar al siguiente
                    yield token

                # Cuando done=True, el modelo ha terminado de generar
                if chunk.get("done", False):
                    break