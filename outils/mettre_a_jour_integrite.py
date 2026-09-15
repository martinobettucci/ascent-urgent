#!/usr/bin/env python3
"""Réaligne les manifestes d'intégrité sur les fichiers ajoutés ou régénérés.

Les kits sont livrés avec des empreintes SHA-256 qui décrivent l'archive. Les
index de navigation et les descripteurs produits par les autres outils doivent
y figurer, sinon `VERIFIER_INTEGRITE.py` échoue et l'inventaire devient faux.

Ce script ne touche qu'aux entrées des fichiers listés ci-dessous. Les autres
empreintes, et en particulier celles des livrables pédagogiques, ne sont ni
recalculées ni réécrites. Chaque passage laisse une trace dans REVISIONS.md.

    python3 outils/mettre_a_jour_integrite.py [--verifier]
"""
from datetime import date
from pathlib import Path
import argparse
import hashlib
import json

RACINE = Path(__file__).resolve().parent.parent

# Fichiers produits par outils/build_index.py et outils/build_methodo_4020.py.
SUIVIS = {
    "formation_4_020": [
        "00_OUVRIR_LES_SUPPORTS.html",
        "kit.json",
        "sources_production/conducteur.json",
        "sources_production/references.json",
        "travaux_pratiques/INDEX_TP.json",
        "README.md",
    ],
    "deep_learning_4_024": [
        "00_OUVRIR_LES_SUPPORTS.html",
        "kit.json",
        "README.md",
        "00_LIRE_EN_PREMIER.txt",
    ],
}

MOTIF = ("Ajout d’un index de navigation généré et des descripteurs de conducteur, "
         "de bibliographie et d’ateliers ; renvoi vers cet index depuis les points "
         "d’entrée. Aucun support pédagogique modifié.")


def empreinte(chemin):
    donnees = chemin.read_bytes()
    return len(donnees), hashlib.sha256(donnees).hexdigest()


def maj_inventaire_json(base, fichiers):
    """INVENTAIRE_COMPLET.json de la 4-020 : liste d'objets chemin/octets/sha256."""
    cible = base / "INVENTAIRE_COMPLET.json"
    inventaire = json.loads(cible.read_text(encoding="utf-8"))
    par_chemin = {e["chemin"]: e for e in inventaire["fichiers"]}
    ajouts, maj = [], []
    for relatif in fichiers:
        octets, sha = empreinte(base / relatif)
        if relatif in par_chemin:
            if par_chemin[relatif]["sha256"] != sha:
                par_chemin[relatif].update(octets=octets, sha256=sha)
                maj.append(relatif)
        else:
            entree = {"chemin": relatif, "octets": octets, "sha256": sha}
            inventaire["fichiers"].append(entree)
            par_chemin[relatif] = entree
            ajouts.append(relatif)
    inventaire["fichiers_manifestes"] = len(inventaire["fichiers"])
    inventaire.setdefault("revisions", []).append(
        {"date": date.today().isoformat(), "motif": MOTIF, "ajoutes": ajouts, "recalcules": maj}
    )
    return cible, json.dumps(inventaire, ensure_ascii=False, indent=2) + "\n", ajouts, maj


def maj_sha256sums(base, fichiers):
    cible = base / "SHA256SUMS.txt"
    if not cible.exists():
        return None, None, [], []
    lignes = {}
    ordre = []
    for ligne in cible.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        sha, nom = ligne.split("  ", 1)
        lignes[nom] = sha
        ordre.append(nom)
    ajouts, maj = [], []
    for relatif in fichiers:
        _, sha = empreinte(base / relatif)
        if relatif in lignes:
            if lignes[relatif] != sha:
                maj.append(relatif)
        else:
            ordre.append(relatif)
            ajouts.append(relatif)
        lignes[relatif] = sha
    contenu = "".join(f"{lignes[nom]}  {nom}\n" for nom in ordre)
    return cible, contenu, ajouts, maj


def maj_manifeste_csv(base, fichiers):
    """INVENTAIRE_COMPLET.csv et MANIFESTE_SHA256.json de la 4-024."""
    csv = base / "INVENTAIRE_COMPLET.csv"
    manifeste = base / "MANIFESTE_SHA256.json"
    if not csv.exists():
        return [], [], []
    brut = csv.read_bytes().decode("utf-8-sig")
    # Le CSV livré est en CRLF : on réécrit avec son terminateur d'origine.
    fin = "\r\n" if "\r\n" in brut else "\n"
    texte = brut.replace("\r\n", "\n")
    entete, *corps = [l for l in texte.splitlines() if l.strip()]
    lignes = {l.split(",", 1)[0]: l for l in corps}
    ordre = list(lignes)
    donnees = json.loads(manifeste.read_text(encoding="utf-8"))
    par_fichier = {e["fichier"]: e for e in donnees["fichiers"]}
    ajouts, maj = [], []
    for relatif in fichiers:
        octets, sha = empreinte(base / relatif)
        if relatif not in lignes:
            ajouts.append(relatif)
            ordre.append(relatif)
        elif lignes[relatif] != f"{relatif},{octets},{sha}":
            maj.append(relatif)
        lignes[relatif] = f"{relatif},{octets},{sha}"
        if relatif in par_fichier:
            par_fichier[relatif].update(octets=octets, sha256=sha)
        else:
            par_fichier[relatif] = {"fichier": relatif, "octets": octets, "sha256": sha}
    connus = {e["fichier"] for e in donnees["fichiers"]}
    donnees["fichiers"] += [par_fichier[f] for f in fichiers if f not in connus]
    donnees["nombre_fichiers_inventories"] = len(donnees["fichiers"])
    donnees.setdefault("revisions", []).append(
        {"date": date.today().isoformat(), "motif": MOTIF, "ajoutes": ajouts, "recalcules": maj}
    )
    return [
        (csv, "﻿" + fin.join([entete] + [lignes[n] for n in ordre]) + fin),
        (manifeste, json.dumps(donnees, ensure_ascii=False, indent=2) + "\n"),
    ], ajouts, maj


def trace(base, ajouts, maj):
    cible = base / "REVISIONS.md"
    entete = "" if cible.exists() else "# Révisions postérieures à la livraison\n"
    bloc = [f"\n## {date.today().isoformat()}\n", MOTIF + "\n"]
    if ajouts:
        bloc.append("\nFichiers ajoutés aux manifestes :\n" + "".join(f"- `{f}`\n" for f in ajouts))
    if maj:
        bloc.append("\nEmpreintes recalculées :\n" + "".join(f"- `{f}`\n" for f in maj))
    bloc.append("\nLes empreintes des autres fichiers sont inchangées.\n")
    return cible, entete + (cible.read_text(encoding="utf-8") if cible.exists() else "") + "".join(bloc)


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--verifier", action="store_true", help="afficher sans écrire")
    options = analyseur.parse_args()

    ecritures = []
    for dossier, fichiers in SUIVIS.items():
        base = RACINE / dossier
        ajouts, maj = [], []

        if (base / "INVENTAIRE_COMPLET.json").exists():
            cible, contenu, a, m = maj_inventaire_json(base, fichiers)
            ecritures.append((cible, contenu))
            ajouts += a
            maj += m
            cible, contenu, a, m = maj_sha256sums(base, fichiers)
            if cible:
                ecritures.append((cible, contenu))
        else:
            paires, a, m = maj_manifeste_csv(base, fichiers)
            ecritures += paires
            ajouts += a
            maj += m

        if ajouts or maj:
            ecritures.append(trace(base, ajouts, maj))
        print(f"{dossier} : {len(ajouts)} ajout(s), {len(maj)} empreinte(s) recalculée(s)")

    if options.verifier:
        print("Vérification seule : aucun fichier écrit.")
        return
    for cible, contenu in ecritures:
        cible.write_text(contenu, encoding="utf-8")
        print(f"écrit {cible.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
