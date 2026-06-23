import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

TOOLS_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
if TOOLS_PATH not in sys.path:
    sys.path.insert(0, TOOLS_PATH)

from pharmacy_finder import find_nearest_pharmacies

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY n'a pas été trouvée. Vérifie ton fichier .env")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[find_nearest_pharmacies],
)


def ask_agent(question: str) -> str:
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(question)
    return response.text


def ask_agent_with_data(question: str) -> dict:
    """
    Envoie la question a l'agent ET appelle directement find_nearest_pharmacies
    pour recuperer les donnees brutes a afficher sur la carte.
    On utilise une heuristique simple : on demande a Gemini d'extraire
    le quartier et le rayon mentionnes dans la question, puis on appelle
    nous-memes la fonction pour etre sur d'avoir les coordonnees exactes.
    """
    texte_reponse = ask_agent(question)

    # Extraction simple du quartier : on redemande a Gemini de l'extraire
    # sous forme structuree pour pouvoir refaire l'appel nous-memes
    extraction_prompt = f"""
    Dans la question suivante, extrait UNIQUEMENT le nom du quartier mentionné
    et le rayon en km si mentionné (sinon mets 1.0 par défaut).
    Réponds STRICTEMENT au format : quartier|rayon
    Exemple de réponse : Cocody|2.0

    Question : {question}
    """
    extraction = model.generate_content(extraction_prompt)
    try:
        quartier, rayon = extraction.text.strip().split("|")
        rayon = float(rayon)
    except Exception:
        quartier, rayon = "Abidjan", 1.0

    data = find_nearest_pharmacies(quartier.strip(), rayon_km=rayon)

    return {
        "reponse": texte_reponse,
        "position_recherchee": data.get("position_recherchee"),
        "rayon_km": data.get("rayon_km"),
        "pharmacies": data.get("pharmacies", []),
    }


if __name__ == "__main__":
    print("=== Agent Pharmacy Finder - tape 'quitter' pour sortir ===\n")
    while True:
        question = input("Toi : ")
        if question.lower() in ["quitter", "exit", "quit"]:
            break
        reponse = ask_agent(question)
        print(f"Agent : {reponse}\n")
