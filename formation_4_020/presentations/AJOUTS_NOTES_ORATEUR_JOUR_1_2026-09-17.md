# Additif notes orateur, Formation 4-020, Jour 1

Formation : Intelligence artificielle appliquée aux systèmes d’information de l’entreprise
Référence : 4-020
Session : Ascent Formation, Bourges, 17 septembre 2026
Destination recommandée : `formation_4_020/presentations/Formation_4_020_Jour_1.pptx`
Mode d’intégration : ajout à la fin des notes orateur existantes, sans suppression, sans réécriture et sans remplacement du contenu actuel.
Préfixe recommandé pour chaque ajout : `AJOUT PÉDAGOGIQUE 17/09/2026`

## Règle d’intégration

Ouvrir le PowerPoint du Jour 1 et ajouter les blocs ci-dessous à la fin des notes orateur des diapositives indiquées. Les diapositives, titres, visuels, textes visibles, séquences et durées restent inchangés. Les notes existantes restent conservées intégralement.

## J1-001, ouverture

`AJOUT PÉDAGOGIQUE 17/09/2026`

Dire explicitement : « Ce n’est pas un cours sur les algorithmes. Le fil rouge de la journée est : comment une entreprise passe de données dispersées à une décision utile, mesurable et gouvernée. » Présenter Novalia comme un terrain d’entraînement fictif, avec données synthétiques et décisions réalistes.

Phrase de transition : « À chaque fois que nous parlerons d’IA aujourd’hui, je vous demanderai quatre choses : quelle décision, quelles données, quel résultat, et qui agit ensuite. »

## J1-002, objectifs

`AJOUT PÉDAGOGIQUE 17/09/2026`

Reformuler les objectifs en livrables visibles : cadrer une décision métier en une phrase, relier les données à cette décision, arbitrer un compromis d’erreur, concevoir un usage vérifiable dans le SI. Question : « Quelle décision répétitive aimeriez-vous mieux prendre dans votre organisation ? » Ne pas accepter « mettre de l’IA dans le CRM » sans relance : qui reçoit le résultat, à quel moment, quelle action change ?

## J1-003, agenda

`AJOUT PÉDAGOGIQUE 17/09/2026`

Rassurer le groupe : les apports courts servent à rendre les ateliers faisables. Les ateliers sont la preuve d’apprentissage. Dire : « Vous n’avez pas besoin de retenir tous les mots techniques dès le départ. Vous devez surtout apprendre à poser les bonnes questions avant d’acheter, développer ou déployer une solution d’IA. »

## J1-004, diagnostic initial

`AJOUT PÉDAGOGIQUE 17/09/2026`

Présenter le diagnostic comme un révélateur de réflexes, pas comme un contrôle. Déroulé : trois minutes seul, quatre minutes en binôme, puis correction collective. Relever les confusions : API confondue avec IA, entraînement confondu avec utilisation, exactitude confondue avec qualité, quantité de données confondue avec valeur, score confondu avec décision.

## J1-005, modèle et SI

`AJOUT PÉDAGOGIQUE 17/09/2026`

Exemple : un ticket client arrive dans un outil support, il est rattaché à un compte, qualifié, routé vers une équipe, puis traité. L’IA peut aider à classer ou prioriser, mais elle ne remplace pas le dossier, les droits, l’équipe, la règle de traitement, ni la responsabilité. Question : « Si le score reste dans un fichier que personne ne consulte, quelle valeur produit-il ? » Réponse attendue : aucune valeur opérationnelle.

## J1-006, observation et action

`AJOUT PÉDAGOGIQUE 17/09/2026`

Utiliser « 38,7 °C ». Demander : « 38,7 de quoi ? Sur quel composant ? Mesuré quand ? Avec quel capteur ? Quelle est la plage normale ? » Message : une donnée seule ne dit presque rien. Le contexte transforme la donnée en information. Plusieurs informations soutiennent une hypothèse. Une hypothèse déclenche une action, par exemple inspecter avant de remplacer.

## J1-007, donnée, algorithme, modèle, système IA

`AJOUT PÉDAGOGIQUE 17/09/2026`

Analogie : l’algorithme est une recette, le modèle est un plat préparé avec des ingrédients donnés, le système IA est le restaurant complet avec cuisine, salle, règles, serveurs, clients et procédures. Une erreur peut venir de la donnée, de l’algorithme, du modèle, de l’interface, de la règle métier ou de l’organisation.

## J1-008, IA et chatbot

`AJOUT PÉDAGOGIQUE 17/09/2026`

Donner trois exemples silencieux : filtre anti-fraude, prévision de panne, recommandation de contenu ou d’article. Question : « Est-ce que c’est moins de l’IA parce que cela ne parle pas ? » Réponse attendue : non.

## J1-009, familles de problèmes

`AJOUT PÉDAGOGIQUE 17/09/2026`

Faire partir la famille technique de la question : « Combien ? » implique régression ou prévision. « Oui ou non ? » implique classification. « À quelle catégorie ? » implique classification multi-classes. « Qui se ressemble ? » implique regroupement. « Quoi proposer ? » implique recommandation. « Que produire ? » implique génération. « Est-ce inhabituel ? » implique détection d’anomalie. Transition : « Avant de choisir un outil, nous devons nommer le type de décision. »

## Format standard pour tous les ateliers

`AJOUT PÉDAGOGIQUE 17/09/2026`

Avant chaque atelier, annoncer : ce que vous devez produire, comment vous allez le faire, un exemple commencé au tableau, et comment savoir que l’atelier est terminé.

## A01, classer les cas métiers

`AJOUT PÉDAGOGIQUE 17/09/2026`

