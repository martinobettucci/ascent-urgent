"""Utilitaires lisibles pour la formation 4-024. Aucun accès réseau nécessaire.

Les données et modèles sont pédagogiques. Aucune décision concernant une personne
réelle ne doit être prise à partir de ces exercices.
"""
from __future__ import annotations
import os
os.environ.setdefault('KERAS_BACKEND', 'torch')
from pathlib import Path
import json, random, time
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, mean_absolute_error,
    mean_squared_error, brier_score_loss)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'donnees'
RESULTS = BASE / 'resultats'
RESULTS.mkdir(exist_ok=True)

def seed_all(seed: int = 42) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(min(2, os.cpu_count() or 1))

seed_all()

def read_tabular(rare: bool = False):
    df = pd.read_csv(DATA / ('priorisation_rare.csv' if rare else 'dossiers_synthetiques.csv'))
    columns = [f'v{i:02d}' for i in range(20)]
    assert 'resultat_apres_examen' not in columns
    return df, df[columns].to_numpy(np.float32), df['examen_utile'].to_numpy(np.int64)

def split_tabular(rare: bool = False):
    df, X, y = read_tabular(rare)
    idx = np.arange(len(y))
    tr, rest = train_test_split(idx, test_size=.30, random_state=42, stratify=y)
    va, te = train_test_split(rest, test_size=.5, random_state=43, stratify=y[rest])
    scaler = StandardScaler().fit(X[tr])
    result = {'indices':(tr,va,te), 'scaler':scaler, 'df':df}
    for name, rows in zip(('train','validation','test'),(tr,va,te)):
        result[name] = (scaler.transform(X[rows]).astype(np.float32), y[rows])
    assert not set(tr)&set(va) and not set(tr)&set(te) and not set(va)&set(te)
    return result

def digits_data():
    d = np.load(DATA/'chiffres_8x8.npz')
    images = d['images'].astype(np.float32) / 16.0
    labels = d['target'].astype(np.int64)
    tr, rest = train_test_split(np.arange(len(labels)), test_size=.3, stratify=labels, random_state=42)
    va, te = train_test_split(rest, test_size=.5, stratify=labels[rest], random_state=43)
    return {name:(images[ix,None,:,:],labels[ix]) for name,ix in zip(('train','validation','test'),(tr,va,te))}

class BinaryMLP(nn.Module):
    def __init__(self, n_features=20, width=32, dropout=0.0):
        super().__init__()
        self.network=nn.Sequential(nn.Linear(n_features,width),nn.ReLU(),nn.Dropout(dropout),
                                   nn.Linear(width,16),nn.ReLU(),nn.Linear(16,1))
    def forward(self,x): return self.network(x).squeeze(-1)

class DenseDigits(nn.Module):
    def __init__(self):
        super().__init__();self.network=nn.Sequential(nn.Flatten(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,10))
    def forward(self,x): return self.network(x)

class TinyCNN(nn.Module):
    def __init__(self,dropout=0.0):
        super().__init__()
        self.features=nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                                    nn.Conv2d(8,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2))
        self.head=nn.Sequential(nn.Flatten(),nn.Dropout(dropout),nn.Linear(16*2*2,10))
    def forward(self,x): return self.head(self.features(x))

class TinyLSTM(nn.Module):
    def __init__(self,hidden=16):
        super().__init__();self.recurrent=nn.LSTM(1,hidden,batch_first=True);self.head=nn.Linear(hidden,1)
    def forward(self,x):
        z,_=self.recurrent(x);return self.head(z[:,-1,:]).squeeze(-1)

class TextMLP(nn.Module):
    def __init__(self,n_features,n_classes=4):
        super().__init__();self.network=nn.Sequential(nn.Linear(n_features,32),nn.ReLU(),nn.Linear(32,n_classes))
    def forward(self,x):return self.network(x)

def tensor_pair(X,y,task):
    return torch.as_tensor(X,dtype=torch.float32),torch.as_tensor(y,dtype=torch.long if task=='multi' else torch.float32)

