#!/usr/bin/env python3
"""Aligne les sources de la formation 4-020 sur la méthodologie de la 4-024.

Trois écarts sont comblés, sans déplacer ni modifier aucun livrable :

  1. conducteur.json  : le `schedule` de contenus_diaporamas.json devient un
     conducteur au schéma de la 4-024, avec bornes minutées, nature codée et
     surtout une colonne « preuve », qui dit ce que le participant doit
     produire pour valider chaque séquence.
  2. references.json  : le dictionnaire `sources` devient une bibliographie
     indexée au même schéma que celle de la 4-024, sans rien perdre.
  3. INDEX_TP.json    : les notebooks sont décrits par atelier et par rôle
     (apprenant / corrigé / corrigé exécuté), comme dans la 4-024.

Les chemins des travaux pratiques sont épinglés dans SHA256SUMS.txt,
MANIFESTE_LIVRAISON.json, INVENTAIRE_COMPLET.json et PROVENANCE.json : les
fichiers restent donc à leur place et ce script n'ajoute que des descripteurs.

    python3 outils/build_methodo_4020.py
"""
from pathlib import Path
import json
import re

RACINE = Path(__file__).resolve().parent.parent
KIT = RACINE / "formation_4_020"
SOURCES = KIT / "sources_production"
TP = KIT / "travaux_pratiques"

# Vocabulaire des natures, commun aux deux formations.
# E exposé, P pratique, D démonstration, V évaluation. La 4-024 n'utilise pas V.
NATURE = {"Apport": "E", "TP": "P", "Évaluation": "V"}

# Preuve attendue par séquence, rédigée d'après les diapositives et le dossier
# pédagogique. Clé : identifiant de segment du `schedule`.
# Valeur : (preuve attendue, notebook mobilisé ou "").
PREUVES = {
    "B1.1": ("Réponses individuelles au diagnostic", ""),
    "B1.2": ("Un besoin métier reformulé en tâche et en cible", ""),
    "B1.3": ("Huit situations classées, hypothèses explicitées", ""),
    "B1.4": ("Entraînement, inférence et décision distingués sur un cas", ""),
    "B1.5": ("Chaîne de décision Novalia dessinée jusqu’au destinataire", ""),
    "B2.1": ("Mécanismes de création de valeur nommés sur un cas", ""),
    "B2.2": ("Comparaison argumentée des deux moteurs de recommandation", ""),
    "B2.3": ("Les quatre issues et leurs conséquences métier", ""),
    "B2.4": ("Politique de seuil retenue et coût des erreurs assumé", ""),
    "B2.5": ("Canevas de valeur des données complété", ""),
    "B3.1": ("Responsabilités de la donnée réparties par rôle", ""),
    "B3.2": ("Sept anomalies relevées et variable du futur identifiée",
             "01_Atelier_Novalia_participant.ipynb"),
    "B3.3": ("Usage qualifié : finalité, base légale, niveau de risque", ""),
    "B3.4": ("RACI nominatif et registre de risques déclenchant une action", ""),
    "B3.5": ("Restitution orale de la journée, sans support", ""),
    "B4.1": ("Système reconstruit de mémoire au tableau", ""),
    "B4.2": ("Six décisions de cadrage explicitées avant tout algorithme", ""),
    "B4.3": ("Bilan des données, référence simple et deux modèles entraînés",
             "01_Atelier_Novalia_participant.ipynb"),
    "B4.4": ("Lecture d’une courbe précision-rappel et de son AP", ""),
    "B4.5": ("Seuil gelé sur validation, test ouvert une seule fois",
             "01_Atelier_Novalia_participant.ipynb"),
    "B4.6": ("Conditions d’emploi de l’apprentissage profond argumentées", ""),
    "B4.7": ("Quatre indicateurs construits sur l’export predictions_powerbi.csv",
             "01_Atelier_Novalia_participant.ipynb"),
    "B5.1": ("Modes d’échange comparés sur une contrainte réelle", ""),
    "B5.2": ("Schéma de flux, du score jusqu’à l’action dans le SI", ""),
    "B5.3": ("Clauses minimales d’un contrat de données listées", ""),
    "B5.4": ("Cas de panne traités et décision explicite journalisée",
             "03_Simulation_contrat_donnees.ipynb"),
    "B5.5": ("Procédure d’incident et journal de décision", ""),
    "B5.6": ("QCM individuel et plan de transfert personnel", ""),
}

