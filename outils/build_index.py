#!/usr/bin/env python3
"""Génère les index HTML de navigation des kits de formation.

Un descripteur `kit.json` par formation décrit les livrables ; le conducteur et
l'index des travaux pratiques sont relus depuis les sources de chaque kit, via
une couche de normalisation, parce que les deux formations ne les stockent pas
sous le même schéma.

    python3 outils/build_index.py            # régénère tout
    python3 outils/build_index.py --verifier # contrôle sans écrire

Sorties : index.html à la racine, et <dossier>/00_OUVRIR_LES_SUPPORTS.html
pour chaque kit. Aucune ressource externe : les pages s'ouvrent en file://.
"""
from pathlib import Path
from html import escape
import argparse
import json
import re
import sys

RACINE = Path(__file__).resolve().parent.parent
KITS = ["formation_4_020/kit.json", "deep_learning_4_024/kit.json"]

BLEU, VERT, OCRE, ROUGE = "#23468C", "#238C33", "#8C6D23", "#A32F2F"

NATURES = {
    "Apport": BLEU,
    "Pratique": VERT,
    "Démonstration": OCRE,
    "Évaluation": ROUGE,
}


# --- normalisation des conducteurs ------------------------------------------
# Les deux kits décrivent le même objet sous deux schémas différents. On les
# ramène à : {jour, bloc, seg, minutes, nature, intitule, preuve}.

def _conducteur_4020(donnees):
    """`schedule` de contenus_diaporamas.json : [seg, jour, bloc, minutes, nature, intitulé]."""
    traduction = {"TP": "Pratique", "Apport": "Apport", "Évaluation": "Évaluation"}
    lignes = []
    for seg, jour, bloc, minutes, nature, intitule in donnees["schedule"]:
        lignes.append({
            "jour": jour, "bloc": bloc, "seg": seg, "minutes": minutes,
            "nature": traduction[nature], "intitule": intitule, "preuve": "",
        })
    return lignes


def _conducteur_normalise(donnees):
    """conducteur.json : bornes minutées, nature codée E/P/D/V et preuve attendue.

    Schéma partagé par les deux formations. La 4-024 n'utilise pas la nature V.
    """
    traduction = {"E": "Apport", "P": "Pratique", "D": "Démonstration", "V": "Évaluation"}
    lignes = []
    for ligne in donnees:
        lignes.append({
            "jour": ligne["day"], "bloc": ligne["block"], "seg": ligne.get("seg", ""),
            "minutes": ligne["minutes"], "nature": traduction[ligne["nature"]],
            "intitule": ligne["label"], "preuve": ligne.get("proof", ""),
            "_debut": ligne.get("start"), "_fin": ligne.get("end"),
        })
    return lignes


FORMATS_CONDUCTEUR = {"schedule_4020": _conducteur_4020, "conducteur": _conducteur_normalise}


def charger_conducteur(base, description, alertes):
    lignes = FORMATS_CONDUCTEUR[description["format"]](
        json.loads((base / description["source"]).read_text(encoding="utf-8"))
    )
    # Horaires relatifs au début de chaque journée : les pauses ne sont pas
    # comptées, donc on n'affiche pas d'heure d'horloge.
    curseur = {}
    for ligne in lignes:
        debut = curseur.get(ligne["jour"], 0)
        ligne["debut"], ligne["fin"] = debut, debut + ligne["minutes"]
        curseur[ligne["jour"]] = ligne["fin"]
        if ligne.get("_debut") is not None and ligne["_debut"] != debut:
            alertes.append(
                f"conducteur : bornes incohérentes jour {ligne['jour']}, "
                f"« {ligne['intitule']} » indique {ligne['_debut']} et le cumul donne {debut}"
            )
    return lignes


# --- normalisation des index de travaux pratiques ---------------------------

def charger_tp(base, tp):
    """Retourne (liste d'ateliers normalisés, colonnes de variantes).

    Deux dispositions coexistent : la 4-024 range un même notebook dans trois
    dossiers de rôle, la 4-020 nomme un fichier par rôle dans un dossier unique.
    Les deux produisent le même tableau à l'écran.
    """
    base_tp = Path(tp["dossier"])
    index = json.loads((base / tp["source"]).read_text(encoding="utf-8"))
    ateliers = []

    for entree in index:
        if tp["format"] == "index_tp":
            variantes = [
                (etiquette, Path(dossier) / entree["fichier"])
                for etiquette, dossier in tp["variantes"]
            ]
            meta = f"{entree['cellules']} cellules • {pluriel(entree['exercices'], 'exercice')}"
            note = ""
        else:
            variantes = [
                (etiquette, base_tp / entree["variantes"][cle] if entree["variantes"][cle] else None)
                for etiquette, cle in tp["variantes"]
            ]
            meta = (f"{entree['cellules']} cellules • {pluriel(entree['exercices'], 'exercice')}"
                    f" • blocs {', '.join(entree['blocs'])}")
            note = entree.get("note", "")

        ateliers.append({
            "id": entree["id"],
            "titre": entree["titre"],
            "meta": meta,
            "note": note,
            "variantes": [
                (etiquette, str(chemin) if chemin and (base / chemin).exists() else None)
                for etiquette, chemin in variantes
            ],
        })

    return ateliers, [etiquette for etiquette, _ in tp["variantes"]]


