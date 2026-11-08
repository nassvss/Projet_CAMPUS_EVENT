# CAMPUS EVENT

Système d'information de gestion d'événements universitaires (projet du module *Introduction aux Systèmes d'information*).

Architecture 3-tiers :

| Niveau | Rôle | Technologie |
|---|---|---|
| Présentation | Affichage des événements, formulaire d'inscription | `index.html` (HTML / CSS / JavaScript, `fetch()`) |
| Logique métier | API REST, règles métier, codes HTTP | Python / Flask (`app.py`) |
| Données | Stockage des étudiants, événements et inscriptions | Listes Python (en mémoire) |

> Les données sont stockées **en mémoire** : elles sont réinitialisées à chaque redémarrage du serveur.

## 1. Prérequis

- Python 3.9 ou supérieur (vérifier avec `python --version`, ou `python3 --version` sous macOS / Linux)
- `pip`

## 2. Installation

Depuis le dossier `CAMPUS_EVENT/` :

```bash
# (optionnel mais recommandé) créer un environnement virtuel
python -m venv venv

# l'activer
#   Windows (PowerShell) : venv\Scripts\Activate.ps1
#   Windows (cmd)        : venv\Scripts\activate.bat
#   macOS / Linux        : source venv/bin/activate

# installer Flask (les en-têtes CORS sont ajoutés directement dans app.py)
pip install flask
```

## 3. Lancer l'application

### Étape 1 : démarrer l'API

```bash
python app.py
```

Le serveur démarre à l'adresse : **http://127.0.0.1:5000**

Test rapide : ouvrir http://127.0.0.1:5000/events dans le navigateur, une liste JSON d'événements doit s'afficher.

### Étape 2 : ouvrir le frontend

Laisser le serveur Flask tourner, puis ouvrir le fichier `index.html` :

- soit en double-cliquant dessus (ouverture directe dans le navigateur) ;
- soit via un petit serveur local (dans un second terminal, dans le même dossier) :

```bash
python -m http.server 8000
```

puis aller sur http://127.0.0.1:8000/index.html

La page affiche les événements récupérés via `GET /events`. Si le serveur Flask est arrêté, la page affiche un message d'erreur.

## 4. Endpoints de l'API

| Méthode | Endpoint | Description | Code succès |
|---|---|---|---|
| GET | `/events` | Liste de tous les événements | 200 |
| GET | `/events/<id>` | Détail d'un événement | 200 |
| GET | `/students` | Liste des étudiants | 200 |
| POST | `/registrations` | Créer une inscription | 201 |
| GET | `/registrations` | Liste des inscriptions | 200 |
| GET | `/registrations/<id>` | Détail d'une inscription | 200 |
| PATCH | `/registrations/<id>` | Modifier le statut (`accepted` / `rejected`) | 200 |

## 5. Règles métier et codes d'erreur

| Situation | Réponse |
|---|---|
| `student_id` ou `event_id` absent (ou corps non JSON) | 400 |
| `student_id` ou `event_id` qui n'est pas un entier positif (texte, booléen, 0, négatif…) | 400 |
| Étudiant inexistant | 404 |
| Événement inexistant | 404 |
| Étudiant déjà inscrit à cet événement (inscription non refusée) | 409 |
| Événement complet (aucune place disponible) | 409 |
| Inscription créée | 201, statut initial `pending`, une place est retirée |
| Statut modifié en `accepted` | 200 |
| Statut modifié en `rejected` | 200, la place est libérée |
| `PATCH` avec un statut invalide | 400 |
| `PATCH` sur une inscription déjà traitée | 409 |
| Inscription inexistante | 404 |

## 6. Exemples de requêtes

(Avec `curl` sous macOS / Linux / Git Bash. Sous Windows, il est plus simple d'utiliser Postman.)

```bash
# Lister les événements
curl http://127.0.0.1:5000/events

# Détail de l'événement 1
curl http://127.0.0.1:5000/events/1

# Lister les étudiants
curl http://127.0.0.1:5000/students

# Créer une inscription
curl -X POST http://127.0.0.1:5000/registrations \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "event_id": 2}'

# Lister les inscriptions
curl http://127.0.0.1:5000/registrations

# Accepter l'inscription 1
curl -X PATCH http://127.0.0.1:5000/registrations/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

Exemple de réponse à `POST /registrations` (201) :

```json
{
  "message": "Inscription creee, en attente de validation",
  "registration": {
    "id": 1,
    "student_id": 1,
    "event_id": 2,
    "date_inscription": "2026-11-08 12:00:00",
    "status": "pending"
  }
}
```

Exemple d'erreur (409) :

```json
{ "error": "Evenement complet" }
```

## 7. Tester l'API avec Postman

Importer ou créer les requêtes ci-dessus, avec le header `Content-Type: application/json` pour les `POST` et `PATCH`.
L'événement 3 (« Atelier Python ») a une capacité de **1 place** pour pouvoir tester le cas « événement complet ».
Pour rejouer la campagne de tests depuis zéro, **redémarrer le serveur** (les données repartent de l'état initial).

## 8. Fonctionnalités bonus

- Formulaire d'inscription dans `index.html` (saisie du numéro étudiant + bouton « S'inscrire » par événement) ;
- Envoi de `POST /registrations` avec `fetch()` ;
- Affichage du message de confirmation retourné par l'API ;
- Affichage des erreurs métier (400, 404, 409) avec leur code ;
- Bouton désactivé et mention « Complet » lorsqu'il n'y a plus de places ;
- Mise en forme CSS.

## 9. Structure du projet

```
CAMPUS_EVENT/
├── app.py        # API Flask (logique métier + données)
├── index.html    # Frontend (fetch)
├── README.md     # Ce fichier
└── rapport.pdf   # Rapport du projet
```