# Rapport de production et de recette

## Livrables ouvrables

Quatre PowerPoint : trois journées de 42 diapositives et un assemblage de 126. Toutes les diapositives contiennent des notes orateur. Chaque présentation dispose de son export PDF.

Cinq documents Word et leurs PDF : dossier pédagogique de 56 pages ; guide formateur de 46 pages ; cahier participant de 26 pages ; évaluation formateur et évaluation participant de 6 et 5 pages respectivement. Les comptes de pages sont ceux des PDF livrés.

Les figures sont intégrées aux documents et diapositives. Les sources SVG/PNG sont fournies. Les figures conceptuelles sont explicitement distinguées des sorties issues des notebooks.

## Recette des travaux pratiques

Les 11 corrigés ont été exécutés sans erreur sur CPU, chacun depuis un noyau neuf. Les copies exécutées sont dans `corriges_executes`. Les résultats et graphiques sont conservés. Détails et durées dans `recette_notebooks.json`.

**Limite :** TensorFlow n’était pas installé ; sa branche conditionnelle n’a pas été exécutée. Le moteur Keras de cette recette est PyTorch. Les tests ne valent ni recette d’un poste institutionnel, ni validation GPU, ni homologation métier. Le projet final a été exécuté dans son parcours par défaut ; les variantes restent à vérifier avant une animation fondée sur un autre parcours.

## Contrôles de fichiers

Intégrité ZIP interne des DOCX et PPTX vérifiée ; nombre de notes égal au nombre de diapositives ; PDF ouverts avec PyMuPDF ; contrôle des mots hors page et pages vides ; contrôle visuel des planches de rendu avec corrections de mise en page. Les empreintes SHA-256 du paquet figurent dans `MANIFESTE_SHA256.json` à la racine.

## Publication

Ces livrables ont été créés dans la conversation. Aucun nouveau commit contenant ces documents n’a été réalisé dans GitHub durant cette correction. Les fichiers d’import précédents ne constituent pas une preuve de publication des supports.