def fit_model(model, train, validation, *, task='binary', epochs=10, lr=.003,
              batch_size=64, weight_decay=0.0, pos_weight=None, patience=None, verbose=False):
    """Boucle explicite : forward, perte, backward, step. Validation sans gradient.
    Retourne le meilleur état de validation si patience est renseignée, sinon le dernier.
    """
    if epochs<1 or batch_size<1: raise ValueError('epochs et batch_size doivent être positifs.')
    seed_all()
    X,y=tensor_pair(*train,task); VX,Vy=tensor_pair(*validation,task)
    loader=DataLoader(TensorDataset(X,y),batch_size=batch_size,shuffle=True,
                      generator=torch.Generator().manual_seed(42))
    if task=='binary':
        criterion=nn.BCEWithLogitsLoss(pos_weight=None if pos_weight is None else torch.tensor(float(pos_weight)))
    elif task=='multi': criterion=nn.CrossEntropyLoss()
    elif task=='regression':criterion=nn.MSELoss()
    else:raise ValueError('Tâche inconnue')
    optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=lr,weight_decay=weight_decay)
    history=[];best=float('inf');best_state=None;wait=0
    for epoch in range(epochs):
        model.train();total=0.0
        for xb,yb in loader:
            optimizer.zero_grad(set_to_none=True)
            output=model(xb);loss=criterion(output,yb)
            if not torch.isfinite(loss):raise FloatingPointError('Perte non finie : vérifier données et taux.')
            loss.backward()
            if task=='regression':nn.utils.clip_grad_norm_(model.parameters(),1.0)
            optimizer.step();total+=loss.item()*len(xb)
        model.eval()
        with torch.no_grad():v_loss=criterion(model(VX),Vy).item()
        history.append({'epoque':epoch+1,'perte_train':total/len(X),'perte_validation':v_loss})
        if verbose:print(history[-1])
        if v_loss<best-1e-7:
            best=v_loss;best_state={k:v.detach().clone() for k,v in model.state_dict().items()};wait=0
        else:wait+=1
        if patience is not None and wait>=patience:break
    if patience is not None and best_state is not None:model.load_state_dict(best_state)
    model.eval()
    return pd.DataFrame(history)

def predict(model,X,task='binary'):
    model.eval()
    with torch.no_grad():
        out=model(torch.as_tensor(X,dtype=torch.float32))
        if task=='binary':out=torch.sigmoid(out)
        elif task=='multi':out=torch.softmax(out,dim=-1)
        return out.numpy()

def binary_metrics(y,score,threshold=.5):
    y=np.asarray(y);score=np.asarray(score);p=(score>=threshold).astype(int)
    if not np.isfinite(score).all():raise ValueError('Scores non finis')
    return dict(seuil=float(threshold),exactitude=float(accuracy_score(y,p)),precision=float(precision_score(y,p,zero_division=0)),
        rappel=float(recall_score(y,p,zero_division=0)),f1=float(f1_score(y,p,zero_division=0)),
        roc_auc=float(roc_auc_score(y,score)),precision_moyenne_AP=float(average_precision_score(y,score)),
        brier=float(brier_score_loss(y,score)),alertes=int(p.sum()))

def topk_metrics(y,score,k):
    if not 1<=k<=len(y):raise ValueError('k doit être compris entre 1 et le nombre d’observations')
    ix=np.argsort(-np.asarray(score),kind='stable')[:k];n=int(np.asarray(y)[ix].sum())
    return dict(k=k,cas_pertinents=n,precision_a_k=n/k,rappel_a_k=n/max(1,int(np.sum(y))))

def save_result(name,data):
    path=RESULTS/f'{name}.json'
    def encode(o):
        if isinstance(o,np.generic):return o.item()
        if isinstance(o,np.ndarray):return o.tolist()
        if isinstance(o,Path):return str(o)
        raise TypeError(type(o).__name__)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=encode))
    return path

def plot_history(history,title='Courbes d’apprentissage',filename=None):
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,4))
    for col,label in [('perte_train','Entraînement'),('perte_validation','Validation')]:ax.plot(history['epoque'],history[col],label=label)
    ax.set(xlabel='Époque',ylabel='Perte',title=title);ax.legend();ax.grid(alpha=.2);fig.tight_layout()
    if filename:fig.savefig(RESULTS/filename,dpi=150)
    return fig

def sequence_data(window=24):
    df=pd.read_csv(DATA/'serie_synthetique.csv');values=df['valeur'].to_numpy(np.float32)
    cut1=int(.7*len(values));cut2=int(.85*len(values));mu=values[:cut1].mean();sd=values[:cut1].std()
    z=(values-mu)/sd
    xs=[];ys=[];times=[]
    for t in range(window,len(values)):
        xs.append(z[t-window:t,None]);ys.append(z[t]);times.append(t)
    X=np.array(xs,np.float32);y=np.array(ys,np.float32);t=np.array(times)
    out={'mu':float(mu),'sd':float(sd),'df':df,'time':t}
    for name,mask in [('train',t<cut1),('validation',(t>=cut1)&(t<cut2)),('test',t>=cut2)]:out[name]=(X[mask],y[mask])
    return out