# Ateliers notebook, décrits par rôle comme dans la 4-024.
ATELIERS = [
    {
        "id": "01",
        "titre": "Atelier Novalia : du risque de départ à une décision dans le SI",
        "blocs": ["B4.3", "B4.5", "B4.7"],
        "variantes": {
            "apprenant": "01_Atelier_Novalia_participant.ipynb",
            "corrige": None,
            "corrige_execute": "02_Atelier_Novalia_corrige_execute.ipynb",
        },
        "donnees": ["novalia_clients.csv", "predictions_powerbi.csv"],
        "note": "Les cellules d’exercice sont des analyses rédigées, pas des cellules de code à compléter.",
    },
    {
        "id": "02",
        "titre": "Simulation d’un contrat de données partenaire",
        "blocs": ["B5.4"],
        "variantes": {
            "apprenant": None,
            "corrige": None,
            "corrige_execute": "03_Simulation_contrat_donnees.ipynb",
        },
        "donnees": [],
        "note": "Annexe facultative du bloc B5. Le corrigé est inclus dans le notebook : à ne pas distribuer avant le débrief.",
    },
]

MARQUEURS_EXERCICE = re.compile(r"^#{1,6}\s*(votre analyse|analyse)\b", re.I | re.M)


def compter_cellules(chemin):
    """Retourne (cellules, cellules de code, exercices repérés)."""
    notebook = json.loads(chemin.read_text(encoding="utf-8"))
    cellules = notebook["cells"]
    exercices = sum(
        len(MARQUEURS_EXERCICE.findall("".join(c["source"])))
        for c in cellules if c["cell_type"] == "markdown"
    )
    return len(cellules), sum(1 for c in cellules if c["cell_type"] == "code"), exercices


def construire_conducteur(schedule):
    curseur = {}
    lignes = []
    for seg, jour, bloc, minutes, nature, intitule in schedule:
        debut = curseur.get(jour, 0)
        preuve, notebook = PREUVES[seg]
        lignes.append({
            "day": jour,
            "block": bloc,
            "seg": seg,
            "start": debut,
            "end": debut + minutes,
            "label": intitule,
            "minutes": minutes,
            "nature": NATURE[nature],
            "proof": preuve,
            "tp": notebook,
        })
        curseur[jour] = debut + minutes
    return lignes


def construire_references(sources):
    references = {}
    for identifiant, (libelle, url, date, note) in sorted(sources.items()):
        auteur, titre = "", libelle
        if " : " in libelle:
            auteur, titre = libelle.split(" : ", 1)
        references[identifiant] = {
            "id": identifiant,
            "author": auteur,
            "title": titre,
            "date": date,
            "url": url,
            "note": note,
            "libelle": libelle,
        }
    return references


def construire_index_tp():
    index = []
    for atelier in ATELIERS:
        entree = dict(atelier)
        reference = atelier["variantes"]["apprenant"] or atelier["variantes"]["corrige_execute"]
        cellules, code, exercices = compter_cellules(TP / reference)
        entree.update(cellules=cellules, cellules_code=code, exercices=exercices)
        manquantes = [role for role, f in atelier["variantes"].items() if f is None]
        entree["variantes_absentes"] = manquantes
        index.append(entree)
    return index


def main():
    donnees = json.loads((SOURCES / "contenus_diaporamas.json").read_text(encoding="utf-8"))

    conducteur = construire_conducteur(donnees["schedule"])
    references = construire_references(donnees["sources"])
    index_tp = construire_index_tp()

    for cible, contenu in [
        (SOURCES / "conducteur.json", conducteur),
        (SOURCES / "references.json", references),
        (TP / "INDEX_TP.json", index_tp),
    ]:
        cible.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"écrit {cible.relative_to(RACINE)}")

    total = sum(l["minutes"] for l in conducteur)
    pratique = sum(l["minutes"] for l in conducteur if l["nature"] == "P")
    sans_preuve = [l["seg"] for l in conducteur if not l["proof"]]
    print(f"conducteur : {len(conducteur)} séquences, {total} minutes, "
          f"{pratique} minutes de pratique ({100 * pratique / total:.1f} %)")
    print(f"preuves renseignées : {len(conducteur) - len(sans_preuve)}/{len(conducteur)}"
          + (f" — manquantes : {sans_preuve}" if sans_preuve else ""))
    print(f"références : {len(references)}")
    for atelier in index_tp:
        absentes = ", ".join(atelier["variantes_absentes"]) or "aucune"
        print(f"atelier {atelier['id']} : {atelier['cellules']} cellules, "
              f"{atelier['exercices']} exercices, variantes absentes : {absentes}")


if __name__ == "__main__":
    main()
