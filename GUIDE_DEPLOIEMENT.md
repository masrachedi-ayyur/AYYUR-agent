# Guide de déploiement — Ayyur Messenger Bot

## Ce que vous avez
Un serveur Python qui :
- Reçoit les DM Messenger de vos prospects
- Les envoie à Claude (IA) avec votre base de données Ayyur
- Renvoie la réponse automatiquement sur Messenger

---

## ÉTAPE 1 — Déployer le serveur sur Railway (gratuit)

1. Créez un compte sur https://railway.app
2. Cliquez "New Project" → "Deploy from GitHub repo"
   - Ou "Deploy from local folder" et uploadez ce dossier
3. Une fois déployé, Railway vous donne une URL publique :
   ex : `https://ayyur-bot-production.up.railway.app`
4. Allez dans "Variables" et ajoutez :
   - `ANTHROPIC_API_KEY`  = votre clé Claude (https://console.anthropic.com)
   - `PAGE_ACCESS_TOKEN`  = (obtenu à l'étape 2)
   - `VERIFY_TOKEN`       = `ayyur_verify_2024`  ← gardez cette valeur

---

## ÉTAPE 2 — Créer l'application Facebook

1. Allez sur https://developers.facebook.com
2. "Mes applications" → "Créer une application" → type "Entreprise"
3. Ajoutez le produit **Messenger**
4. Dans Messenger → Paramètres :
   - "Tokens d'accès" → sélectionnez votre Page Facebook Ayyur
   - Copiez le **Token d'accès à la page** → collez-le dans Railway comme `PAGE_ACCESS_TOKEN`

---

## ÉTAPE 3 — Connecter le Webhook

Dans Messenger → Webhooks :
1. **URL de rappel** : `https://VOTRE-URL-RAILWAY.up.railway.app/webhook`
2. **Token de vérification** : `ayyur_verify_2024`
3. Cochez : `messages` et `messaging_postbacks`
4. Cliquez "Vérifier et enregistrer"
5. Abonnez votre Page Facebook au webhook

---

## ÉTAPE 4 — Tester

Envoyez un DM sur votre Page Facebook Ayyur depuis un autre compte.
Le bot doit répondre automatiquement en quelques secondes.

---

## Coûts estimés
- Railway : gratuit jusqu'à 500h/mois (largement suffisant)
- Claude Haiku API : ~0,25$ pour 1 million de tokens (environ 5000 conversations)
- Total : presque gratuit au démarrage

---

## Support
Pour toute question technique sur ce bot, conservez ce guide.
