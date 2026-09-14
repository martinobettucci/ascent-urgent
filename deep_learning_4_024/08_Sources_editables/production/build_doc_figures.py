from pathlib import Path
import math, numpy as np, base64
from build_visuals import Canvas,ROOT,OUT,BLUE,GREEN,RED,NAVY,PALE,INK,MUTED,LINE,WHITE,YELLOW
SPECIAL={}
def finish(n,title,c):
 c.foot('Illustration pédagogique • schéma explicatif, pas une mesure métier');name=f'DOC_{n:03d}';c.save(name);SPECIAL[n]={'name':name,'title':title}
def head(title):
 c=Canvas();c.text(35,43,title.upper(),24,BLUE,True);return c
# 7 : nuages de points et complexité.
c=head('Sous-apprentissage, compromis et surapprentissage');rng=np.random.default_rng(17);x=np.linspace(0,1,16);obs=.35+.32*np.sin(x*5)+rng.normal(0,.08,len(x));xx=np.linspace(0,1,240)
for j,(lab,col) in enumerate([('Sous-apprentissage',RED),('Compromis',GREEN),('Surapprentissage',RED)]):
 ox=35+j*398;c.rect(ox,103,365,390,PALE);c.text(ox+183,143,lab,22,col,True,'middle')
 for a,b in zip(x,obs):c.circle(ox+38+a*291,439-b*285,5,BLUE)
 yy=np.repeat(obs.mean(),len(xx)) if j==0 else .35+.32*np.sin(xx*5) if j==1 else np.polyval(np.polyfit(x,obs,12),xx)
 c.path([(ox+38+a*291,439-min(.98,max(.05,b))*285) for a,b in zip(xx,yy)],col,4)
finish(7,'Trois régimes d’ajustement',c)
# 17 : architectures.
c=head('Trois mécanismes de représentation');
for j,(lab,sub) in enumerate([('CNN','Voisinage spatial'),('LSTM','État transmis dans le temps'),('Transformer','Interactions par attention')]):
 x=40+j*393;c.box(x,103,360,75,lab,BLUE,WHITE,size=29)
 for k in range(6):c.circle(x+38+k*57,292,11,GREEN)
 if j==0:
  for k in range(3):c.line(x+38+k*57,315,x+95,382,LINE,3)
 elif j==1:
  for k in range(5):c.line(x+53+k*57,292,x+81+k*57,292,BLUE,2,True)
 else:
  for a in range(6):
   for b in range(a+1,6):c.line(x+38+a*57,280,x+38+b*57,280,LINE,1)
 c.text(x+180,462,sub,21,MUTED,True,'middle',width=26)
finish(17,'CNN, LSTM et attention',c)
# 27 : extrait réel du jeu synthétique livré.
import pandas as pd
df=pd.read_csv(ROOT/'03_Travaux_pratiques/donnees/dossiers_synthetiques.csv').head(8)
c=head('Dossiers fictifs : variables et cible');cols=['v00','v01','v02','v03','v04','examen_utile'];xs=[35,221,407,593,779,965]
for x,t in zip(xs,cols):c.box(x,88,175,47,t,BLUE,WHITE,size=18)
for i,(_,row) in enumerate(df.iterrows()):
 for x,col in zip(xs,cols):c.box(x,148+i*43,175,37,str(int(row[col])) if col=='examen_utile' else f'{row[col]:.2f}',PALE,size=18)
c.text(600,533,'Extrait du jeu synthétique livré ; aucune donnée fiscale réelle.',22,MUTED,True,'middle');finish(27,'Un extrait des données synthétiques',c)
c=head('Faire le point sur son apprentissage');c.flow(['Je sais expliquer','Je sais faire','Je dois revoir'],y=170,colors=[BLUE,GREEN,PALE]);c.text(600,445,'Tenseur • perte • split • réseau • matrice • seuil',27,MUTED,False,'middle');finish(28,'Carte de fin de journée',c)
# 30 : cinq expériences, courbes schématiques identifiables.
c=head('Laboratoire CNN : une hypothèse par expérience')
for j,lab in enumerate(['A : MLP','B : CNN','C : capacité','D : régulariser','E : erreurs']):
 ox=20+j*238;c.rect(ox,110,220,357,PALE);c.text(ox+110,155,lab,18,BLUE,True,'middle');xx=np.linspace(0,1,30)
 for k,col in enumerate([BLUE,RED]):
  yy=.70*np.exp(-xx*(2+j/2))+.10+(np.maximum(xx-.45,0)*.65 if j==2 and k==1 else .08*k)
  c.path([(ox+27+a*169,423-b*231) for a,b in zip(xx,yy)],col,3)
