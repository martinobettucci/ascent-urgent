# Travaux pratiques, formation 4-024

Les notebooks apprenants, corrigés et corrigés exécutés sont séparés. Les fichiers de données et `modules/atelier.py` doivent rester dans cette arborescence. Les résultats de référence sont dans `resultats` et ne constituent pas des performances métier.

## Environnement CPU

La recette a été effectuée avec Python 3.13.5 et PyTorch 2.10.0+cpu, Keras 3.13.2 (moteur PyTorch). Les 11 corrigés ont été exécutés dans un noyau neuf chacun. La branche TensorFlow conditionnelle n’a pas été exécutée : TensorFlow n’était pas installé. L’installation depuis un poste vierge, le GPU, Colab et les variantes des quatre projets n’ont pas tous été recettés. Les chiffres de recette sont limités à l’environnement décrit.

Sur un poste Python 3.11 autorisé, préparer l’environnement avant la formation :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-cpu.txt
jupyter lab
```

Sous Windows, activer `.venv\Scripts\activate` à la place de la commande `source`. L’installation demande un accès réseau autorisé ; l’exécution du socle des exercices utilise ensuite les données locales. Aucun téléchargement de données ne se produit dans les notebooks.

Ouvrir d’abord `apprenants/00_Vérifier_son_environnement.ipynb`. Ne pas changer de moteur Keras après son import. Les cellules d’exercice du cahier apprenant sont volontairement à compléter. Les corrections et sorties de recette sont destinées au formateur.

## Données et sécurité

Les données de dossiers, priorisation, documents et séries sont synthétiques. Les chiffres manuscrits 8 × 8 proviennent du jeu public scikit-learn/UCI. Voir `donnees/FICHES_DONNEES.json`. Aucun fichier personnel ou fiscal réel ne doit être chargé dans un service externe.
