from pathlib import Path
import json, math, html, textwrap, re, random
import numpy as np
import cairosvg
from PIL import Image, ImageFont
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'05_Illustrations';OUT.mkdir(exist_ok=True)
SLIDES=json.loads((ROOT/'08_Sources_editables/slides.json').read_text())
BLUE='#23468C'; GREEN='#238C33'; YELLOW='#D9CF4A'; RED='#F24141'; INK='#0D0D0D'; NAVY='#122441'; MUTED='#56677F'; PALE='#EFF4FA'; WHITE='#FFFFFF'; LINE='#CDD8E6'
class Canvas:
 def __init__(self):
  self.e=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker></defs><rect width="1200" height="600" fill="{WHITE}"/>']
 def rect(self,x,y,w,h,fill=PALE,stroke='none',r=14,sw=2):self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def line(self,x1,y1,x2,y2,color=MUTED,sw=3,arrow=False,dash=None):self.e.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'+(' marker-end="url(#arrow)"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def circle(self,x,y,r,fill=BLUE,stroke='none',sw=2):self.e.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def text(self,x,y,t,size=25,color=INK,bold=False,anchor='start',width=None):
  lines=str(t).split('\n') if not width else sum([textwrap.wrap(v,width=width,break_long_words=False) or [''] for v in str(t).split('\n')],[])
  for i,l in enumerate(lines):self.e.append(f'<text x="{x}" y="{y+i*size*1.32}" fill="{color}" font-family="DejaVu Sans" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{html.escape(l)}</text>')
 def box(self,x,y,w,h,label,fill=PALE,color=INK,sub=None,size=24):
  self.rect(x,y,w,h,fill)
  def wrap_pixels(txt,fs):
   font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',round(fs*4))
   result=[]
   for para in str(txt).split('\n'):
    line=''
    for word in para.split():
     candidate=(line+' '+word).strip()
     if line and font.getlength(candidate)/4>w-30:result.append(line);line=word
     else:line=candidate
    result.append(line)
   return result
  lines=wrap_pixels(label,size)
  while len(lines)*size*1.32 > h-(56 if sub else 25) and size>14:
   size-=1;lines=wrap_pixels(label,size)
  centre=y+(h-28)/2 if sub else y+h/2
  yy=centre-(len(lines)-1)*size*.66+size*.34
  for i,t in enumerate(lines):self.text(x+w/2,yy+i*size*1.32,t,size,color,True,'middle')
  if sub:
   font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',68)
   ss=min(17,17*(w-25)/max(1,font.getlength(sub)/4));self.text(x+w/2,y+h-18,sub,ss,color,False,'middle')
 def path(self,points,color=BLUE,sw=4,fill='none'):
  self.e.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
 def foot(self,t='Schéma pédagogique • aucune performance réelle représentée'):
  self.line(30,557,1170,557,LINE,1);self.text(32,584,t,16,MUTED);self.text(1166,584,'https://p2enjoy.studio',16,BLUE,False,'end')
 def flow(self,labels,y=245,colors=None):
  n=len(labels);gap=26;w=(1100-gap*(n-1))/n;x=50
  for i,label in enumerate(labels):
   self.box(x,y,w,120,label,(colors or [PALE]*n)[i],WHITE if colors and colors[i] in [BLUE,GREEN,NAVY,RED] else INK,size=23)
   if i<n-1:self.line(x+w+4,y+60,x+w+gap-4,y+60,arrow=True)
   x+=w+gap
 def nodes(self,x,y,w,h,drop=False):
  layers=[3,5,4,2];pts=[]
  for l,n in enumerate(layers):pts.append([(x+l*w/3,y+(i+1)*h/(n+1)) for i in range(n)])
  for l in range(3):
   for a in pts[l]:
    for b in pts[l+1]:self.line(*a,*b,LINE,1.4)
  for l,ps in enumerate(pts):
   for i,(xx,yy) in enumerate(ps):
    self.circle(xx,yy,16,'#D6DCE5' if drop and (i+l)%3==0 else [BLUE,GREEN,BLUE,RED][l])
 def axis(self,x=90,y=80,w=1000,h=370,xlabel='Époque',ylabel='Perte'):
  self.line(x,y+h,x+w,y+h,INK,2,True);self.line(x,y+h,x,y,INK,2,True)
  self.text(x+w/2,y+h+45,xlabel,21,MUTED,False,'middle');self.text(x-25,y-15,ylabel,20,MUTED)
  return x,y,w,h
 def grid(self,x,y,data,size=45,high=None,labels=True):
  a=np.asarray(data);lo,hi=float(a.min()),float(a.max());hi=max(hi,lo+1)
  for i,row in enumerate(a):
   for j,v in enumerate(row):
    c=BLUE if high and (i,j) in high else (PALE if labels else f'#{int(245-((v-lo)/(hi-lo))*200):02x}'*0)
    if not labels:
     k=int(250-((v-lo)/(hi-lo))*200);c=f'#{k:02x}{k:02x}{k:02x}'
    self.rect(x+j*size,y+i*size,size-2,size-2,c,r=2)
    if labels:self.text(x+j*size+size/2,y+i*size+size*.68,str(int(v)),size*.45,WHITE if high and (i,j) in high else INK,False,'middle')
 def save(self,name):
  svg=''.join(self.e)+'</svg>';(OUT/f'{name}.svg').write_text(svg)
  cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/f'{name}.png'),output_width=1500,output_height=750)

