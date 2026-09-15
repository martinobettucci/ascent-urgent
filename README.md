# Kits de formation P2Enjoy

Deux kits complets et autonomes. Ouvrir [index.html](index.html), ou l’index de chaque kit.

| Kit | Référence | Durée | Index |
| --- | --- | --- | --- |
| Intelligence artificielle et systèmes d’information | 4-020 | 12 h, 2 journées | [ouvrir](formation_4_020/00_OUVRIR_LES_SUPPORTS.html) |
| Deep Learning par la pratique | 4-024 | 18 h, 3 journées | [ouvrir](deep_learning_4_024/00_OUVRIR_LES_SUPPORTS.html) |

## Outils

Les index HTML sont générés, jamais écrits à la main. Chaque kit est décrit par un `kit.json` ; le conducteur, la bibliographie et l’index des ateliers sont relus depuis les sources du kit à travers une couche de normalisation, parce que les deux formations ne les stockent pas sous le même schéma.

| Commande | Effet |
| --- | --- |
| `python3 outils/build_index.py` | régénère `index.html` et les deux index de kit |
| `python3 outils/build_index.py --verifier` | contrôle les totaux et les bornes du conducteur, sans écrire |
| `python3 outils/build_methodo_4020.py` | régénère les descripteurs normalisés de la 4-020 |
| `python3 outils/mettre_a_jour_integrite.py` | réaligne les manifestes SHA-256 sur les fichiers générés |

Le générateur recalcule les durées depuis le conducteur et signale tout écart avec la durée annoncée dans `kit.json`, ainsi que toute incohérence entre les bornes stockées et les cumuls. Aucune ressource externe n’est chargée : les pages s’ouvrent en `file://`.

## Intégrité

Les supports pédagogiques livrés ne sont pas modifiés. Les seuls fichiers ajoutés aux manifestes sont les index générés, les descripteurs et les renvois vers l’index depuis les points d’entrée ; chaque passage est tracé dans le `REVISIONS.md` du kit concerné.

```bash
python3 formation_4_020/VERIFIER_INTEGRITE.py
```

https://p2enjoy.studio