# --- rendu -------------------------------------------------------------------

STYLE = """
:root{--bleu:#23468C;--vert:#238C33;--encre:#0D0D0D;--gris:#58616e;--trait:#d9dfe8;--fond:#f5f6f8}
*{box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:var(--fond);color:var(--encre);line-height:1.6}
main{max-width:1060px;margin:0 auto;padding:24px 20px 48px}
header{border-top:7px solid var(--bleu);padding-top:26px;margin-bottom:28px}
h1{font-size:32px;line-height:1.2;margin:.2em 0}
h2{font-size:20px;margin:0 0 .5em}
h3{font-size:16px;margin:0 0 .4em}
a{color:var(--bleu)}
p{margin:.5em 0}
.meta{color:var(--gris);font-size:14px;margin:0}
.chiffres{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0 0;padding:0;list-style:none}
.chiffres li{background:#fff;border:1px solid var(--trait);border-radius:8px;padding:10px 16px;font-size:14px}
.chiffres b{display:block;font-size:21px;line-height:1.3}
nav.sommaire{margin:26px 0 0;font-size:14px}
nav.sommaire a{display:inline-block;margin:0 14px 6px 0}
section{margin:34px 0 0;scroll-margin-top:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}
article{background:#fff;border:1px solid var(--trait);border-radius:10px;padding:22px}
.btn{display:inline-block;background:var(--bleu);color:#fff;text-decoration:none;border-radius:5px;padding:8px 13px;margin:6px 10px 2px 0}
.lien-sec{display:inline-block;margin:6px 12px 2px 0;font-size:14px}
.panel{background:#fff;border-left:5px solid var(--vert);border-radius:0 10px 10px 0;padding:18px 24px}
details{background:#fff;border:1px solid var(--trait);border-radius:8px;padding:12px 16px;margin-top:14px}
summary{cursor:pointer;font-weight:bold}
.defile{overflow-x:auto;margin-top:12px}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--trait);vertical-align:top}
th{color:var(--gris);font-weight:normal;white-space:nowrap}
td.num{white-space:nowrap;color:var(--gris);font-variant-numeric:tabular-nums}
.badge{display:inline-block;border-radius:4px;padding:1px 8px;font-size:12px;color:#fff;white-space:nowrap}
ul.liens{list-style:none;padding:0;margin:12px 0 0}
ul.liens li{margin:9px 0}
.notes{font-size:14px;color:var(--gris)}
footer{margin-top:44px;border-top:1px solid var(--trait);padding-top:20px;font-size:14px;color:var(--gris)}
footer li{margin:7px 0}
@media print{body{background:#fff}.btn{background:none;color:var(--bleu);padding:0;text-decoration:underline}details{border:none}}
"""


def pluriel(nombre, mot):
    return f"{nombre} {mot}" + ("s" if nombre > 1 else "")


def duree(minutes):
    heures, reste = divmod(minutes, 60)
    return f"{heures} h {reste:02d}" if heures else f"{reste} min"


def horaire(minutes):
    return f"{minutes // 60}:{minutes % 60:02d}"


def liens_html(liens, base=""):
    morceaux = []
    for etiquette, cible, *principal in liens:
        classe = "btn" if (principal and principal[0]) else "lien-sec"
        morceaux.append(f'<a class="{classe}" href="{escape(base + cible)}">{escape(etiquette)}</a>')
    return "".join(morceaux)


def table_conducteur(lignes, avec_preuve):
    entetes = ["Minute", "Durée", "Bloc", "Nature", "Séquence"]
    if avec_preuve:
        entetes.append("Preuve attendue")
    rangs = [f"<tr>{''.join(f'<th>{h}</th>' for h in entetes)}</tr>"]
    for l in lignes:
        couleur = NATURES[l["nature"]]
        cellules = [
            f'<td class="num">{horaire(l["debut"])} → {horaire(l["fin"])}</td>',
            f'<td class="num">{l["minutes"]} min</td>',
            f'<td class="num">{escape(l["seg"] or l["bloc"])}</td>',
            f'<td><span class="badge" style="background:{couleur}">{escape(l["nature"])}</span></td>',
            f'<td>{escape(l["intitule"])}</td>',
        ]
        if avec_preuve:
            cellules.append(f'<td class="notes">{escape(l["preuve"]) or "—"}</td>')
        rangs.append(f"<tr>{''.join(cellules)}</tr>")
    return '<div class="defile"><table>' + "".join(rangs) + "</table></div>"


