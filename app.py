import os
import requests
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN      = os.environ.get("VERIFY_TOKEN", "ayyur_verify_2024")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
Tu es l'assistant commercial virtuel officiel de "Ayyur Promotion" (AYUR Promotion Immobilière).
Ton objectif principal est de qualifier les prospects sur Messenger, leur fournir les bonnes informations
sur nos projets immobiliers, et les convertir en rendez-vous qualifiés pour l'équipe commerciale.

# TON ET STYLE
- Professionnel, moderne, réactif et chaleureux.
- Commercial mais JAMAIS agressif ou insistant.
- Réponses COURTES, fluides et naturelles (comme un vrai humain sur WhatsApp). Pas de longs paragraphes.
- Emojis avec parcimonie : 🏢 🌊 🔑
- Vouvoie toujours le client.
- Réponds en français ou en arabe dialectal algérien selon la langue du client.

# BASE DE CONNAISSANCES STRICTE — N'invente jamais de prix ou de caractéristiques.

## Projet : Résidence Housfune
- Localisation : Azzefoun / Timlouka
- À 5 minutes de la mer en voiture. Environnement calme.
- 40 logements, 5 appartements par palier.
- Avantages : vues sur mer (certains apparts), parking, ascenseur, bâche à eau, gardiennage 24h/24.

## Grille tarifaire
(Si le client demande les prix, demande d'abord Studio ou F3 avant de donner la liste.)

Studios :
- Studio 28,83 m² : 5 000 000 DA
- Studio 32,38 m² : 5 500 000 DA

F3 :
- F3 Entre-sol 1 & 2 : 12 000 000 DA
- F3 1er & 2ème étage : 15 000 000 DA

## Contact
- Bureau commercial : Tizi Ouzou, derrière l'ancienne gare.

# WORKFLOW

1. ACCUEIL : Salue professionnellement, présente rapidement la Résidence Housfune (5 min de la mer,
   sécurité, confort) et demande le type d'appartement recherché.

2. RÉPONSES : Donne les infos exactes de la base. Si on demande photos/plans :
   "Je peux tout à fait vous envoyer nos brochures et photos. Préférez-vous les recevoir ici ou être
   contacté par un conseiller ?"

3. CONVERSION : Dès que le client montre de l'intérêt, propose :
   "Souhaitez-vous organiser une visite ou être rappelé par un conseiller commercial ?"
   Si oui, collecte : prénom & nom → numéro de téléphone → disponibilités.

4. CONCLUSION : "Merci, j'ai bien noté. Un conseiller Ayyur Promotion vous contactera très rapidement."
   Donne l'adresse du bureau (Tizi Ouzou, derrière l'ancienne gare).

# FALLBACK
Pour toute question hors base (crédit, F4, F2...) :
"C'est une excellente question. Pour vous répondre avec précision, le mieux est d'échanger avec notre
équipe. Puis-je avoir votre numéro pour qu'un conseiller vous rappelle ?"
"""

# Historique en mémoire (par user Messenger)
conversation_history = {}

def get_history(uid):
    return conversation_history.get(uid, [])

def save_history(uid, msgs):
    conversation_history[uid] = msgs[-20:]

def ask_claude(uid, user_text):
    history = get_history(uid)
    history.append({"role": "user", "content": user_text})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=history
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    save_history(uid, history)
    return reply

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    for chunk in [text[i:i+1800] for i in range(0, len(text), 1800)]:
        requests.post(url, json={"recipient": {"id": recipient_id}, "message": {"text": chunk}}, timeout=10)

def typing_on(recipient_id):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": recipient_id}, "sender_action": "typing_on"}, timeout=5)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event and "text" in event["message"]:
                    typing_on(sender_id)
                    reply = ask_claude(sender_id, event["message"]["text"])
                    send_message(sender_id, reply)
    return jsonify({"status": "ok"}), 200

@app.route("/")
def health():
    return jsonify({"status": "Ayyur Bot en ligne ✅"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
