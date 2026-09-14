from pathlib import Path
import json,re,math,datetime,fitz,os
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(os.environ.get('FORMATION_ROOT','/mnt/data/formation_4_020'));OUT=ROOT/'documents';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'sources_production/contenus_diaporamas.json').read_text())
S=D['sources'];R=json.loads((ROOT/'travaux_pratiques/resultats_reference.json').read_text())
BLUE='23468C';GREEN='238C33';INK='0D0D0D';PALE='F1F5FA'

def clean(t):return str(t or '').replace('—',': ').replace('–',', ')
def p(doc,text,style=None,bold=False):
 q=doc.add_paragraph(style=style);r=q.add_run(clean(text));r.bold=bold;return q

def tag(doc,text):
 q=p(doc,text);q.paragraph_format.space_after=Pt(8)
 for r in q.runs:r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREEN)
 return q

def shade(cell,fill):
 tcPr=cell._tc.get_or_add_tcPr();e=OxmlElement('w:shd');e.set(qn('w:fill'),fill);tcPr.append(e)

def table(doc,rows,widths=None,blanks=False):
 tab=doc.add_table(rows=0,cols=max(len(r) for r in rows));tab.style='Table Grid';tab.autofit=False
 if widths:
  for col,ww in zip(tab.columns,widths):col.width=Cm(ww)
 for i,row in enumerate(rows):
  cells=tab.add_row().cells
  for j,t in enumerate(row):
   cells[j].text=clean(t)
   if i==0:shade(cells[j],BLUE)
   elif i%2:shade(cells[j],PALE)
   for q in cells[j].paragraphs:
    q.paragraph_format.space_after=Pt(5);q.paragraph_format.space_before=Pt(5)
    for run in q.runs:
     run.font.size=Pt(9 if len(rows)>9 else 9.5)
     if i==0:run.font.color.rgb=RGBColor(255,255,255);run.bold=True
  trpr=tab.rows[-1]._tr.get_or_add_trPr();nosplit=OxmlElement('w:cantSplit');trpr.append(nosplit)
  if i==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  if blanks and i:tab.rows[-1].height=Cm(.92)
 return tab

def note(doc,label,text):
 q=doc.add_paragraph();q.paragraph_format.space_before=Pt(6);q.paragraph_format.space_after=Pt(9)
 pp=q._p.get_or_add_pPr();border=OxmlElement('w:pBdr');left=OxmlElement('w:left');left.set(qn('w:val'),'single');left.set(qn('w:sz'),'18');left.set(qn('w:color'),GREEN);border.append(left);pp.append(border)
 q.paragraph_format.left_indent=Cm(.25)
 r=q.add_run(label+'  ');r.bold=True;r.font.color.rgb=RGBColor.from_string(BLUE);q.add_run(clean(text));return q

def heading(doc,t,level=1):
 h=doc.add_heading(clean(t),level);return h

def cover(title,subtitle,kind):
 doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.85);sec.bottom_margin=Cm(1.8);sec.left_margin=Cm(1.85);sec.right_margin=Cm(1.85);sec.header_distance=Cm(.7);sec.footer_distance=Cm(.75)
 normal=doc.styles['Normal'];normal.font.name='Liberation Sans';normal.font.size=Pt(10.5);normal.font.color.rgb=RGBColor.from_string(INK);normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.widow_control=True
 for lev,size in [(1,24),(2,16),(3,12)]:
  st=doc.styles[f'Heading {lev}'];st.font.name='Liberation Sans';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string(BLUE);st.paragraph_format.space_before=Pt(15 if lev>1 else 20);st.paragraph_format.space_after=Pt(9);st.paragraph_format.keep_with_next=True
 doc.styles['Heading 1'].paragraph_format.page_break_before=True
 for sn in ['Header','Footer']:
  doc.styles[sn].font.name='Liberation Sans';doc.styles[sn].font.size=Pt(8);doc.styles[sn].font.color.rgb=RGBColor.from_string(BLUE)
 hp=sec.header.paragraphs[0];hp.text='P2ENJOY STUDIO  |  FORMATION 4-020  |  IA & SYSTÈMES D’INFORMATION'
 fp=sec.footer.paragraphs[0];fp.text='https://p2enjoy.studio';fp.add_run('                                          '+kind+'  |  ')
 fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld)
 p(doc,'P2ENJOY STUDIO',bold=True).runs[0].font.color.rgb=RGBColor.from_string(GREEN)
 p(doc,'COLLECTION FORMATION  /  LOT 4')
 for _ in range(3):p(doc,'')
 q=p(doc,title,bold=True);q.runs[0].font.size=Pt(34);q.runs[0].font.color.rgb=RGBColor.from_string(BLUE)
 p(doc,subtitle).runs[0].font.size=Pt(17)
 p(doc,'Intelligence artificielle appliquée aux systèmes d’information de l’entreprise').runs[0].font.size=Pt(18)
 p(doc,'Référence 4-020 • Niveau SAME : Application (A) • 12 heures sur 2 jours',bold=True)
 note(doc,'Périmètre','Aucun client ni aucune date de session n’est attribué. Le référentiel fourni est conservé ; les modalités détaillées sont des choix de conception pédagogique.')
 p(doc,'Version de production : 14 septembre 2026. Les exemples Novalia et les jeux de données sont entièrement synthétiques. Les cas externes sont distingués des simulations et documentés dans le corpus de sources.')
 doc.core_properties.author='P2Enjoy Studio';doc.core_properties.title=title;doc.core_properties.subject='Formation 4-020, IA et systèmes d’information';doc.core_properties.language='fr-FR'
 return doc