def table_tp(notebooks, colonnes):
    entetes = ["N°", "Atelier"] + colonnes
    rangs = [f"<tr>{''.join(f'<th>{escape(h)}</th>' for h in entetes)}</tr>"]
    for nb in notebooks:
        cellules = [
            f'<td class="num">{escape(nb["id"])}</td>',
            f'<td>{escape(nb["titre"])}<br><span class="notes">{escape(nb["meta"])}'
            + (f'<br>{escape(nb["note"])}' if nb["note"] else "")
            + '</span></td>',
        ]
        for etiquette, chemin in nb["variantes"]:
            cellules.append(
                f'<td>{f"""<a href="{escape(chemin)}">ouvrir</a>""" if chemin else "—"}</td>'
            )
        rangs.append(f"<tr>{''.join(cellules)}</tr>")
    return '<div class="defile"><table>' + "".join(rangs) + "</table></div>"


def compter(base, ressource):
    if "compter" not in ressource:
        return ""
    dossier = base / ressource["chemin"]
    if not dossier.is_dir():
        return ""
    nombre = sum(1 for f in dossier.glob(ressource["compter"]) if f.is_file())
    return f"{nombre} fichiers • "


def page_kit(base, kit, alertes):
    conducteur = charger_conducteur(base, kit["conducteur"], alertes)
    avec_preuve = any(l["preuve"] for l in conducteur)
    notebooks, colonnes = charger_tp(base, kit["tp"])

    total = sum(l["minutes"] for l in conducteur)
    pratique = sum(l["minutes"] for l in conducteur if l["nature"] == "Pratique")
    jours = sorted({l["jour"] for l in conducteur})

    heures_declarees = int(re.search(r"(\d+)\s*heures", kit["duree"]).group(1))
    if total != heures_declarees * 60:
        alertes.append(
            f'{kit["ref"]} : le conducteur totalise {total} minutes, '
            f'le descripteur annonce {heures_declarees} heures'
        )

    parties = []
    parties.append(f"""<header>
<p class="meta">P2Enjoy Studio · Référence {escape(kit['ref'])} · {escape(kit['duree'])} · Niveau {escape(kit['niveau'])}</p>
<h1>{escape(kit['titre'])}</h1>
<p><strong>{escape(kit['accroche'])}</strong></p>
<p>{escape(kit['resume'])}</p>
<p class="meta">{escape(kit['session'])}</p>
<ul class="chiffres">
<li><b>{duree(total)}</b>face-à-face net</li>
<li><b>{duree(pratique)}</b>production pratique, {100 * pratique / total:.1f} %</li>
<li><b>{len(jours)}</b>journée{'s' if len(jours) > 1 else ''}</li>
<li><b>{len(notebooks)}</b>atelier{'s' if len(notebooks) > 1 else ''} notebook</li>
</ul>
<nav class="sommaire"><a href="#documents">Documents</a><a href="#journees">Journées et conducteur</a><a href="#tp">Travaux pratiques</a><a href="#ressources">Ressources et sources</a><a href="#controles">Contrôles</a></nav>
</header>""")

    cartes = "".join(
        f'<article><h2>{escape(d["titre"])}</h2><p class="meta">{escape(d["meta"])}</p>{liens_html(d["liens"])}</article>'
        for d in kit["documents"]
    )
    parties.append(f'<section id="documents"><h2>Documents</h2><div class="grid">{cartes}</div></section>')

    blocs_jours = []
    if "presentation_complete" in kit:
        pc = kit["presentation_complete"]
        blocs_jours.append(
            f'<article><h2>{escape(pc["titre"])}</h2><p class="meta">{escape(pc["meta"])}</p>{liens_html(pc["liens"])}</article>'
        )
    for journee in kit["journees"]:
        lignes = [l for l in conducteur if l["jour"] == journee["num"]]
        minutes = sum(l["minutes"] for l in lignes)
        pratique_jour = sum(l["minutes"] for l in lignes if l["nature"] == "Pratique")
        blocs_jours.append(f"""<article>
<h2>Jour {journee['num']} — {escape(journee['titre'])}</h2>
<p class="meta">{escape(journee['meta'])} · {duree(minutes)} · {duree(pratique_jour)} de pratique</p>
{liens_html(journee['liens'])}
<details><summary>Conducteur minuté du jour {journee['num']} ({len(lignes)} séquences)</summary>
{table_conducteur(lignes, avec_preuve)}
<p class="notes">{escape(kit['conducteur']['note'])}</p>
</details></article>""")
    parties.append(
        f'<section id="journees"><h2>Journées et conducteur</h2><div class="grid">{"".join(blocs_jours)}</div></section>'
    )

    tp = kit["tp"]
    fichiers = "".join(
        f'<li><a href="{escape(cible)}">{escape(etiquette)}</a></li>' for etiquette, cible in tp["fichiers"]
    )
    parties.append(f"""<section id="tp"><h2>Travaux pratiques</h2>
<div class="panel">
<p>{escape(tp['intro'])}</p>
<p><a class="btn" href="{escape(tp['lisezmoi'])}">Instructions et installation</a></p>
{table_tp(notebooks, colonnes)}
<h3 style="margin-top:22px">Données, modules et dépendances</h3>
<ul class="liens">{fichiers}</ul>
</div></section>""")

    ressources = "".join(
        f'<article><h3>{escape(r["titre"])}</h3>'
        f'<p class="meta">{compter(base, r)}<a href="{escape(r["chemin"])}">{escape(r["chemin"])}</a></p>'
        f'<p class="notes">{escape(r["note"])}</p></article>'
        for r in kit["ressources"]
    )
    parties.append(f'<section id="ressources"><h2>Ressources et sources</h2><div class="grid">{ressources}</div></section>')

    controles = "".join(
        f'<li><a href="{escape(cible)}">{escape(etiquette)}</a></li>' for etiquette, cible in kit["controles"]
    )
    parties.append(
        f'<section id="controles"><h2>Contrôles et intégrité</h2><div class="panel"><ul class="liens">{controles}</ul></div></section>'
    )

    avertissements = "".join(f"<li>{escape(a)}</li>" for a in kit["avertissements"])
    parties.append(
        f"<footer><h2>Limites déclarées</h2><ul>{avertissements}</ul>"
        "<p>Page générée par <code>outils/build_index.py</code> depuis <code>kit.json</code> "
        "et les sources du kit. Ne pas la modifier à la main.</p></footer>"
    )

    return enveloppe(f"{kit['titre']} | Référence {kit['ref']}", "".join(parties)), {
        "total": total, "pratique": pratique, "jours": len(jours), "notebooks": len(notebooks),
    }


