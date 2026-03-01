import json


def build_prompt(user_message: str, candidates: list) -> str:
    """
    Construye el prompt siguiendo exactamente las indicaciones del enunciado.
    """

    context_json = json.dumps(candidates, ensure_ascii=False, indent=2)

    prompt = f"""
    Ets un assistent de recomanació d'esdeveniments.
    Només pots recomanar events del context proporcionat.
    Si no hi ha matches, digues-ho i pregunta criteris.
    Respon SEMPRE en català.

    Respon ÚNICAMENT amb aquest JSON (sense text addicional fora del JSON):
    {{
    "answer": "text amb la recomanació",
    "recommended_ids": [1, 2, 3],
    "follow_up": ""
    }}

    CONTEXT:
    {context_json}

    Usuari: {user_message}
    """.strip()

    return prompt