def refs(doc,ids):
 if not ids:return
 text='Sources : '+' ; '.join('['+r+'] '+S[r][0] for r in ids if r in S)
 q=p(doc,text)
 for run in q.runs:run.font.size=Pt(8);run.font.color.rgb=RGBColor.from_string('586777')

FIG={}
def figures():
 selected={'J1-005','J1-006','J1-008','J1-013','J1-014','J1-015','J1-016','J1-017','J1-019','J1-020','J1-028','J1-043','J1-053','J1-056','J2-010','J2-018','J2-021','J2-028','J2-030','J2-033','J2-037','J2-044','J2-050','J2-053','J2-055'}
 for day in (1,2):
  fp=ROOT/f'presentations/Formation_4_020_Jour_{day}.pdf'
  if not fp.exists():continue
  pdf=fitz.open(fp);arr=[s for s in D['slides'] if s['day']==day]
  for i,s in enumerate(arr):
   if s['id'] not in selected:continue
   page=pdf[i];path=ROOT/f'illustrations/{s["id"]}.png';clip=fitz.Rect(36,134,920,451)
   page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),clip=clip).save(str(path))
   from PIL import Image,ImageDraw,ImageFont
   im=Image.open(path).convert('RGB');canvas=Image.new('RGB',(im.width,im.height+28),'white');canvas.paste(im,(0,0));ImageDraw.Draw(canvas).text((12,im.height+5),'https://p2enjoy.studio',fill='#23468C');canvas.save(path);FIG[s['id']]=path

def figure(doc,sid,title):
 if sid not in FIG:return
 doc.add_picture(str(FIG[sid]),width=Cm(16.7));q=p(doc,f'Figure {sid}. {title}. Schéma pédagogique original, version éditable dans le PowerPoint.')
 q.paragraph_format.space_after=Pt(12)
 for r in q.runs:r.italic=True;r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('586777')