FLOW={
'pipeline':['Besoin','Données','Modèle','Évaluation','Décision'],
'journey':['J1\nComprendre','J2\nDiagnostiquer','J3\nAppliquer'],
'learningtypes':['Supervisé\nCible fournie','Non supervisé\nStructure','Auto-supervisé\nCible construite'],
'learningtypes':['Exemples + cibles','Structure sans cible','Cible dérivée des données'],
'backprop':['Entrées','Prédiction','Perte','Gradients','Mise à jour'],
'batch':['Jeu train','Lots successifs','Une époque','Époque suivante'],
'drivers':['Données','Calcul','Architectures','Optimisation','Logiciels ouverts'],
'environment':['Fichiers locaux','Jupyter ou Colab','Noyau Python','CPU / GPU'],
'checkpoint':['Architecture','Paramètres','Prétraitement','Seuil + versions'],
'leakage':['Donnée future','Variable interdite','Score flatteur','Échec en usage'],
'scaler':['Séparer','fit sur train','transform partout','Objet conservé'],
'compare':['Indices identiques','Baseline','Réseau','Métrique commune'],
'cnn':['1 × 8 × 8','8 × 4 × 4','16 × 2 × 2','64 valeurs','10 logits'],
'architectures':['MLP\nVariables','CNN\nEspace','LSTM\nOrdre temporel'],
'regularization':['Capacité','L2 / poids','Dropout','Données','Arrêt anticipé'],
'earlystop':['Entraîner','Mesurer validation','Sauver le meilleur','Arrêter si patience'],
'foncierflow':['Images IGN','Contours candidats','Rapprochement','Revue de l’agent'],
'stream':['Transactions','Score','Budget de revue','Label tardif','Mise à jour'],
'purpose':['Population','Tâche précise','Données nécessaires','Action autorisée'],
'deployment':['Finalité','Tests','Supervision','Surveillance','Arrêt / retour'],
'resources':['Notebooks','Données locales','Corrigés','Sources','Fiches pratiques'],
'projecttracks':['Vision','Priorisation','Séquence','Documents'],
'roles':['Données','Modèle','Évaluation','Restitution'],
'cards':['Fiche données','Fiche modèle','Fiche système'],
'metrics':['Cible','Métrique principale','Effectifs','Seuil / top-k','Coût d’erreur'],
'governance':['Finalité','Accès','Données','Entraînement','Usage'],
'compliance':['Quel usage ?','Quelles données ?','Quel rôle ?','Quels risques ?','Quelles obligations ?'],
'decisiontree':['Nature des données','Référence simple','Modèle candidat','Comparaison','Choix justifié'],
'freeze':['Extracteur gelé','Tête nouvelle','Dernier bloc ajusté','Évaluation'],
'forecast':['Horizon explicite','Persistance','LSTM','MAE / RMSE','Analyse des ruptures'],
'optimizer':['Gradient','SGD / Adam','Taux choisi','Mise à jour','Validation'],
'baseline':['Constant / naïf','Linéaire','Arbres','Réseau','Même protocole'],
'section':['Observer','Formuler','Tester','Mesurer','Interpréter'],
'defense':['Problème','Protocole','Résultat','Limites','Recommandation'],
}

def chart_curves(c,kind):
 if kind=='lr':
  x,y,w,h=c.axis(y=100,h=345,xlabel='Pas d’optimisation',ylabel='Perte (échelle logarithmique)')
  n=21;xx=np.linspace(0,1,n);steps=np.arange(n)
  raw=[49*(1-2*rate)**(2*steps) for rate in [.01,.1,1.1]]
  lo,hi=np.log10(.001),np.log10(1e5)
  vals=[(np.log10(arr)-lo)/(hi-lo) for arr in raw]
  labels=['0,01 : lent','0,1 : convergence','1,1 : divergence']
 elif kind=='calibration':
  x,y,w,h=c.axis(y=100,h=345,xlabel='Score annoncé',ylabel='Fréquence observée')
  n=40;xx=np.linspace(0,1,n);vals=[xx,xx**2];labels=['Calibration idéale','Exemple non calibré']
 else:
  x,y,w,h=c.axis(y=100,h=345);n=40;xx=np.linspace(0,1,n)
  vals=[.83*np.exp(-xx*5)+.04,.75*np.exp(-xx*4)+.15+.6*np.maximum(xx-.48,0)];labels=['Entraînement','Validation']
 for val,col,lab,j in zip(vals,[BLUE,RED,GREEN],labels,range(3)):
  c.path([(x+xx[i]*w,y+h-val[i]*h) for i in range(n)],col,4)
  c.line(120+j*350,510,153+j*350,510,col,5);c.text(164+j*350,517,lab,18,MUTED)