Produire quatre cases par situation : question métier, type de sortie attendue, données nécessaires, action qui suit. Exemple : « Anticiper un départ client dans trente jours ». Sortie : oui, non ou score. Données : ancienneté, tickets support, retards de paiement, usage digital, satisfaction. Action : prioriser une file de rappel. Critère de fin : un autre groupe comprend pourquoi la famille de traitement a été choisie. Si le groupe écrit seulement « IA » ou « réseau de neurones », ce n’est pas terminé. Question finale : quel cas peut être traité sans Machine Learning ? Exemple attendu : une alerte sur seuil contractuel explicite.

## A02, cartographier Novalia

`AJOUT PÉDAGOGIQUE 17/09/2026`

Produire un schéma de chaîne de décision : source des données, préparation, score ou résultat, lecteur du résultat, action déclenchée, mesure. Chaque flèche porte une donnée ou une action. Interdiction d’écrire une boîte « IA magique » sans préciser les entrées et sorties. Exemple : CRM, facturation et support vers nettoyage, puis score de départ, puis liste priorisée dans le CRM, puis appel commercial, puis mesure du taux de contact et de rétention. Critère de fin : une personne extérieure peut suivre un dossier client depuis la source jusqu’à l’action.

## A03, Netflix et Google Play

`AJOUT PÉDAGOGIQUE 17/09/2026`

Produire cinq cases : action utilisateur, signaux utilisés, mécanisme de personnalisation, mesure de valeur, garde-fous. Ne pas copier Netflix ou Google Play, extraire une logique transposable. Exemple Netflix : regarder ou ignorer une proposition, historique et interactions, recommandation et expérimentation, engagement et satisfaction, diversité et effet tunnel. Exemple Google Play : installer ou non une application, historique et requête, combinaison de mémorisation et généralisation, installation et usage, qualité et sécurité. Critère de fin : formuler une idée transposable à Novalia sans promettre un gain non prouvé.

## A04, arbitrer les erreurs de fraude

`AJOUT PÉDAGOGIQUE 17/09/2026`

Écrire au tableau : 10 000 paiements, dont 100 fraudes. Politique A : 80 fraudes détectées, 20 ratées, 400 fausses alertes, 480 alertes à traiter. Politique B : 65 détectées, 35 ratées, 100 fausses alertes, 165 alertes à traiter. Hypothèse : une fraude ratée coûte 100 €, une fausse alerte coûte 5 €. A : 20 × 100 € + 400 × 5 € = 4 000 €. B : 35 × 100 € + 100 × 5 € = 4 000 €. Message : même coût total, mais charge et expérience client différentes. Variante : si la fausse alerte coûte 10 €, A coûte 6 000 € et B coûte 4 500 €. Phrase mémo : « On ne choisit pas le modèle le plus malin, on choisit le compromis d’erreur que le métier peut assumer. »

## A05, canevas de valeur métier

`AJOUT PÉDAGOGIQUE 17/09/2026`

Produire six cases : problème, décision, données, mesure de réussite, référence actuelle, critère d’abandon. Exemple : prioriser les clients à rappeler. Problème : l’équipe ne peut pas rappeler tout le monde. Décision : qui rappeler en premier. Données : usage, tickets, satisfaction, ancienneté, paiement. Mesure : taux de contact, rétention, marge nette après coût de l’action. Référence actuelle : liste triée par ancienneté ou intuition. Critère d’abandon : pas d’amélioration mesurable, coût trop élevé ou risque non acceptable. Trois portes : utile, faisable, acceptable.

## A06, audit qualité Novalia

`AJOUT PÉDAGOGIQUE 17/09/2026`

Produire une table d’anomalies : anomalie, règle de détection, risque, correction possible, responsable. Ouvrir `novalia_audit_qualite.csv`. Chercher impossible, incohérent, manquant, dupliqué ou temporellement suspect. Exemples : dépense mensuelle négative, ancienneté négative, type de contrat avec espaces et casse incohérente, satisfaction à 18, identifiant client dupliqué, valeur manquante, date de rafraîchissement ancienne. Point clé : `cancellation_request_date` est postérieure au snapshot pour certains clients. Si elle est utilisée comme variable d’entrée pour prédire le départ, le modèle apprend une information du futur. Question : « Quelle anomalie vous fait arrêter l’entraînement immédiatement ? » Réponse attendue : variable du futur ou fuite temporelle.

## A07, RACI et risques

`AJOUT PÉDAGOGIQUE 17/09/2026`

RACI : Responsible, celui qui fait. Accountable, celui qui tranche et porte la responsabilité finale. Consulted, ceux qu’on consulte avant. Informed, ceux qu’on informe après. Règle d’or : un seul Accountable par décision. Produire une matrice RACI et une fiche incident : problème, signal d’alerte, qui agit, qui décide l’arrêt ou le repli, qui est consulté, qui est informé. Exemple : scores incohérents après migration CRM. Signal : hausse brutale des scores élevés ou chute de performance. Responsible : data ou IT opérationnel. Accountable : responsable métier ou DSI désigné, mais un seul tranche. Consulted : juridique, sécurité, métier, data. Informed : équipes commerciales et support. Question finale : « Qui a l’autorité d’arrêter le système si les scores deviennent incohérents ? »

## Contrôle qualité après intégration

Vérifier que le fichier original n’est pas écrasé, que les 75 diapositives du Jour 1 sont toujours présentes, que les notes existantes sont conservées, que chaque ajout porte le préfixe `AJOUT PÉDAGOGIQUE 17/09/2026`, qu’aucun texte visible sur les slides n’a été modifié, que les PDF existants ne sont pas modifiés sauf demande explicite, et que ce fichier additif reste présent dans le kit pour traçabilité.