ACT=[
 ('A01','Classer huit situations métier',30,'Une proposition de famille de traitement est justifiée par la question, la cible et l’usage.',
 [('Finance','Repérer un paiement suspect.'),('Support','Affecter un ticket à la bonne équipe.'),('Marketing','Anticiper un départ dans trente jours.'),('Commerce','Proposer trois articles pertinents.'),('Opérations','Prévoir la quantité vendue demain.'),('IT','Repérer un comportement inhabituel dans les journaux.'),('RH','Classer des documents de formation, sans sélectionner des candidats.'),('Achats','Alerter lorsque le montant dépasse un seuil contractuel explicite.')],
 ['Famille proposée','Cible ou sortie','Données disponibles','Action et responsable'],
 'Classification supervisée si les cas historiques sont étiquetés ; recommandation pour le commerce ; régression ou prévision temporelle pour les ventes ; détection d’anomalies pour les journaux ; règles déterministes pour un seuil contractuel stable. Accepter les variantes justifiées. Un simple classement documentaire RH n’équivaut pas à une décision automatisée sur les personnes.'),
 ('A02','Cartographier la chaîne de décision Novalia',30,'Un autre groupe peut suivre un dossier de sa source à la mesure du résultat.',
 [('Contexte','Novalia dispose d’un CRM, d’un ERP, d’un ticketing, d’un site marchand et d’un entrepôt analytique.'),('Mission','Choisir une décision répétitive et dessiner la chaîne de bout en bout.'),('Contraintes','Chaque flèche porte le type de donnée, la fréquence et le destinataire. Ne pas supposer qu’un score déclenche seul une décision.')],
 ['Source et donnée','Préparation','Score ou résultat','Règle et action','Indicateur métier'],
 'Exemple : ticket entrant et texte disponible à t₀ ; nettoyage et contrôle des droits ; classification de l’équipe ; proposition au conseiller, avec revue si faible confiance ; mesure du temps de routage, de la réaffectation et du délai total. Une catégorie connue seulement après clôture peut servir de cible, pas d’entrée à t₀.'),
 ('A03','Comparer Netflix et Google Play',30,'L’analyse distingue le modèle, le système de recommandation et la preuve d’impact.',
 [('Netflix','L’article de Gomez-Uribe et Hunt (2015) décrit plusieurs algorithmes articulés à la présentation du catalogue et à l’expérimentation. [S07]'),('Google Play','Cheng et ses coauteurs (2016) combinent une voie large et une voie profonde pour mémoriser certaines associations et généraliser à de nouvelles combinaisons. [S08]'),('Travail','Repérer les données, le mécanisme, l’interface, les indicateurs et une limite de transfert.')],
 ['Cas','Données','Mécanisme','Mesure de valeur','Limite'],
 'Ne pas résumer Netflix à un algorithme unique. Ne pas présenter les résultats historiques de Google Play comme une promesse de gain pour Novalia. Une meilleure métrique hors ligne doit être confrontée à l’expérience réelle. Surveiller pertinence, diversité, exposition et satisfaction plutôt que le seul clic.'),
 ('A04','Arbitrer les erreurs de fraude',30,'Le choix est étayé par le calcul et la capacité opérationnelle, pas par l’exactitude seule.',
 [('Population','10 000 paiements fictifs, dont 100 fraudes.'),('Politique A','80 fraudes détectées, 20 manquées, 400 paiements légitimes signalés.'),('Politique B','65 fraudes détectées, 35 manquées, 100 paiements légitimes signalés.'),('Hypothèses','Une fraude manquée coûte 100 €. Une fausse alerte coûte 5 €. Les autres coûts sont supposés identiques.')],
 ['Politique','Précision','Rappel','Coût total','Charge de revue'],
 'A : 80 / 480 = 16,7 % de précision ; 80 % de rappel ; 20 × 100 + 400 × 5 = 4 000 € ; 480 alertes. B : 65 / 165 = 39,4 % ; 65 % ; 35 × 100 + 100 × 5 = 4 000 € ; 165 alertes. Avec un faux positif à 10 €, A coûte 6 000 € et B 4 500 €. Ce calcul compare des hypothèses, il ne mesure pas un gain commercial observé.'),
 ('A05','Rédiger le canevas de valeur des données',30,'La proposition relie problème, action et indicateur métier mesurable.',
 [('Mission','Choisir un usage Novalia et défendre sa valeur sans promesse de performance non démontrée.'),('Étapes','5 minutes de choix, 15 de rédaction, 10 de contre-expertise.'),('Question centrale','Que fera réellement une personne ou un système avec le résultat ?')],
 ['Problème','Utilisateur','Action','Données','Famille de traitement','Métrique modèle','KPI métier','Risques','Responsable','Intégration'],
 'Exemple churn : l’équipe de fidélisation reçoit chaque nuit une file priorisée. La précision du score n’est pas la rétention incrémentale. Le KPI métier demande une comparaison pertinente avec un groupe témoin ou une autre méthode d’évaluation de l’action. Expliciter coût du contact, remise, délai et capacité.'),
 ('A06','Auditer la qualité et la disponibilité temporelle',35,'Les anomalies sont associées à des règles testables et à un propriétaire.',
 [('Fichier','novalia_audit_qualite.csv, réservé à cet exercice ; ne pas remplacer le fichier propre du TP ML.'),('Mission','Rechercher les défauts, distinguer correction automatique et arbitrage métier.'),('Vigilance','Une excellente prédiction peut cacher une variable disponible après la décision.')],
 ['Anomalie','Règle de détection','Conséquence','Correction','Responsable'],
 'Défauts intentionnels : montant négatif, ancienneté négative, catégorie « Mensuel » avec espaces et casse, satisfaction hors domaine, identifiant dupliqué, valeur manquante, date de rafraîchissement ancienne. La date de demande de résiliation est postérieure au snapshot pour certains dossiers : l’utiliser comme caractéristique pour anticiper le départ produirait une fuite d’information.'),
 ('A07','Attribuer les responsabilités et traiter les risques',45,'Chaque arbitrage possède un responsable et une procédure utilisable.',
 [('Scénario','Novalia calcule chaque nuit un risque de départ et le transmet à l’équipe commerciale.'),('Livrable','RACI, règles de qualité, matrice de risques et procédure d’incident.'),('À instruire','Finalité, accès, conservation, bases juridiques, catégorie éventuelle de système IA : ne pas inventer une validation juridique.')],
 ['Décision','A : arbitrage','R : réalisation','C : consultation','I : information'],
 'La finalité et le seuil relèvent d’un propriétaire métier désigné, la réalisation data des équipes habilitées et l’exploitation d’une équipe SI. Le DPO et le RSSI sont consultés selon leurs compétences ; ils ne remplacent pas automatiquement le propriétaire du service. Chaque risque a un contrôle, un indicateur, un responsable et un critère de suspension.'),
 ('A08','Explorer, entraîner, choisir puis évaluer',75,'Les décisions de modèle et de seuil sont prises sans exploiter le test final.',
 [('Fichiers','01_Atelier_Novalia_participant.ipynb et novalia_clients.csv.'),('Phase A, 40 min','Explorer, identifier la cible, séparer entraînement/validation/test, ajuster une référence puis deux modèles.'),('Phase B, 35 min','Comparer sur validation, arrêter modèle et politique, ouvrir le test, expliquer erreurs et limites.'),('Variante sans code','Analyser le notebook corrigé exécuté et les CSV de résultats, en masquant d’abord les réponses.')],
 ['Étape','Choix retenu','Preuve ou calcul','Limite'],
 f"Le jeu compte {R['n']} clients synthétiques et {R['taux_depart']*100:.2f} % de départs. La séparation est 3 000 / 1 000 / 1 000. La référence retient la régression logistique selon la précision moyenne sur validation. Le seuil {R['seuil']:.6f}, décidé sur validation, signale 105 clients sur test. Matrice : 767 vrais négatifs, 58 faux positifs, 128 faux négatifs et 47 vrais positifs. Précision 44,76 %, rappel 26,86 %. Ne pas modifier la politique sur ce même test pour obtenir a posteriori 100 alertes."),
 ('A09','Construire une vue de décision Power BI',35,'La vue est correctement étiquetée et permet de décider sans masquer les limites.',
 [('Entrée','predictions_powerbi.csv, cohorte indépendante de 1 000 clients synthétiques.'),('Production','Indicateurs de population, alertes, part d’alertes et montant mensuel associé ; distribution des scores, comparaison des contrats, tableau de synthèse.'),('Traçabilité','Afficher périmètre, date, version de modèle et seuil ; distinguer exposition comptable et perte attendue.'),('Variante','Un classeur tabulaire ou la maquette du support suffit pour discuter la décision si Power BI Desktop est indisponible.')],
 ['Vue','Question métier','Champ ou calcul','Précaution d’interprétation'],
 'Importer le CSV, contrôler les types, compter 1 000 observations et 105 alertes dans le résultat de référence. Un montant associé aux comptes alertés ne mesure ni une perte future certaine ni un gain de rétention. La maquette est illustrative ; aucun fichier PBIX n’est inclus dans ce kit.'),
 ('A10','Concevoir les flux entrants et sortants',45,'L’architecture justifie chaque échange, sa fréquence et ses contrôles.',
 [('Besoin','Mieux prévoir la demande et les livraisons.'),('Entrées','Commandes, stocks, météo, transporteurs ; retenir seulement les données utiles et disponibles.'),('Sorties','Prévisions agrégées vers des fournisseurs autorisés.'),('Production','Architecture, latence attendue, propriétaires, gestion des secrets et mode dégradé.')],
 ['Flux','Donnée et finalité','Mode / fréquence','Contrôles','Responsable / repli'],
 'Exemple : ingestion quotidienne de prévisions météo contextualisées par zone ; validation du schéma, des unités et de la fraîcheur ; jointure aux ventes historiques ; prévision ; agrégation par produit et période ; API fournisseur limitée par périmètre. Prévoir les effets d’une donnée météo absente. Ne pas exposer les clients individuels sans nécessité démontrée.'),
 ('A11','Définir et tester un contrat de données',35,'Le contrat précise aussi les échecs et la réponse attendue.',
 [('Objet','Choisir une prévision météo entrante ou une prévision agrégée sortante.'),('Contenu','Schéma, unités, horodatage, versions, finalité, droits, fraîcheur, disponibilité et repli.'),('Test local','03_Simulation_contrat_donnees.ipynb, sans API externe ni secret.')],
 ['Règle','Entrée de test','Résultat attendu','Réponse de repli'],
 'Trois tests minimum : champ obligatoire absent, version inconnue, donnée trop ancienne. Un contrat de données n’est pas uniquement un schéma JSON. Un rejet doit produire un état explicite et un circuit de traitement. Ne pas inventer une valeur de remplacement sans politique validée.'),
 ('A12','Réagir à un incident sur le SI ouvert',30,'La réponse précise impact, détection, repli, responsable et reprise.',
 [('Déclencheur','Tirer une carte incident ; conserver le cadre défensif et simulé.'),('Méthode','5 minutes de lecture, 10 d’analyse, 10 de contradiction, 5 de documentation.'),('Livrable','Une procédure courte qu’un opérateur peut appliquer sans deviner.')],
 ['Impact','Signal de détection','Mesure immédiate','Responsable','Critère de reprise'],
 'Exemple jeton compromis : révoquer le jeton concerné, isoler le flux, préserver les journaux et qualifier l’exposition ; appliquer le processus d’incident, fournir le service en mode dégradé validé ; renouveler les secrets et rétablir les accès limités seulement après contrôle. Les scénarios ne justifient aucun accès à des systèmes réels.')]