c.text(600,528,'Bleu : entraînement • Rouge : validation • courbes illustratives',23,MUTED,False,'middle');finish(30,'Cinq expériences contrôlées sur un CNN',c)
c=head('Ne pas confondre besoin, famille et architecture');
for j,(lab,col) in enumerate([('Besoin : prioriser une revue de dossiers',BLUE),('Familles possibles : règles, statistiques, apprentissage',GREEN),('Architecture particulière : à choisir et comparer',PALE)]):c.box(90,98+j*144,1020,112,lab,col,WHITE if col!=PALE else INK,size=28)
finish(40,'Trois niveaux de formulation',c)
c=head('Cas clinique : rendre visibles les incertitudes')
for j,(lab,noise) in enumerate([('Signal exploitable',0),('Signal altéré (simulation)',12)]):
 ox=45+j*600;c.rect(ox,115,545,305,PALE);c.text(ox+272,154,lab,23,BLUE,True,'middle');rng=np.random.default_rng(51)
 for k,col in enumerate([BLUE,GREEN,RED]):c.path([(ox+25+i*3.15,248+k*40+13*math.sin(i*.09)+float(rng.normal(0,noise))) for i in range(155)],col,4)
c.text(600,488,'Comment signaler l’incertitude et organiser une revue ?',26,MUTED,True,'middle');finish(44,'Qualité du signal et incertitude',c)
c=head('Quelles données sont autorisées en TP ?')
for i,(t,col) in enumerate([('Données synthétiques ou corpus public validé',GREEN),('Données internes : validation institutionnelle préalable',YELLOW),('Pas de données fiscales personnelles sur un service externe',RED)]):c.box(55,107+i*145,1090,115,t,col,WHITE if col in [GREEN,RED] else INK,size=27)
finish(51,'Règles de données du stage',c)
c=head('Rendre une contribution algorithmique intelligible');c.box(60,105,305,360,'Décision administrative',BLUE,WHITE,size=30)
for i,t in enumerate(['Degré de contribution','Données et sources','Paramètres pertinents','Opérations effectuées']):c.box(470,85+i*110,675,92,t,PALE,size=25)
c.line(378,285,450,285,arrow=True);finish(53,'Points de transparence à examiner',c)
c=head('Les biais peuvent apparaître dans toute la chaîne');c.flow(['Collecte','Annotation','Modèle','Métrique','Seuil','Usage'],y=180)
for i in range(6):c.circle(132+i*187,397,15,RED)
c.text(600,492,'Pour chaque risque : un test, un responsable et une action.',27,MUTED,True,'middle');finish(55,'Des risques à chaque étape',c)
c=head('Compétences visées : niveau Application')
for i,(t,w,col) in enumerate([('Recherche avancée : hors périmètre',430,LINE),('Justifier',580,NAVY),('Diagnostiquer',730,GREEN),('Exécuter',880,BLUE),('Expliquer',1030,BLUE)]):c.box((1200-w)/2,83+i*88,w,74,t,col,INK if col==LINE else WHITE,size=24)
finish(57,'Progression des compétences du stage',c)
c=head('Hiérarchie typographique des supports')
for y,t,sz in [(142,'Un titre, une idée principale',37),(238,'Un sous-titre pour orienter la lecture',29),(322,'Un texte court et lisible en projection',24),(399,'model.fit(X_train, y_train)',23),(473,'Une annotation discrète, sans perdre la lisibilité',18)]:c.text(70,y,t,sz,BLUE if y<300 else MUTED,y<300)
finish(59,'Hiérarchie des titres, textes et annotations',c)
c=head('Un langage graphique constant')
for i,(t,col) in enumerate([('Opération',BLUE),('Données',GREEN),('Modèle',NAVY),('Décision',YELLOW),('Revue humaine',BLUE),('Risque / alerte',RED)]):c.box(40+(i%3)*396,113+(i//3)*215,365,165,t,col,INK if col==YELLOW else WHITE,size=29)
finish(60,'Légende des catégories visuelles',c)
c=head('Une diapositive explique au lieu d’accumuler');c.rect(48,102,497,360,PALE)
for i in range(13):c.line(75,145+i*21,507,145+i*21,LINE,5)
c.text(295,510,'Accumulation de texte',25,RED,True,'middle');c.rect(653,102,497,360,PALE);c.grid(705,150,np.arange(9).reshape(3,3),63);c.line(926,244,975,244,arrow=True);c.box(994,183,131,117,'Une idée',GREEN,WHITE,size=23);c.text(900,510,'Un mécanisme à discuter',25,GREEN,True,'middle');finish(61,'Transformer une liste en explication',c)
c=head('Anticiper les incidents avant la session')
for i,t in enumerate(['Réseau : données locales','GPU : modèle CPU','Dépendances : noyau préparé','Données : copie de secours','Temps : checkpoint fourni','Niveau : cellules guidées']):c.box(40+(i%2)*597,100+(i//2)*148,560,120,t,PALE,size=25)
finish(62,'Incidents et solutions de repli',c)
c=head('Du problème à un système défendable');labs=['Formuler','Cible / instant','Données','Séparer','Baseline','Architecture','Entraîner','Erreurs','Décision métier','Documenter / suivre']
for i,t in enumerate(labs):c.box(25+(i%5)*238,125+(i//5)*194,220,145,str(i+1)+'. '+t,BLUE if i<5 else GREEN,WHITE,size=22)
finish(63,'Les dix étapes de la démarche',c)
# Galerie d’erreurs réellement calculées pendant la recette CPU.
file=ROOT/'03_Travaux_pratiques/resultats/04_erreurs.png'
if file.exists():
 for sid in [55,118]:
  c=head('Exemples d’erreurs issus de la recette CPU')
  b64=base64.b64encode(file.read_bytes()).decode();c.e.append(f'<image x="50" y="72" width="1100" height="445" href="data:image/png;base64,{b64}" preserveAspectRatio="xMidYMid meet"/>');c.foot('Sorties du TP CNN • exemples réels du jeu public de chiffres manuscrits');c.save(f'{sid:03d}_errors')
# Liste de correspondance rédigée explicitement, sans appariement automatique.
MAP=[1,5,10,13,18,31,'DOC_007',70,39,40,20,21,46,48,56,57,'DOC_017',98,23,25,27,41,28,4,16,17,'DOC_027','DOC_028',46,'DOC_030',55,59,60,66,74,81,86,88,89,'DOC_040',91,92,95,'DOC_044',97,99,120,100,101,104,'DOC_051',103,'DOC_053',102,'DOC_055',93,'DOC_057',124,'DOC_059','DOC_060','DOC_061','DOC_062','DOC_063']
import json
(ROOT/'08_Sources_editables'/'Choix_figures_dossier.json').write_text(json.dumps({'map':MAP,'special':SPECIAL},ensure_ascii=False,indent=2));print('Correspondances vérifiées :',len(MAP))
# Figures finales : erreurs de validation effectivement observées et trois diagnostics.
import sys, ast, torch
from torch import nn
sys.path.insert(0,str(ROOT/'03_Travaux_pratiques/modules'))
from atelier import digits_data,predict
nb=json.loads((ROOT/'03_Travaux_pratiques/corriges/04_CNN___classer_des_images_et_examiner_les_erreurs.ipynb').read_text());env={'nn':nn,'torch':torch}
for cell in nb['cells']:
 if cell['cell_type']=='code':
  tree=ast.parse(''.join(cell['source']))
  for node in tree.body:
   if isinstance(node,ast.ClassDef) and node.name=='MonCNN':exec(compile(ast.Module(body=[node],type_ignores=[]),'<modele_recette>','exec'),env)
m=env['MonCNN']();m.load_state_dict(torch.load(ROOT/'03_Travaux_pratiques/resultats/04_cnn.pt',weights_only=True));data=digits_data();X,y=data['validation'];scores=predict(m,X,'multi');pred=scores.argmax(1);errors=np.where(pred!=y)[0][:12]
for sid in [55,118]:
 c=head('Erreurs observées sur la validation du TP CNN')
 for j,ix in enumerate(errors):
  ox=28+(j%4)*297;oy=86+(j//4)*151;c.rect(ox,oy,275,137,PALE);c.grid(ox+13,oy+11,X[ix,0],size=13,labels=False);c.text(ox+129,oy+41,'Vrai : '+str(y[ix]),19,BLUE,True);c.text(ox+129,oy+72,'Prédit : '+str(pred[ix]),19,RED,True);c.text(ox+129,oy+107,f'Score : {scores[ix,pred[ix]]:.2f}',17,MUTED)
 c.foot('Recette CPU : erreurs sur validation • test non consulté');c.save(f'{sid:03d}_errors')
c=head('Trois profils de courbes d’apprentissage');xx=np.linspace(0,1,40)
for j,(lab,tr,va) in enumerate([('Sous-apprentissage',.8-.18*xx,.86-.12*xx),('Compromis',.80*np.exp(-5*xx)+.05,.75*np.exp(-4*xx)+.14),('Surapprentissage',.80*np.exp(-5*xx)+.04,.75*np.exp(-4*xx)+.15+.75*np.maximum(xx-.45,0))]):
 ox=28+j*395;c.rect(ox,98,366,395,PALE);c.text(ox+183,143,lab,22,BLUE,True,'middle');c.line(ox+37,444,ox+338,444,INK,2);c.line(ox+37,444,ox+37,184,INK,2)
 for yy,col in [(tr,BLUE),(va,RED)]:c.path([(ox+38+a*298,442-b*253) for a,b in zip(xx,yy)],col,4)
c.text(600,534,'Bleu : entraînement • Rouge : validation • courbes schématiques',23,MUTED,False,'middle');c.foot('Diagnostic à confirmer par le protocole et des tests discriminants');c.save('065_curves')
