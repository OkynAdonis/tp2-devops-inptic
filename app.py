from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

compteur_requetes = Counter(
    "app_requetes_total",
    "Nombre total de requetes recues par l'application"
)


@app.route("/")
def accueil():
    compteur_requetes.inc()

    return jsonify({
        "application": "Gestion des étudiants - INPTIC",
        "statut": "Application opérationnelle",
        "message": "Bienvenue sur l'API du TP DevOps"
    })


@app.route("/api/etudiants")
def etudiants():
    compteur_requetes.inc()

    return jsonify([
        {"id": 1, "nom": "Etudiant 1", "filiere": "Genie Informatique"},
        {"id": 2, "nom": "Etudiant 2", "filiere": "Telecommunications"}
    ])


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