QUIZ=[
('Une API est-elle une IA ?','Non. C’est une interface ; elle peut exposer un service d’IA.'),
('Entraînement et inférence correspondent-ils à la même étape ?','Non. L’entraînement ajuste le modèle ; l’inférence utilise un modèle pour une nouvelle observation.'),
('Avec 1 % de fraudes, « tout accepter » peut-il atteindre 99 % d’exactitude ?','Oui, avec un rappel nul. L’exactitude ne suffit pas à décider.'),
('Quel type de problème correspond à une estimation de montant de vente ?','Régression ou prévision temporelle selon le cadrage.'),
('Pourquoi exclure une date de résiliation future des variables disponibles à t₀ ?','Elle contient une information inconnue au moment de la décision et crée une fuite d’information.'),
('Sur quelle partie des données choisir le seuil du TP ?','Sur la validation ; le test final mesure une politique déjà fixée.'),
('Le score le plus performant hors ligne garantit-il une valeur métier ?','Non. Il faut évaluer l’action et son impact dans le processus réel.'),
('Pourquoi une API partenaire requiert-elle davantage qu’une clé secrète ?','Il faut aussi autorisation, limitation du périmètre, validation, journalisation, disponibilité et révocation.'),
('Une association entre tickets et churn démontre-t-elle que les tickets causent le churn ?','Non. Corrélation prédictive et effet causal sont différents.'),
('Que prévoir lorsque les données ou les comportements changent ?','Surveillance des entrées et performances, responsabilité, seuils d’alerte, analyse et repli ou réentraînement validé.')]