def text_data():
    from sklearn.feature_extraction.text import TfidfVectorizer
    df=pd.read_csv(DATA/'documents_synthetiques.csv')
    # Split par famille de gabarits déjà défini dans le fichier, jamais par variante.
    vectorizer=TfidfVectorizer(ngram_range=(1,2),max_features=1000)
    train=df[df.partition=='train'];vectorizer.fit(train.texte)
    out={'vectorizer':vectorizer,'df':df,'classes':['information','paiement','rendez_vous','rectification']}
    for name in ['train','validation','test']:
        part=df[df.partition==name];out[name]=(vectorizer.transform(part.texte).toarray().astype(np.float32),part.classe_id.to_numpy(np.int64))
    groups={name:set(df[df.partition==name].gabarit_id) for name in ['train','validation','test']}
    assert not groups['train']&groups['test'] and not groups['train']&groups['validation']
    return out

def project(track='priorisation',open_test=False):
    """Solution de référence des quatre parcours, adaptée au temps disponible.
    Les choix se font sur validation. open_test=True est réservé à l’audit final.
    """
    seed_all();report={'parcours':track,'test_ouvert':bool(open_test)}
    if track=='priorisation':
        d=split_tabular(True);tr=d['train'];va=d['validation'];model=BinaryMLP()
        h=fit_model(model,tr,va,epochs=14)
        base=LogisticRegression(max_iter=300).fit(*tr);score=predict(model,va[0]);report['validation']=binary_metrics(va[1],score)
        report['baseline']=binary_metrics(va[1],base.predict_proba(va[0])[:,1]);report['capacite']=topk_metrics(va[1],score,30)
        if open_test:report['test_final']=binary_metrics(d['test'][1],predict(model,d['test'][0]))
    elif track=='vision':
        d=digits_data();model=TinyCNN();h=fit_model(model,d['train'],d['validation'],task='multi',epochs=12)
        X,y=d['validation'];p=predict(model,X,'multi').argmax(1)
        base=LogisticRegression(max_iter=300).fit(d['train'][0].reshape(len(d['train'][1]),-1),d['train'][1])
        report['validation']={'exactitude':float(accuracy_score(y,p)),'f1_macro':float(f1_score(y,p,average='macro'))}
        report['baseline']={'exactitude':float(base.score(X.reshape(len(y),-1),y))}
        if open_test:report['test_final']={'exactitude':float(accuracy_score(d['test'][1],predict(model,d['test'][0],'multi').argmax(1)))}
    elif track=='sequence':
        d=sequence_data();model=TinyLSTM();h=fit_model(model,d['train'],d['validation'],task='regression',epochs=12,lr=.003)
        X,y=d['validation'];actual=y*d['sd']+d['mu'];pred=predict(model,X,'regression')*d['sd']+d['mu'];naive=X[:,-1,0]*d['sd']+d['mu']
        report['validation']={'MAE':float(mean_absolute_error(actual,pred)),'RMSE':float(mean_squared_error(actual,pred)**.5)}
        report['baseline']={'MAE_persistance':float(mean_absolute_error(actual,naive))}
        if open_test:
            X,y=d['test'];report['test_final']={'MAE':float(mean_absolute_error(y*d['sd']+d['mu'],predict(model,X,'regression')*d['sd']+d['mu']))}
    elif track=='documents':
        d=text_data();model=TextMLP(d['train'][0].shape[1]);h=fit_model(model,d['train'],d['validation'],task='multi',epochs=12)
        X,y=d['validation'];p=predict(model,X,'multi').argmax(1);base=LogisticRegression(max_iter=300).fit(*d['train'])
        report['validation']={'f1_macro':float(f1_score(y,p,average='macro')),'exactitude':float(accuracy_score(y,p))}
        report['baseline']={'f1_macro':float(f1_score(y,base.predict(X),average='macro'))}
        if open_test:report['test_final']={'f1_macro':float(f1_score(d['test'][1],predict(model,d['test'][0],'multi').argmax(1),average='macro'))}
    else:raise ValueError('Parcours attendu : priorisation, vision, sequence ou documents')
    report['epoques']=len(h);report['limite']='Jeu pédagogique public ou synthétique, aucune validation métier réelle.'
    save_result('projet_'+track,report)
    return report,model,h
