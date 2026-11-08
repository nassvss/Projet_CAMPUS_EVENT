from flask import Flask, jsonify, request
from datetime import datetime



app = Flask(__name__)


@app.after_request
def ajouter_headers_cors(response):
    """Autorise les appels de l'API depuis index.html."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, OPTIONS"
    return response

# ----- Données (listes Python) -----
students = [
    {"id": 1, "nom": "Martin", "prenom": "Léa", "email": "lea.martin@efrei.net", "filiere": "Informatique", "annee": 2},
    {"id": 2, "nom": "Dupont", "prenom": "Karim", "email": "karim.dupont@efrei.net", "filiere": "Informatique", "annee": 1},
    {"id": 3, "nom": "Nguyen", "prenom": "Sofia", "email": "sofia.nguyen@efrei.net", "filiere": "Data", "annee": 3},
    {"id": 4, "nom": "Bernard", "prenom": "Yanis", "email": "yanis.bernard@efrei.net", "filiere": "Réseaux", "annee": 2},
]

events = [
    {"id": 1, "titre": "Conférence IA", "date": "2026-12-03", "lieu": "Amphi A",
     "capacite": 100, "places_disponibles": 100},
    {"id": 2, "titre": "Forum entreprises", "date": "2026-12-10", "lieu": "Hall principal",
     "capacite": 50, "places_disponibles": 50},
    {"id": 3, "titre": "Atelier Python", "date": "2026-12-15", "lieu": "Salle B204",
     "capacite": 1, "places_disponibles": 1},  # capacité 1 pour tester "événement complet"
]

registrations = []


def trouver(liste, id):
    for element in liste:
        if element["id"] == id:
            return element
    return None


# ----- Événements -----
@app.get("/events")
def get_events():
    return jsonify(events), 200


@app.get("/events/<int:id>")
def get_event(id):
    event = trouver(events, id)
    if event is None:
        return jsonify({"error": "Evenement introuvable"}), 404
    return jsonify(event), 200


# ----- Étudiants -----
@app.get("/students")
def get_students():
    return jsonify(students), 200


# ----- Inscriptions -----
@app.post("/registrations")
def create_registration():
    data = request.get_json(silent=True)

    # champs obligatoires
    if not data or "student_id" not in data or "event_id" not in data:
        return jsonify({"error": "student_id et event_id sont obligatoires"}), 400

    student = trouver(students, data["student_id"])
    if student is None:
        return jsonify({"error": "Etudiant introuvable"}), 404

    event = trouver(events, data["event_id"])
    if event is None:
        return jsonify({"error": "Evenement introuvable"}), 404

    # double inscription
    for r in registrations:
        if r["student_id"] == student["id"] and r["event_id"] == event["id"] and r["status"] != "rejected":
            return jsonify({"error": "Etudiant deja inscrit a cet evenement"}), 409

    # événement complet
    if event["places_disponibles"] <= 0:
        return jsonify({"error": "Evenement complet"}), 409

    registration = {
        "id": len(registrations) + 1,
        "student_id": student["id"],
        "event_id": event["id"],
        "date_inscription": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    }
    registrations.append(registration)
    event["places_disponibles"] -= 1  # la place est reservee des la demande

    return jsonify({"message": "Inscription creee, en attente de validation",
                    "registration": registration}), 201


@app.get("/registrations")
def get_registrations():
    return jsonify(registrations), 200


@app.get("/registrations/<int:id>")
def get_registration(id):
    registration = trouver(registrations, id)
    if registration is None:
        return jsonify({"error": "Inscription introuvable"}), 404
    return jsonify(registration), 200


@app.patch("/registrations/<int:id>")
def update_registration(id):
    registration = trouver(registrations, id)
    if registration is None:
        return jsonify({"error": "Inscription introuvable"}), 404

    data = request.get_json(silent=True)
    if not data or data.get("status") not in ["accepted", "rejected"]:
        return jsonify({"error": "status doit etre accepted ou rejected"}), 400

    # on ne traite qu'une inscription en attente
    if registration["status"] != "pending":
        return jsonify({"error": "Inscription deja traitee"}), 409

    registration["status"] = data["status"]

    # si refusee, la place est liberee
    if data["status"] == "rejected":
        event = trouver(events, registration["event_id"])
        event["places_disponibles"] += 1

    return jsonify(registration), 200


if __name__ == "__main__":
    app.run(debug=True)
