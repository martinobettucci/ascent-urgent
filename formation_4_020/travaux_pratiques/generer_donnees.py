from pathlib import Path
import numpy as np
import pandas as pd

def creer_donnees(dossier: Path, n: int = 5000, graine: int = 4020) -> pd.DataFrame:
    """Crée des clients purement synthétiques. Aucun enregistrement réel."""
    if n < 100: raise ValueError("Au moins 100 observations sont nécessaires.")
    dossier.mkdir(parents=True, exist_ok=True)
    r = np.random.default_rng(graine)
    anciennete = r.integers(1, 73, n)
    contrat = r.choice(["mensuel", "annuel", "bisannuel"], n, p=[.55,.3,.15])
    depense = np.round(r.uniform(19, 149, n), 2)
    tickets = r.poisson(1.5, n)
    retard = r.poisson(.45, n)
    sessions = r.poisson(18, n)
    satisfaction = np.clip(r.normal(7.2, 1.7, n), 1, 10).round(1)
    remise = r.choice([0.,.05,.10,.20], n, p=[.55,.2,.2,.05])
    produits = r.integers(1, 5, n)
    paiement = r.choice(["prelevement","carte","virement"], n, p=[.5,.4,.1])
    z = (-2.2 + .42*tickets + .55*retard - .018*anciennete
         + .012*(depense-70) - .055*(sessions-18)
         + .50*(6-satisfaction) + .75*(contrat=="mensuel")
         - .6*(contrat=="bisannuel") + .5*((tickets>3)&(satisfaction<5)))
    p = 1/(1+np.exp(-z))
    cible = r.binomial(1,p)
    df = pd.DataFrame({"customer_id":[f"NOV-{i:05}" for i in range(n)],
        "tenure_months":anciennete, "monthly_spend":depense,
        "support_tickets_90d":tickets,"late_payments_12m":retard,
        "digital_sessions_30d":sessions,"contract_type":contrat,
        "payment_method":paiement,"satisfaction_score":satisfaction,
        "discount_rate":remise,"products_owned":produits,"churn":cible})
    # Les valeurs manquantes sont intentionnelles et décrites dans le dictionnaire.
    for c in ["satisfaction_score","monthly_spend"]:
        df.loc[r.choice(n,int(.02*n),replace=False),c] = np.nan
    df.to_csv(dossier/"novalia_clients.csv",index=False)
    audit=df.head(40).copy()
    audit.loc[0,"monthly_spend"]=-49
    audit.loc[1,"tenure_months"]=-3
    audit.loc[2,"contract_type"]=" Mensuel "
    audit.loc[3,"satisfaction_score"]=18
    audit.loc[4,"customer_id"]=audit.loc[5,"customer_id"]
    audit.loc[6,"satisfaction_score"]=np.nan
    audit["snapshot_date"]="2026-01-31"
    audit["last_refresh"]="2026-01-31"
    audit.loc[7,"last_refresh"]="2024-01-01"
    # Colonne délibérément postérieure à la décision : jamais dans le modèle normal.
    audit["cancellation_request_date"] = np.where(audit.churn==1,"2026-02-15",None)
    audit.to_csv(dossier/"novalia_audit_qualite.csv",index=False)
    return df

if __name__ == "__main__":
    df=creer_donnees(Path(__file__).resolve().parent)
    print(f"{len(df)} clients synthétiques créés.")