GLOSS=[('SI','Ensemble organisé de personnes, processus, logiciels, infrastructures et données.'),('Donnée','Observation brute ou structurée, à interpréter dans un contexte.'),('Big Data','Contexte où volume, vitesse ou variété imposent des traitements adaptés.'),('Data Science','Démarche empirique reliant question métier, données, analyse et mesure.'),('Machine Learning','Famille de méthodes apprenant des régularités à partir de données.'),('Deep Learning','Apprentissage automatique par réseaux de neurones à plusieurs niveaux de représentation.'),('Cible','Résultat à apprendre ou à estimer dans un problème supervisé.'),('Caractéristique','Information utilisée en entrée, disponible au moment pertinent.'),('Entraînement','Ajustement des paramètres du modèle.'),('Inférence','Calcul d’une sortie à partir d’un modèle déjà ajusté.'),('Référence naïve','Méthode simple utilisée pour vérifier qu’un modèle apporte quelque chose.'),('Validation','Données utilisées pour comparer des choix sans employer le test final.'),('Test','Évaluation indépendante de choix arrêtés.'),('Précision','Vrais positifs / ensemble des alertes positives.'),('Rappel','Vrais positifs / ensemble des cas réellement positifs.'),('Faux positif','Observation légitime signalée à tort.'),('Faux négatif','Cas recherché qui n’est pas détecté.'),('Seuil','Niveau de score à partir duquel une politique déclenche une action.'),('Fuite de données','Utilisation d’information non disponible ou interdite au moment de la décision.'),('Surapprentissage','Ajustement trop spécifique aux données connues, au détriment de la généralisation.'),('Dérive','Changement des données, des relations ou des performances en exploitation.'),('Pipeline','Chaîne reproductible de préparation et de traitement.'),('API','Contrat d’interface entre applications ou services.'),('Événement','Fait publié pour informer d’autres composants d’un changement.'),('OAuth 2.0','Cadre de délégation d’autorisation ; ne pas le confondre avec une preuve d’identité utilisateur.'),('Minimisation','Limitation des données à ce qui est nécessaire pour la finalité.'),('RACI','Matrice des responsabilités d’arbitrage, réalisation, consultation et information.'),('MLOps','Pratiques d’industrialisation, de traçabilité et d’exploitation des modèles.'),('KPI métier','Indicateur du résultat opérationnel ou économique recherché.'),('Mode dégradé','Fonctionnement de repli explicite lorsque le fonctionnement nominal est indisponible.')]

figures()
doc=cover('Dossier pédagogique\net guide formateur','Contenus détaillés, conducteur, corrigés et corpus de référence','GUIDE FORMATEUR')
heading(doc,'Repères pour comprendre, même sans expérience',1)
tag(doc,'[Objectif : vocabulaire commun] [Public : débutant à intermédiaire] [Référentiel : fondamentaux Big Data, Data Science et ML]')
intro=[
('Partir d’une décision plutôt que d’un outil',"Un projet utile commence par une décision observable : affecter une demande à une équipe, anticiper un manque de stock, proposer une inspection, choisir une prochaine action commerciale. Dire « nous voulons une IA » ne précise ni qui agit, ni ce qui doit changer, ni comment mesurer le résultat. Le cadrage doit nommer l’utilisateur, la donnée disponible, l’horizon de décision et le coût de l’erreur.","Le système d’information est le cadre dans lequel cette décision existe. Il ne se limite pas aux logiciels : il réunit aussi personnes, règles, procédures, infrastructures et données. Un score stocké dans un fichier que personne ne consulte peut être statistiquement valide et opérationnellement inutile. L’IA est un maillon qui reçoit des données et rend un résultat à un processus.",'J1-005'),
('De la donnée à l’action',"38,7 °C est une donnée. Pour interpréter cette température, il faut connaître le composant, les conditions de fonctionnement, le capteur et la plage attendue. L’information se construit lorsque la mesure est contextualisée. L’expertise et les modèles permettent ensuite de relier plusieurs observations à une hypothèse. L’action peut être une inspection, pas nécessairement un remplacement automatique.","La pyramide donnée, information, connaissance, décision est une représentation pédagogique. Elle ne signifie pas qu’un algorithme produit automatiquement une connaissance certaine. Dans l’entreprise, la qualité du contexte et la responsabilité de la décision restent déterminantes. Demander aux participants de remonter un exemple personnel depuis une observation jusqu’à un résultat vérifiable.",'J1-006'),
('IA, apprentissage automatique et apprentissage profond',"L’intelligence artificielle est un champ qui comprend plusieurs méthodes de perception, prédiction, raisonnement, planification ou génération. Le Machine Learning désigne des approches qui ajustent un modèle à partir d’exemples au lieu d’exiger l’écriture explicite de toutes les règles. Dans l’apprentissage supervisé, les exemples sont associés à une cible ; sans cible explicite, d’autres approches recherchent des structures ou des anomalies.","Le Deep Learning est une famille du Machine Learning fondée sur des réseaux de neurones à plusieurs niveaux de représentation. L’IA générative décrit une capacité à produire du contenu et ne constitue pas un synonyme de toute l’IA. Une entreprise peut créer une forte valeur avec une régression, des arbres, un moteur de règles ou une prévision classique. Choisir la complexité seulement lorsqu’elle améliore une exigence réelle. [S02, S05, S06]",'J1-008'),
('Big Data et valeur des données',"Le Big Data ne commence pas à un seuil universel de téraoctets. Volume, vélocité et variété peuvent obliger à adapter le stockage, les flux et les traitements. La grille des cinq V ajoute la véracité et la valeur pour ramener la discussion à la confiance et à la décision. Cette grille est une aide de lecture, pas une loi scientifique ou un label de performance.","Un petit jeu cohérent peut être plus utile qu’un immense historique sans définition stable ni finalité. Les données peuvent réduire un risque, un coût ou un délai, soutenir un service ou améliorer l’expérience. La valeur se vérifie dans l’action et son effet. Il faut donc distinguer volume disponible, droit d’utilisation, utilité prédictive et résultat métier. [S27]",'J1-013'),
('Entraîner n’est pas décider',"L’entraînement utilise des exemples pour ajuster des paramètres. L’inférence applique le modèle à une nouvelle observation. La règle de décision combine ensuite le score avec les contraintes métier : capacité de traitement, criticité, coût des erreurs, contrôles et niveau de supervision. Cette troisième couche appartient au système, pas au modèle seul.","Pour prédire un départ dans trente jours, les caractéristiques doivent être connues à la date du score. La résiliation observée dans le futur peut servir à construire la cible historique, mais pas à alimenter le modèle comme si elle était disponible au moment de décider. Cette distinction temporelle est l’un des contrôles essentiels de validité. [S03]",'J1-015'),
('Mesurer les erreurs utiles au métier',"Avec cent fraudes parmi dix mille paiements, une politique qui accepte tout obtient 99 % d’exactitude mais ne détecte aucune fraude. La précision mesure la proportion de cas pertinents parmi les alertes. Le rappel mesure la part des cas réels détectés. Un faux positif peut gêner un client légitime ; un faux négatif laisse passer le risque recherché.","Le coût ne se limite pas à la métrique statistique. Il comprend revue humaine, friction, perte éventuelle, délai, exploitation et capacité. Un seuil moins élevé augmente souvent le nombre d’alertes. Le bon choix dépend donc d’une politique explicite et d’une validation indépendante. Un score de risque n’est pas un effet causal et n’établit pas qu’une action de fidélisation sera efficace. [S04, S30]",'J1-019'),
('Le modèle continue à vivre après le notebook',"Un notebook permet d’explorer, d’expliquer et de tester un raisonnement. La production exige en plus des flux fiables, des droits d’accès, des versions, des journaux, un service disponible et une procédure de retour arrière. La même préparation doit être appliquée en entraînement et en inférence. La responsabilité d’un incident doit être connue avant le premier déploiement.","Les données et les comportements changent. Surveiller les distributions ne remplace pas la mesure des résultats, et le réentraînement automatique n’est pas toujours la réponse adéquate. Une dérive peut venir d’une nouvelle politique métier, d’un capteur remplacé, d’une source erronée ou d’un changement de population. Il faut qualifier la cause et décider du contrôle adapté. [S28]",'J2-033')]
for title,t1,t2,fig in intro:heading(doc,title,2);p(doc,t1);p(doc,t2);figure(doc,fig,title)