def page_racine(kits):
    cartes = []
    for base, kit, mesures in kits:
        cartes.append(f"""<article>
<p class="meta">Référence {escape(kit['ref'])} · {escape(kit['duree'])} · Niveau {escape(kit['niveau'])}</p>
<h2>{escape(kit['titre'])}</h2>
<p>{escape(kit['accroche'])}</p>
<p class="notes">{duree(mesures['total'])} de face-à-face, dont {duree(mesures['pratique'])} de pratique
({100 * mesures['pratique'] / mesures['total']:.1f} %) · {mesures['notebooks']} ateliers notebook</p>
<a class="btn" href="{escape(kit['dossier'])}/{escape(kit['index'])}">Ouvrir le kit</a>
<a class="lien-sec" href="{escape(kit['dossier'])}/README.md">README</a>
</article>""")
    corps = f"""<header>
<p class="meta">P2Enjoy Studio</p>
<h1>Kits de formation</h1>
<p>Deux kits complets et autonomes. Chaque index s'ouvre localement, sans compte ni accès réseau.</p>
</header>
<section><div class="grid">{''.join(cartes)}</div></section>
<footer><p>Les limites de recette propres à chaque formation sont déclarées en bas de son index.
Page générée par <code>outils/build_index.py</code>.</p></footer>"""
    return enveloppe("Kits de formation | P2Enjoy Studio", corps)


def enveloppe(titre, corps):
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(titre)}</title><style>{STYLE}</style></head>"
        f"<body><main>{corps}</main></body></html>"
    )


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--verifier", action="store_true", help="contrôler sans écrire")
    options = analyseur.parse_args()

    alertes, produits, ecrits = [], [], []
    for chemin in KITS:
        descripteur = RACINE / chemin
        base = descripteur.parent
        kit = json.loads(descripteur.read_text(encoding="utf-8"))
        html, mesures = page_kit(base, kit, alertes)
        produits.append((base, kit, mesures))
        ecrits.append((base / kit["index"], html))

    ecrits.append((RACINE / "index.html", page_racine(produits)))

    for _, kit, mesures in produits:
        print(f"{kit['ref']} : {mesures['jours']} jours, {mesures['total']} min "
              f"dont {mesures['pratique']} min de pratique "
              f"({100 * mesures['pratique'] / mesures['total']:.1f} %), "
              f"{mesures['notebooks']} ateliers")

    for alerte in alertes:
        print(f"ALERTE {alerte}", file=sys.stderr)

    if options.verifier:
        print("Vérification seule : aucun fichier écrit.")
    else:
        for cible, html in ecrits:
            cible.write_text(html, encoding="utf-8")
            print(f"écrit {cible.relative_to(RACINE)} ({len(html):,} octets)".replace(",", " "))

    return 1 if alertes else 0


if __name__ == "__main__":
    raise SystemExit(main())
