# Travaux pratiques 4-020

Données Novalia 100 % synthétiques. Aucun compte externe, aucune donnée de client et aucun achat de service n'est nécessaire pour les notebooks.

## Démarrage
Dans un environnement Python 3.11 ou ultérieur, créer un environnement virtuel puis installer les dépendances. Les bibliothèques de calcul sont épinglées sur les versions effectivement utilisées pour la validation du livrable.

```bash
python -m venv .venv
# Linux/macOS : source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m jupyter lab
```

Ouvrir `01_Atelier_Novalia_participant.ipynb`. Ne pas distribuer le corrigé exécuté avant le débrief. Les fichiers de résultats pré-calculés permettent une variante sans code. Ils portent exclusivement sur un jeu fictif de test.

Le notebook corrigé et la simulation de contrat ont été exécutés de bout en bout dans l'environnement de production des livrables. L'installation et l'interface graphique Power BI Desktop ne sont pas disponibles dans cet environnement : aucun fichier PBIX n'est prétendu testé ou fourni.

## Réexécution
Le script `generer_donnees.py` recrée les CSV avec la graine 4020. Relancer ensuite le notebook pour actualiser les exports. Ne pas modifier les jeux de données sans recalculer les résultats.

## Limites
Les scores ne sont pas validés pour une utilisation commerciale réelle. Les modèles ne démontrent pas la valeur causale d'une campagne. La séparation aléatoire est adaptée à la simulation de clients indépendants, pas automatiquement aux historiques réels.