heading(doc,'Cadre contractuel et conducteur vérifiable',1)
tag(doc,'[Durée : 720 minutes hors pauses] [TP : 450 minutes, 62,5 %] [Diagnostic et évaluations : 60 minutes] [Apports : 210 minutes]')
p(doc,'Objectif général fourni : acquérir une compréhension approfondie des concepts et applications de l’intelligence artificielle dans les systèmes d’information des entreprises, avec un accent sur les impacts organisationnels et stratégiques.')
p(doc,'Public : dirigeants, managers, responsables métiers, professionnels informatiques et data, personnes intéressées par l’impact de l’IA sur les SI. Prérequis : culture informatique et données ; notions SI souhaitées. Le niveau Application est matérialisé par la capacité à cadrer et justifier un usage dans une situation professionnelle.')
table(doc,[['Bloc contractuel','Durée','Preuve d’apprentissage'],['B1 : Big Data, Data Science et ML','120 min','A01, A02 et diagnostic'],['B2 : données et modèles économiques','120 min','A03, A04, A05'],['B3 : Data Science et gouvernance','120 min','A06, A07'],['B4 : Machine Learning et Deep Learning','180 min','A08, A09'],['B5 : ouverture du SI','180 min','A10, A11, A12 et évaluation']])
note(doc,'Comptage','Les durées de séquence sont partagées entre plusieurs diapositives. Elles ne s’additionnent pas à chaque fiche. Les annexes sont des ressources complémentaires, pas des heures contractuelles supplémentaires.')
for day in (1,2):
 heading(doc,f'Conducteur du jour {day}',2)
 rows=[['Séquence','Minutes','Modalité','Contenu']]+[[x[0],str(x[3]),x[4],x[5]] for x in D['schedule'] if x[1]==day]
 table(doc,rows,[2.0,1.6,2.4,11.1])
 p(doc,'Pauses et repas sont hors temps pédagogique. Le conducteur peut être positionné sur les horaires convenus pour la session ; aucun horaire contractuel ni client n’est inventé.')
heading(doc,'Préparation, différenciation et secours',2)
for label,text in [
('Avant la session','Tester les notebooks de bout en bout ; préparer les CSV locaux et une copie des résultats ; vérifier le poste de projection, l’accès à Jupyter et la compatibilité du parc Power BI ; distribuer le cahier participant sans les corrigés.'),
('Composition des groupes','Privilégier des équipes de trois à cinq profils mixtes. Managers : valeur et arbitrage. Métiers : workflow et action. IT : flux, identité, sécurité et repli. Data : validation et métriques. Tous travaillent sur le même cas.'),
('Sans environnement Python','Distribuer les CSV et montrer le corrigé exécuté en masquant les réponses. Faire expliciter entrées, transformations et résultats. Ne pas consacrer le temps contractuel à une installation improvisée.'),
('Sans Power BI ou sans Internet','Utiliser la maquette du diaporama et une lecture tabulaire des données. Tous les éléments essentiels sont locaux. Aucun compte fournisseur ni donnée confidentielle n’est nécessaire.'),
('Après la session','Mettre à disposition les diaporamas PDF, les notebooks, les données, les corrigés et le corpus. Recueillir satisfaction et éléments de transfert sans les confondre avec une preuve d’impact économique.')]:note(doc,label,text)

