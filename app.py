from flask import Flask, jsonify, Response, render_template, request, redirect, url_for
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
import os

app = Flask(__name__)

DATABASE = "/data/etudiants.db"

compteur_requetes = Counter(
    "app_requetes_total",
    "Nombre total de requetes recues par l'application"
)


def connexion_db():
    connexion = sqlite3.connect(DATABASE)
    connexion.row_factory = sqlite3.Row
    return connexion


def initialiser_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

    connexion = connexion_db()

    connexion.execute("""
        CREATE TABLE IF NOT EXISTS etudiants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            filiere TEXT NOT NULL,
            niveau TEXT NOT NULL
        )
    """)

    nombre = connexion.execute(
        "SELECT COUNT(*) FROM etudiants"
    ).fetchone()[0]

    if nombre == 0:
        connexion.executemany(
            """
            INSERT INTO etudiants (nom, filiere, niveau)
            VALUES (?, ?, ?)
            """,
            [
                ("Etudiant 1", "Genie Informatique", "Licence"),
                ("Etudiant 2", "Telecommunications", "Licence"),
                ("Etudiant 3", "Genie Informatique", "DTS")
            ]
        )

    connexion.commit()
    connexion.close()


@app.route("/")
def accueil():
    compteur_requetes.inc()

    connexion = connexion_db()

    etudiants = connexion.execute(
        "SELECT * FROM etudiants ORDER BY id DESC"
    ).fetchall()

    connexion.close()

    return render_template(
        "index.html",
        etudiants=etudiants,
        nombre_etudiants=len(etudiants)
    )


@app.route("/ajouter", methods=["POST"])
def ajouter_etudiant():
    compteur_requetes.inc()

    nom = request.form.get("nom", "").strip()
    filiere = request.form.get("filiere", "").strip()
    niveau = request.form.get("niveau", "").strip()

    if nom and filiere and niveau:
        connexion = connexion_db()

        connexion.execute(
            """
            INSERT INTO etudiants (nom, filiere, niveau)
            VALUES (?, ?, ?)
            """,
            (nom, filiere, niveau)
        )

        connexion.commit()
        connexion.close()

    return redirect(url_for("accueil"))


@app.route("/modifier/<int:id>", methods=["POST"])
def modifier_etudiant(id):
    compteur_requetes.inc()

    nom = request.form.get("nom", "").strip()
    filiere = request.form.get("filiere", "").strip()
    niveau = request.form.get("niveau", "").strip()

    if nom and filiere and niveau:
        connexion = connexion_db()

        connexion.execute(
            """
            UPDATE etudiants
            SET nom = ?, filiere = ?, niveau = ?
            WHERE id = ?
            """,
            (nom, filiere, niveau, id)
        )

        connexion.commit()
        connexion.close()

    return redirect(url_for("accueil"))


@app.route("/supprimer/<int:id>", methods=["POST"])
def supprimer_etudiant(id):
    compteur_requetes.inc()

    connexion = connexion_db()

    connexion.execute(
        "DELETE FROM etudiants WHERE id = ?",
        (id,)
    )

    connexion.commit()
    connexion.close()

    return redirect(url_for("accueil"))


@app.route("/api/etudiants")
def api_etudiants():
    compteur_requetes.inc()

    connexion = connexion_db()

    lignes = connexion.execute(
        "SELECT * FROM etudiants ORDER BY id"
    ).fetchall()

    connexion.close()

    return jsonify([
        dict(etudiant) for etudiant in lignes
    ])


@app.route("/api/status")
def status():
    compteur_requetes.inc()

    return jsonify({
        "application": "Gestion des étudiants - INPTIC",
        "statut": "operationnel",
        "base_de_donnees": "SQLite",
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
    initialiser_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )
