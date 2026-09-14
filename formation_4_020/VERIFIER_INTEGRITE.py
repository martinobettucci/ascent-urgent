#!/usr/bin/env python3
"""Vérifie l’intégrité des fichiers après extraction. Aucun accès réseau."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / "INVENTAIRE_COMPLET.json").read_text(encoding="utf-8"))
errors = []
for item in manifest["fichiers"]:
    path = root / item["chemin"]
    if not path.is_file():
        errors.append("Fichier absent : " + item["chemin"])
        continue
    data = path.read_bytes()
    if len(data) != item["octets"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        errors.append("Fichier modifié : " + item["chemin"])
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(str(len(manifest["fichiers"])) + " fichiers vérifiés, tous identiques à leur empreinte.")