names={'B1':'Fondamentaux et mise en application métier','B2':'Données et nouveaux modèles économiques','B3':'Data Science, gouvernance, sécurité et conformité','B4':'Machine Learning, Deep Learning et intégration SI','B5':'Ouverture des SI, contrats et résilience'}
for b,title in names.items():
 heading(doc,title,1);tag(doc,f'[Bloc : {b}] [Niveau : Application] [Fiches synchronisées avec les identifiants des diapositives]')
 arr=[s for s in D['slides'] if s['block']==b and s['kind'] not in ('cover','section','sources') and not s['seg'].startswith('ANN')]
 # Keep full teaching content, including annexes assigned to the block.
 for s in arr:
  heading(doc,s['id']+' | '+s['title'].replace('\n',' '),2)
  tag(doc,f"[Séquence : {s['seg']}] [Modalité : {s['mode']}] [Budget de la séquence : {s['segment_minutes']} min]")
  if s['kind'] in ('table','confusion'):table(doc,s['items'])
  elif s['kind']=='metric':note(doc,str(s.get('metric','Indicateur')),s.get('label',''))
  elif s['items']:
   for a in s['items']:
    if isinstance(a,list):
     q=doc.add_paragraph();q.add_run(clean(a[0])+'. ').bold=True;q.add_run(clean(' / '.join(map(str,a[1:]))))
    else:p(doc,a)
  p(doc,s['n'])
  figure(doc,s['id'],s['title'].replace('\n',' '))
  if s.get('q'):note(doc,'Question de relance',s['q'])
  if s.get('a'):note(doc,'Réponse attendue',s['a'])
  if s.get('pitfall'):note(doc,'Vigilance',s['pitfall'])
  note(doc,'Message à faire retenir',s['take']);refs(doc,s.get('sources',[]))

heading(doc,'Corrigés et critères des travaux pratiques',1)
for ident,title,duration,obj,context,fields,answer in ACT:
 heading(doc,f'{ident} | {title}',2);tag(doc,f'[Durée cumulée : {duration} min] [Réussite : {obj}]');p(doc,answer)
 note(doc,'Évaluation formative','Vérifier l’argumentation, le lien avec une action et l’identification des limites. Une alternative techniquement plausible et correctement justifiée peut être acceptée. Une réponse vague contenant uniquement un nom d’outil est insuffisante.')

heading(doc,'Évaluation finale, suivi et preuves',1)
p(doc,'La restitution finale porte sur un système de maintenance industrielle : données de capteurs chez les clients, anticipation de panne, alerte technicien et tableau de bord client. Le participant explicite problème, données, méthode, indicateurs, flux, supervision et risques. La proposition ci-dessous est une modalité pédagogique, pas un seuil contractuel fourni.')
table(doc,[['Critère','Points','Preuve attendue'],['Cadrage métier','15','Décision, utilisateur et horizon explicites'],['Données','15','Sources, disponibilité et qualité'],['Famille ML / DL','15','Choix plausible, référence simple'],['Métriques et erreurs','15','Mesures et coût opérationnel'],['Gouvernance et conformité','15','Responsabilités et questions à instruire'],['Architecture ouverte','15','Flux entrants et sortants contrôlés'],['Risques et suivi','5','Détection, repli et surveillance'],['Argumentation','5','Hypothèses et limites visibles']])
p(doc,'Un seuil de 70/100 peut être utilisé comme repère pédagogique si l’organisme le valide. Le QCM individuel et la fiche de transfert complètent la preuve de groupe. Le certificat de réalisation atteste une action réalisée ; il ne constitue pas, à lui seul, une certification universelle de maîtrise de l’IA.')
for i,(q,a) in enumerate(QUIZ,1):heading(doc,f'Q{i:02}. {q}',3);p(doc,a)
heading(doc,'Indicateurs de suivi de l’action',2)
table(doc,[['Indicateur prévu','Définition opérationnelle à retenir'],['Nombre d’apprenants','Inscrits, présents au démarrage et présents à la fin, distingués'],['Satisfaction','Résultat de l’enquête avec nombre de réponses et échelle'],['Taux de retour','Réponses reçues / personnes sollicitées'],['Abandons','Nombre et causes documentées / effectif de référence annoncé'],['Interruptions','Situations définies par le prestataire, effectifs et motifs'],['Présence','Émargements par demi-journée et temps réalisés']])
note(doc,'Ne pas inventer les résultats','Les modèles de suivi sont vierges tant qu’une session réelle n’a pas eu lieu. Aucun client, apprenant, taux de satisfaction ou date d’émargement n’est présumé.')

heading(doc,'Glossaire progressif',1)
for term,definition in GLOSS:
 q=note(doc,term,definition);q.paragraph_format.space_before=Pt(2);q.paragraph_format.space_after=Pt(4)
 for r in q.runs:r.font.size=Pt(9.5)
heading(doc,'Corpus de sources et limites d’interprétation',1)
p(doc,'Les références renvoient aux sources identifiées dans la base éditoriale. Les chiffres fournisseur sont présentés comme des déclarations de leur auteur ; les simulations Novalia sont séparées. Les pages réglementaires et de documentation peuvent évoluer. Vérifier le champ et le calendrier applicables avant une future session ou une mise en production. Les titres anglais des publications sont conservés pour permettre leur identification exacte.')
for key,data in S.items():
 heading(doc,f'[{key}] {data[0]}',3);p(doc,data[1]);p(doc,'Date ou repère : '+data[2]+'. '+data[3])
refs(doc,['S01'])
doc.save(OUT/'Dossier_pedagogique_4_020.docx')
print('guide saved',flush=True)

work=cover('Cahier participant','Ateliers, fiches de travail, évaluation et repères','CAHIER PARTICIPANT')
heading(work,'Mode d’emploi et parcours',1)
p(work,'Ce cahier accompagne les deux journées. Les espaces sont destinés à votre production, pas à recopier des définitions. Pour chaque atelier, notez une hypothèse, une preuve et une limite. Les corrigés sont remis séparément dans le guide formateur après l’activité.')
p(work,'Nom : ..............................................................    Date de session : ........................................')
table(work,[['Jour 1','Jour 2'],['A01 à A07 : comprendre, cadrer, valoriser et gouverner','A08 à A12 : expérimenter, restituer et intégrer'],['6 heures hors pauses','6 heures hors pauses']])
heading(work,'Diagnostic initial individuel',2)
for q,a in QUIZ[:3]+QUIZ[6:8]:p(work,q,bold=True);p(work,'Réponse et degré de certitude : ........................................................................................................');p(work,'.....................................................................................................................................................')
for ident,title,duration,obj,context,fields,answer in ACT:
 heading(work,f'{ident} | {title}',1);tag(work,f'[Durée : {duration} min] [Livrable : production argumentée]');note(work,'Critère de réussite',obj)
 for label,text in context:note(work,label,text)
 if ident=='A01':
  rows=[['Cas','Famille et sortie','Donnée / décision']]+[[k,'',''] for k,_ in context];table(work,rows,blanks=True)
 elif ident in ('A05','A07','A10','A12'):
  rows=[['Élément à préciser','Votre réponse']]+[[f,''] for f in fields];table(work,rows,blanks=True)
 elif ident=='A04':
  table(work,[fields]+[[pol,'','','',''] for pol in ('Politique A','Politique B')],blanks=True)
  note(work,'Deuxième tour','Recalculer avec une fausse alerte à 10 €. La préférence change-t-elle ? Quelle charge votre équipe peut-elle traiter ?')
 else:
  rows=[fields]+[['']*len(fields) for _ in range(5 if ident not in ('A06','A08') else 7)];table(work,rows,blanks=True)
 p(work,'Hypothèse décisive : ....................................................................................................................')
 p(work,'Preuve ou test d’acceptation : ........................................................................................................')
 p(work,'Limite à ne pas masquer : .............................................................................................................')
 if ident in ('A02','A10'):
  work.add_page_break();heading(work,'Zone de schéma',2)
  p(work,'Données entrantes → préparation → modèle ou traitement → application → action → mesure',bold=True)
  table(work,[['Dessinez les composants, puis annotez les flèches.']]+[['\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n']],blanks=False)
 if ident=='A08':
  work.add_page_break();heading(work,'Arrêter le choix avant le test',2)
  table(work,[['Décision à figer','Votre réponse'],['Modèle retenu',''],['Critère sur validation',''],['Seuil ou quota',''],['Capacité maximale',''],['Coût des erreurs',''],['Motif du choix','']],blanks=True)
  note(work,'Une fois le test ouvert','Rapporter le résultat, les erreurs et les limites. Modifier le seuil pour réussir le test transforme ce test en nouvelle validation ; une évaluation indépendante devient nécessaire.')
heading(work,'Cartes incident',1)
for title,question in [('API météo indisponible','Quelle donnée de repli est encore acceptable, et pendant combien de temps ?'),('Schéma JSON modifié','Comment détecter et isoler un changement incompatible ?'),('Volume multiplié par dix','Quel service dégrader et quelle file prioriser ?'),('Donnée personnelle inattendue','Comment isoler le flux et qualifier la situation ?'),('Rappel en baisse','Comment distinguer changement de population et défaut de données ?'),('Demande de données brutes','Quelle finalité et quel droit justifieraient ce partage ?'),('Jeton partenaire compromis','Comment révoquer, enquêter et reprendre avec un périmètre limité ?')]:note(work,title,question)
heading(work,'Évaluation individuelle',1)
p(work,'Répondre en une ou deux phrases et donner un exemple lorsque cela éclaire le raisonnement. Le formateur indique le barème retenu pour la session.')
for i,(q,a) in enumerate(QUIZ,1):
 if i==6:work.add_page_break();heading(work,'Évaluation individuelle, suite',2)
 heading(work,f'Q{i:02}. {q}',3)
 for _ in range(3):p(work,'.....................................................................................................................................................')
heading(work,'Transfert vers votre métier',1)
table(work,[['Question','Votre cas'],['Quelle décision améliorer ?',''],['Qui utilisera le résultat ?',''],['Quelles données sont disponibles à t₀ ?',''],['Quelle référence simple ?',''],['Quel indicateur métier ?',''],['Quelle erreur coûte le plus ?',''],['Dans quelle application intégrer ?',''],['Qui porte la responsabilité ?',''],['Quel point juridique ou sécurité instruire ?',''],['Quel premier test observable ?','']],blanks=True)
heading(work,'Fiche réflexe et vocabulaire',1)
for term,definition in GLOSS:
 q=note(work,term,definition);q.paragraph_format.space_before=Pt(2);q.paragraph_format.space_after=Pt(4)
 for r in q.runs:r.font.size=Pt(9.5)
work.save(OUT/'Cahier_participant_4_020.docx')
print('workbook saved',flush=True)
# Companion readable markdown, searchable in the repository.
lines=['# Dossier pédagogique 4-020','', 'IA appliquée aux systèmes d’information de l’entreprise. 12 h / 2 jours.','']
for para in doc.paragraphs:
 t=para.text
 if not t:continue
 if para.style.name.startswith('Heading'):
  lvl=int(para.style.name[-1]);lines+=['#'*(lvl+1)+' '+t,'']
 else:lines+=[t,'']
(ROOT/'documents/Dossier_pedagogique_4_020.md').write_text('\n'.join(lines),encoding='utf-8')
print('figures',len(FIG))