def make(s):
 c=Canvas();v=s['visual'];title=s['title'];c.text(36,42,{'hero':'APPRENTISSAGE PROFOND','case_foncier':'CAS DOCUMENTÉ : FONCIER INNOVANT','case_cfvr':'CAS DOCUMENTÉ : CFVR','case_health':'CAS DOCUMENTÉ : OCT RÉTINIENNES'}.get(v,'MÉCANISME • '+title.upper()),21,BLUE,True)
 if v=='hero':
  c.nodes(355,65,470,425)
  for i,t in enumerate(['Tableaux','Images','Séquences','Documents']):c.box(36,100+i*95,220,70,t,size=22);c.line(263,135+i*95,326,280,LINE,2,True)
  for i,t in enumerate(['Score','Classe','Prévision','Aide à la décision']):c.box(926,100+i*95,240,70,t,PALE,size=21);c.line(865,280,920,135+i*95,LINE,2,True)
  c.text(600,528,'Données → entraînement → validation → diagnostic → usage',20,MUTED,False,'middle')
 elif v=='taxonomy':
  c.rect(70,85,830,430,'#ECF1F9',r=26);c.text(110,134,'INTELLIGENCE ARTIFICIELLE',28,BLUE,True)
  c.rect(125,163,710,302,'#DCE7F6',r=25);c.text(155,207,'APPRENTISSAGE AUTOMATIQUE',25,BLUE,True)
  c.rect(190,239,560,186,BLUE,r=20);c.text(230,296,'APPRENTISSAGE PROFOND',25,WHITE,True);c.text(230,344,'Réseaux de transformations',23,WHITE);c.text(230,377,'neuronales successives',23,WHITE)
  c.box(910,211,255,180,'IA générative',GREEN,WHITE,sub='Une finalité, pas un synonyme',size=24);c.line(761,327,900,300,GREEN,3,True)
 elif v=='neuron':
  for i,t in enumerate(['x₁ × w₁','x₂ × w₂','Biais b']):c.box(55,100+i*140,230,100,t,size=32);c.line(298,150+i*140,440,290,LINE,3,True)
  c.circle(515,290,65,BLUE);c.text(515,305,'Σ',52,WHITE,True,'middle');c.line(588,290,650,290,arrow=True);c.box(665,230,220,120,'Activation',GREEN,WHITE);c.line(895,290,960,290,arrow=True);c.box(971,230,184,120,'Sortie',NAVY,WHITE)
  c.text(715,452,'Appris : poids et biais',25,BLUE,True,'middle')
 elif v=='xor':
  c.line(150,450,620,450,INK,2,True);c.line(150,450,150,95,INK,2,True)
  for a,b in [(0,0),(1,1)]:c.circle(230+a*280,375-b*210,35,BLUE);c.text(230+a*280,388,'0',28,WHITE,True,'middle')
  for a,b in [(0,1),(1,0)]:c.circle(230+a*280,375-b*210,35,RED);c.text(230+a*280,388,'1',28,WHITE,True,'middle')
  c.box(720,130,420,140,'Une droite ne sépare pas les deux classes',PALE,size=26);c.box(720,330,420,140,'Couche cachée + non-linéarité',BLUE,WHITE,size=26)
  c.text(570,490,'x₁',25);c.text(102,122,'x₂',25)
 elif v=='activations':
  for k,lab in enumerate(['ReLU','Sigmoïde','Softmax (3 classes)']):
   ox=55+k*390;c.rect(ox,105,360,395,PALE);c.text(ox+180,155,lab,23,BLUE,True,'middle')
   if k<2:
    c.line(ox+40,403,ox+328,403,INK,2);c.line(ox+175,430,ox+175,200,INK,2)
    xx=np.linspace(-4,4,80);yy=np.maximum(xx,0)/4 if k==0 else 1/(1+np.exp(-xx));c.path([(ox+42+(t+4)/8*280,402-u*184) for t,u in zip(xx,yy)],BLUE,5)
   else:
    for j,(h,txt) in enumerate([(140,'0,70'),(40,'0,20'),(20,'0,10')]):c.rect(ox+55+j*93,416-h,55,h,[BLUE,GREEN,RED][j],r=4);c.text(ox+82+j*93,453,txt,20,INK,False,'middle')
    c.text(ox+180,238,'Somme = 1',24,MUTED,True,'middle')
 elif v in ['tensors','shape']:
  if v=='tensors':
   for i,(n,t) in enumerate([('0','Scalaire'),('1','Vecteur'),('2','Matrice'),('3','Image'),('4','Lot')]):
    x=40+i*236;y=340-i*45;c.rect(x,y,211,145,PALE);c.text(x+105,y+63,n,50,BLUE,True,'middle');c.text(x+105,y+110,t,23,INK,True,'middle')
   c.text(620,80,'Nombre d’axes ≠ nombre de valeurs',28,MUTED,False,'middle')
  else:
   c.grid(90,140,np.arange(6).reshape(2,3),70);c.text(185,350,'2 × 3',31,BLUE,True,'middle');c.text(375,245,'×',55,MUTED)
   c.grid(470,100,np.arange(12).reshape(3,4),66);c.text(598,350,'3 × 4',31,GREEN,True,'middle');c.line(774,235,844,235,arrow=True);c.box(873,155,270,160,'2 × 4',BLUE,WHITE,size=46)
   c.text(600,470,'Les dimensions intérieures doivent coïncider.',26,MUTED,False,'middle')
 elif v=='traininfer':
  c.text(60,105,'ENTRAÎNEMENT',25,BLUE,True);c.flow(['Entrées + cibles','Réseau','Perte + gradient','Poids modifiés'],y=140)
  c.text(60,333,'INFÉRENCE',25,GREEN,True);c.flow(['Nouvelle entrée','Prétraitement','Poids figés','Score'],y=365)
 elif v=='loss':
  for i,(a,b,d) in enumerate([('Binaire','1 logit','BCEWithLogitsLoss'),('Multiclasse','K logits + classe entière','CrossEntropyLoss'),('Régression','Valeur réelle','MSE ou MAE')]):
   y=105+i*140;c.box(45,y,270,105,a,BLUE,WHITE);c.box(350,y,385,105,b,PALE);c.box(770,y,385,105,d,PALE,size=22);c.line(320,y+52,345,y+52,arrow=True);c.line(740,y+52,765,y+52,arrow=True)
 elif v=='gradient':
  x,y,w,h=c.axis(90,100,960,345,'Valeur du paramètre w','L(w) = (w - 3)²');xx=np.linspace(-4,7,90);yy=(xx-3)**2/50;c.path([(x+(t+4)/11*w,y+h-u*h) for t,u in zip(xx,yy)],BLUE,4)
  for t in [-4,-2.6,-1.48,-.584,.133,3]:c.circle(x+(t+4)/11*w,y+h-(t-3)**2/50*h,9,RED if t<2 else GREEN)
  c.text(770,150,'Minimum : w = 3',29,GREEN,True)
 elif v in ['lr','curves','calibration']:chart_curves(c,v)
 elif v=='timeline':
  c.line(100,288,1095,288,BLUE,5)
  for i,(a,b) in enumerate([('1997','LSTM'),('2012','AlexNet'),('2015','BatchNorm / ResNet'),('2017','Transformer')]):
   x=120+i*320;c.circle(x,288,15,BLUE);c.text(x,240,a,40,BLUE,True,'middle');c.text(x,350,b,21,MUTED,True,'middle')
  c.text(600,461,'Mémoire → calcul GPU → profondeur → attention',25,MUTED,False,'middle')
 elif v in ['framework','stack']:
  c.box(125,85,950,125,'Keras 3 : API de haut niveau',BLUE,WHITE,size=34)
  for i,t in enumerate(['TensorFlow','PyTorch','JAX']):c.box(75+i*390,282,345,145,t,[GREEN,BLUE,NAVY][i],WHITE,sub='Moteur de calcul',size=31);c.line(600,218,247+i*390,270,LINE,3,True)
  c.text(600,500,'Accès natif possible aux tenseurs, gradients et boucles.',25,MUTED,False,'middle')
 elif v in ['code_torch','code_keras']:
  code=['optimizer.zero_grad()','prediction = model(x)','loss = criterion(prediction, y)','loss.backward()','optimizer.step()'] if v=='code_torch' else ['model = keras.Sequential([...])','model.compile(optimizer="adam",','    loss="binary_crossentropy")','model.fit(X_train, y_train,','    validation_data=(X_val, y_val))']
  c.rect(50,88,1100,415,NAVY)
  for i,l in enumerate(code):c.text(90,155+i*68,l,31,WHITE,False)
 elif v in ['split','timesplit']:
  labs=['ENTRAÎNEMENT','VALIDATION','TEST'];ws=[644,138,138];x=125
  for lab,ww,col in zip(labs,ws,[BLUE,GREEN,RED]):c.rect(x,205,ww,130,col,r=0);c.text(x+ww/2,185,lab,20,col,True,'middle');c.text(x+ww/2,283,'70 %' if lab==labs[0] else '15 %',28,WHITE,True,'middle');x+=ww+8
  c.line(120,411,1085,411,MUTED,3,True);c.text(600,451,'Temps →' if v=='timesplit' else 'Rôles différents : ajuster, choisir, estimer',27,MUTED,True,'middle');c.text(600,520,'Répartition illustrative ; le protocole dépend du problème.',20,MUTED,False,'middle')
 elif v=='imbalance':
  c.text(85,205,'99 %',107,BLUE,True);c.text(80,255,'d’exactitude',28,MUTED)
  c.text(715,205,'0 %',107,RED,True);c.text(710,255,'de rappel',28,MUTED)
  c.box(80,320,1030,150,'Toujours prédire « négatif » :\n9 900 négatifs et 100 positifs',PALE,size=29)
 elif v=='confusion':
  c.text(570,95,'PRÉDICTION',23,MUTED,True,'middle');c.text(427,139,'Négatif',22,BLUE,True,'middle');c.text(757,139,'Positif',22,RED,True,'middle')
  vals=[('Vrais négatifs','9 870',PALE),('Faux positifs','30','#FCE8E8'),('Faux négatifs','20','#FCE8E8'),('Vrais positifs','80','#E8F5E9')]
  for i,(a,b,col) in enumerate(vals):x=270+(i%2)*330;y=166+(i//2)*148;c.box(x,y,310,135,a,col,sub=b,size=25)
  c.text(45,240,'Réel négatif',19,MUTED,True);c.text(45,390,'Réel positif',19,MUTED,True)
  c.text(600,510,'Précision : 80/110 = 72,7 %   •   Rappel : 80/100 = 80 %',25,BLUE,True,'middle')
 elif v=='threshold':
  rng=random.Random(5);c.line(95,350,1110,350,MUTED,3)
  for i in range(43):x=100+rng.random()*1000;c.circle(x,290+rng.random()*110,7,BLUE if rng.random()<.7 else RED)
  for x,lab in [(400,'0,3'),(600,'0,5'),(900,'0,8')]:c.line(x,195,x,425,GREEN,3,False,'7 6');c.text(x,165,lab,27,GREEN,True,'middle')
  c.text(100,454,'0',25,MUTED);c.text(1105,454,'1',25,MUTED);c.text(600,514,'Le seuil règle la charge et les erreurs ; il n’est pas « donné » par le score.',24,BLUE,True,'middle')
 elif v in ['journal','checklist','diagnostic','quiz']:
  labels= {'journal':['Hypothèse','Modification','Effet attendu','Résultat','Interprétation','Décision'], 'checklist':['Versions','Tenseurs','Gradients','Données locales','CPU / GPU','Écriture fichier'], 'diagnostic':['Python','Données','Validation','Paramètres','Métriques','Besoin métier'], 'quiz':['Sortie / perte','Gradient','Validation','Classes rares','CNN / LSTM','Supervision']}[v]
  for i,t in enumerate(labels):x=45+(i%3)*390;y=110+(i//3)*205;c.box(x,y,355,165,t,PALE,size=28);c.circle(x+35,y+35,18,BLUE);c.text(x+35,y+42,str(i+1),19,WHITE,True,'middle')
 elif v in ['digits','errors','augmentation']:
  d=np.load(ROOT/'03_Travaux_pratiques/donnees/chiffres_8x8.npz');im=d['images'];tar=d['target']
  for j in range(8):
   ix=int(np.where(tar==j)[0][0]);x=40+(j%4)*297;y=85+(j//4)*226;c.grid(x+50,y,im[ix],size=19,labels=False);c.text(x+125,y+186,'Classe '+str(j),22,BLUE,True,'middle')
  if v=='errors':c.text(1120,536,'Exemples du jeu, pas erreurs mesurées.',15,MUTED,False,'end')
 elif v=='mlpcnn':
  c.text(60,108,'MLP',30,BLUE,True);c.flow(['Image','Aplatir','Dense','Classe'],y=141)
  c.text(60,337,'CNN',30,GREEN,True);c.flow(['Image','Filtres locaux','Réduire l’espace','Classe'],y=370)
 elif v in ['convolution','padding','pooling','receptive']:
  if v=='convolution':
   a=np.array([[1,0,2,1,0],[2,1,0,2,1],[0,1,2,0,1],[1,0,1,2,0],[2,1,0,1,2]]);c.grid(40,123,a,58,high={(i,j) for i in range(3) for j in range(3)});c.text(185,467,'Entrée 5 × 5',25,BLUE,True,'middle');c.text(402,291,'×',51,MUTED);k=np.array([[1,0,-1],[1,0,-1],[1,0,-1]]);c.grid(478,168,k,65);c.text(576,467,'Filtre 3 × 3',25,BLUE,True,'middle');c.line(724,292,805,292,arrow=True);c.box(845,200,292,170,'Σ produits = -1',GREEN,WHITE,size=28)
  elif v=='pooling':
   a=np.array([[1,4,2,0],[3,2,8,1],[1,5,0,6],[2,1,7,3]]);c.grid(85,134,a,76);c.text(237,494,'Fenêtres 2 × 2',27,BLUE,True,'middle');c.line(465,285,641,285,arrow=True);c.grid(736,172,np.array([[4,8],[5,7]]),110);c.text(850,465,'Maximum local',27,GREEN,True,'middle')
  elif v=='padding':
   c.grid(50,155,np.pad(np.ones((4,4),int),1),47);c.box(420,145,720,100,'Sortie = ⌊(entrée + 2p - k) / s⌋ + 1',PALE,size=27);c.box(420,305,720,145,'8 pixels, filtre 3, pas 1, bord 1\n→ sortie de 8 pixels',BLUE,WHITE,size=28)
  else:
   
   for i in range(7):
    for j in range(7):c.rect(55+j*42,138+i*42,39,39,BLUE if 1<=i<=5 and 1<=j<=5 else PALE,r=2)
   for i in range(5):
    for j in range(5):c.rect(495+j*42,180+i*42,39,39,GREEN if 1<=i<=3 and 1<=j<=3 else PALE,r=2)
   c.line(377,285,469,285,arrow=True);c.line(747,285,881,285,arrow=True);c.circle(986,285,36,RED)
   c.text(205,476,'Champ 5 × 5 dans l’entrée',22,BLUE,True,'middle');c.text(602,476,'Voisinage 3 × 3',22,GREEN,True,'middle');c.text(986,476,'Une sortie',22,RED,True,'middle')
   c.text(600,525,'Deux convolutions 3 × 3 de pas 1 : le champ théorique grandit.',23,MUTED,False,'middle')
 elif v=='parameters':
  c.box(65,118,495,180,'Convolution :\n(3 × 3 × 1 + 1) × 8 = 80',BLUE,WHITE,size=31);c.box(635,118,495,180,'Dense :\n64 × 32 + 32 = 2 080',GREEN,WHITE,size=31)
  c.text(600,389,'Comparer aussi les sorties et les opérations.',27,MUTED,True,'middle');c.text(600,447,'Moins de paramètres n’est pas une preuve automatique de qualité.',23,MUTED,False,'middle')
 elif v=='rnn':
  for i in range(5):x=58+i*232;c.box(x,215,177,100,'Cellule',BLUE,WHITE);c.box(x+15,385,147,70,'x'+str(i+1),PALE,size=24);c.line(x+88,378,x+88,323,arrow=True);c.text(x+88,155,'h'+str(i+1),26,BLUE,True,'middle');c.line(x+88,208,x+88,173,arrow=True)
  for i in range(4):c.line(240+i*232,265,285+i*232,265,arrow=True)
  c.text(600,507,'Les mêmes paramètres sont réutilisés à chaque pas.',27,MUTED,True,'middle')
 elif v=='lstm':
  c.rect(90,95,1015,405,PALE);c.line(20,165,1170,165,BLUE,5,True);c.text(540,126,'Mémoire de cellule cₜ',26,BLUE,True,'middle')
  for i,t in enumerate(['OUBLI','ÉCRITURE','SORTIE']):x=165+i*328;c.box(x,247,238,110,t,[BLUE,GREEN,NAVY][i],WHITE,size=26);c.line(x+119,239,x+119,180,LINE,4,True)
  c.text(150,458,'Entrée xₜ + état précédent hₜ₋₁',27,MUTED);c.text(960,458,'État hₜ',27,BLUE,True)
 elif v=='vanishing':
  for i,(name,val,col) in enumerate([('0,5¹⁰',.5**10,BLUE),('1¹⁰',1,GREEN),('2¹⁰',2**10,RED)]):
   c.box(55+i*395,140,350,290,name,PALE,size=42);c.text(230+i*395,365,('≈ 0,001' if i==0 else '1' if i==1 else '1 024'),35,col,True,'middle')
  c.text(600,501,'Produit répété : atténuation, maintien ou amplification.',26,MUTED,False,'middle')
 elif v=='window':
  xs=np.linspace(85,1115,56);ys=[275-76*math.sin(i*.31)-i*.6 for i in range(56)];c.path(list(zip(xs,ys)),BLUE,4);c.rect(xs[12]-8,128,xs[35]-xs[12]+16,293,'none',GREEN,12,4);c.circle(xs[36],ys[36],13,RED);c.text(510,477,'24 observations passées',26,GREEN,True,'middle');c.text(880,477,'Cible suivante',26,RED,True,'middle');c.line(870,430,xs[36],ys[36]+20,RED,3,True)
 elif v=='diagnosticmatrix':
  cols=[48,398,760];headers=['SYMPTÔME','TEST','ACTION CANDIDATE'];ww=[330,340,385]
  rows=[['Train bon, validation mauvaise','Vérifier split et courbes','Régularisation / données'],['Perte instable','Réduire le taux à données fixes','Taux / normalisation'],['Rien n’apprend','Mémoriser 32 exemples','Corriger données / boucle'],['Score global flatteur','Examiner positifs et alertes','Métrique / seuil']]
  for x,w,t in zip(cols,ww,headers):c.box(x,85,w,60,t,BLUE,WHITE,size=21)
  for i,row in enumerate(rows):
   for x,w,t in zip(cols,ww,row):c.box(x,160+i*92,w,80,t,PALE,size=20)
 elif v=='tinybatch':
  for i in range(32):c.rect(65+(i%8)*48,155+(i//8)*62,35,46,BLUE,r=5)
  c.line(482,267,581,267,arrow=True);c.nodes(650,106,395,290);c.text(265,470,'32 exemples',30,BLUE,True,'middle');c.text(855,470,'Peut-il les mémoriser ?',30,GREEN,True,'middle')
 elif v=='dropout':
  c.nodes(85,92,425,360,False);c.nodes(695,92,425,360,True);c.text(280,500,'Évaluation : réseau actif',26,BLUE,True,'middle');c.text(900,500,'Entraînement : masque aléatoire',25,GREEN,True,'middle')
 elif v=='batchnorm':
  c.flow(['Activations','Centrer / réduire','Échelle + décalage appris','Sorties'],y=170);c.box(100,370,455,116,'Train : statistiques du lot',BLUE,WHITE,size=24);c.box(640,370,455,116,'Évaluation : statistiques suivies',GREEN,WHITE,size=24)
 elif v=='transfer':
  c.text(55,115,'1. APPRENDRE UNE TÊTE',24,BLUE,True);c.flow(['Bloc gelé','Bloc gelé','Nouvelle tête'],y=145,colors=[PALE,PALE,GREEN]);c.text(55,342,'2. AJUSTER AVEC PRUDENCE',24,GREEN,True);c.flow(['Bloc gelé','Bloc ajustable','Tête'],y=370,colors=[PALE,BLUE,GREEN])
 elif v=='topk':
  for row,name,count,col in [(0,'Modèle A',20,BLUE),(1,'Modèle B',35,GREEN)]:
   yy=120+row*211;c.text(50,yy+62,name,27,col,True);c.rect(265,yy,660,135,PALE)
   for i in range(50):c.circle(288+(i%25)*25,yy+43+(i//25)*48,8,col if i<count else LINE)
   c.text(995,yy+52,str(count)+'/50',30,col,True,'middle');c.text(995,yy+95,'utiles',22,MUTED,False,'middle')
  c.text(600,516,'Comparer la qualité dans le budget réel de revue.',28,MUTED,True,'middle')
 elif v=='drift':
  x,y,w,h=c.axis(xlabel='Variable / score',ylabel='Densité (schéma)');xx=np.linspace(-4,5,120)
  for mu,col,lab,offset in [(0,BLUE,'Période initiale',0),(1.6,RED,'Période récente',420)]:
   vals=np.exp(-(xx-mu)**2/2)*.8;c.path([(x+(t+4)/9*w,y+h-u*h) for t,u in zip(xx,vals)],col,4);c.text(190+offset,515,lab,24,col,True)
 elif v in ['case_foncier','case_cfvr','case_health']:
  texts={'case_foncier':['Image aérienne','Anomalie candidate','Rapprochement','Vérification humaine'],'case_cfvr':['Grandes bases','Datamining','Dossiers ciblés','Examen par agent'],'case_health':['Volume OCT','Segmentation','Orientation','Protocole clinique']}[v]
  c.flow(texts,y=210);c.box(120,407,960,92,'Cas documenté ≠ reproduction de l’architecture interne',PALE,size=27)
 elif v=='aerial':
  for i,(lab,col) in enumerate([('Candidat pertinent',GREEN),('Objet ressemblant',RED),('Objet manqué',RED),('Absence pertinente',BLUE)]):
   x=30+i*297;c.rect(x,107,267,330,'#F0F4ED');c.rect(x+25,147,118,84,'#BEC5C0');c.rect(x+160,210,77,149,'#D9DFD2');
   if i!=3:c.rect(x+58,290,87,59,'#67A6CD',r=6)
   if i<2:c.rect(x+49,281,105,77,'none',col,5,4)
   c.text(x+133,483,lab,20,col,True,'middle')
  c.text(600,524,'Vignettes fictives ; aucun bien réel représenté.',22,MUTED,False,'middle')
 elif v=='oct':
  for k,col in enumerate([BLUE,GREEN,RED]):
   pts=[(55+t*2.8,205+k*36+22*math.sin(t*.045)+8*math.sin(t*.14)) for t in range(155)];c.path(pts,col,9)
  c.text(260,465,'Tissus (schéma)',27,BLUE,True,'middle');c.line(530,286,618,286,arrow=True);c.box(650,142,485,128,'Segmentation intermédiaire',BLUE,WHITE,size=28);c.box(650,326,485,128,'Orientation clinique',GREEN,WHITE,size=28);c.line(890,279,890,314,arrow=True)
 elif v=='costmatrix':
  for i,(a,b,col) in enumerate([('Faux positif','Revue inutile',PALE),('Faux négatif','Cas pertinent manqué','#FCE8E8'),('Abstention','Revue complémentaire','#FFF9DC'),('Résultat vérifié','Suite selon protocole','#E8F5E9')]):
   x=55+(i%2)*600;y=103+(i//2)*200;c.box(x,y,545,170,a,col,sub=b,size=29)
 elif v=='documents':
  for i in range(4):c.rect(65+i*24,122+i*27,235,235,WHITE,LINE);[c.line(88+i*24,165+i*27+j*29,260+i*24,165+i*27+j*29,LINE,3) for j in range(5)]
  c.line(407,280,503,280,arrow=True);c.box(526,215,252,133,'Traitement texte',BLUE,WHITE,size=27);c.line(788,270,879,182,arrow=True);c.line(788,297,879,405,arrow=True);c.box(898,105,270,134,'Routage',GREEN,WHITE,size=28);c.box(898,353,270,134,'Résumé',PALE,size=28)
 elif v=='humanloop':
  c.text(60,115,'SUPERVISION FORMELLE',23,RED,True);c.flow(['Score','Clic automatique','Décision'],y=145)
  c.text(60,342,'SUPERVISION EFFECTIVE',23,GREEN,True);c.flow(['Score + limites','Dossier source','Agent peut contester','Décision motivée'],y=372)
 elif v=='testlock':
  c.box(80,112,470,343,'VALIDATION',BLUE,WHITE,sub='Choix, réglages, analyses',size=44);c.box(650,112,470,343,'TEST',RED,WHITE,sub='Une évaluation finale',size=44)
  c.text(600,518,'Ne pas réajuster après avoir observé le test.',28,MUTED,True,'middle')
 elif v=='executive':
  c.box(40,105,290,390,'Problème\nDonnées',PALE,size=32);c.box(352,105,456,390,'Protocole\nComparaison\nMétriques',BLUE,WHITE,size=32);c.box(832,105,328,390,'Risques\nRecommandation',GREEN,WHITE,size=31)
 elif v=='rubric':
  for i,(n,t,col) in enumerate([('45','Problème, données, protocole',BLUE),('35','Baseline, architecture, métriques',GREEN),('20','Erreurs, limites, décision',RED)]):
   x=48+i*398;c.rect(x,111,355,373,PALE);c.text(x+177,266,n,100,col,True,'middle');c.text(x+177,331,'POINTS',21,MUTED,True,'middle');c.text(x+177,387,t,20,INK,False,'middle',width=24)
 elif v in ['incident','segments','casegrid','sectors','taskcards','dataset','tpboard','repro']:
  texts={
   'incident':['Symptôme','Hypothèse','Test discriminant','Correction','Preuve','Limite'],
   'segments':['Classe','Période','Source','Qualité','Effectif','Erreur'],
   'casegrid':['Problème / cible','Données','Modèle / protocole','Métrique','Workflow humain','Risques / limites'],
   'sectors':['Contrôle','Vision / foncier','Santé','Finance','Maintenance','Documents'],
   'taskcards':['Classer','Prédire une valeur','Localiser','Segmenter','Trier / router','Aider la revue'],
   'dataset':['Observation','Variables','Cible','Date','Provenance','Disponibilité'],
   'tpboard':['Ouvrir le notebook','Lire les données','Construire','Exécuter','Vérifier','Documenter'],
   'repro':['Graine','Indices','Données figées','Versions','Configuration','Paramètres']
  }[v]
  for i,t in enumerate(texts):c.box(40+(i%3)*395,112+(i//3)*213,365,169,t,BLUE if i==0 else PALE,WHITE if i==0 else INK,size=26)
 elif v in FLOW:c.flow(FLOW[v],colors=[BLUE]+[PALE]*(len(FLOW[v])-2)+[GREEN] if len(FLOW[v])>1 else [BLUE])
 else:
  for i,t in enumerate(s['items'][:3]):c.box(75,106+i*143,1050,112,t,BLUE if i==0 else PALE,WHITE if i==0 else INK,size=27)
 c.foot('Schéma pédagogique • source : voir les notes de la diapositive' if v.startswith('case_') else ('Données locales : chiffres manuscrits 8 × 8 (scikit-learn / UCI)' if v in ['digits','errors','augmentation'] else 'Schéma pédagogique • valeurs d’illustration, sauf indication contraire'))
 c.save(f"{s['id']:03d}_{v}")

if __name__=='__main__':
 for s in SLIDES:make(s)
 # Seule une portion décorative sans allégation chiffrée du visuel imagegen est retenue.
 (OUT/'LISEZ_MOI.md').write_text('# Illustrations du cours 4-024\n\nLes 126 schémas sont fournis en SVG éditable et PNG. Les courbes conceptuelles portent la mention pédagogique et ne sont pas des mesures. Les chiffres manuscrits proviennent du jeu fourni. Les cas DGFiP sont des transpositions explicatives, pas des captures internes.\n\n`detail_reseau_imagegen.png` est une portion décorative de l’image produite avec imagegen durant cette conversation. Les mentions promotionnelles de cette image ne sont pas utilisées.\n')
 print('Schémas produits :',len(SLIDES))
