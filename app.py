from flask import Flask, jsonify, Response, render_template
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

compteur_requetes = Counter(
    "app_requetes_total",
    "Nombre total de requetes recues par l'application"
)

ETUDIANTS = [
    {
        "id": 1,
        "nom": "Etudiant 1",
        "filiere": "Genie Informatique",
        "niveau": "Licence"
    },
    {
        "id": 2,
        "nom": "Etudiant 2",
        "filiere": "Telecommunications",
        "niveau": "Licence"
    },
    {
        "id": 3,
        "nom": "Etudiant 3",
        "filiere": "Genie Informatique",
        "niveau": "DTS"
    }
]


@app.route("/")
def accueil():
    compteur_requetes.inc()

    return render_template(
        "index.html",
        etudiants=ETUDIANTS,
        nombre_etudiants=len(ETUDIANTS)
    )


@app.route("/api/etudiants")
def etudiants():
    compteur_requetes.inc()
    return jsonify(ETUDIANTS)


@app.route("/api/status")
def status():
    compteur_requetes.inc()

    return jsonify({
        "application": "Gestion des étudiants - INPTIC",
        "statut": "operationnel",
        "monitoring": "Prometheus / Grafana",
        "deploiement": "Docker / Jenkins"
    })


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
