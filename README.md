# STB Credit Risk Platform — Instructions de lancement

## Structure des fichiers

```
app.py               ← point d'entrée principal
model_utils.py       ← coefficients et fonctions de calcul
requirements.txt     ← dépendances Python
pages/
  __init__.py
  page_scoring.py    ← Page 1 : Scoring Client
  page_stress.py     ← Page 2 : Stress Simulator
  page_dashboard.py  ← Page 3 : Tableau de Bord
```

## Installation (une seule fois)

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement sur http://localhost:8501

## Pour la soutenance

1. Lancez `streamlit run app.py` AVANT d'entrer en salle
2. L'application fonctionne 100% hors ligne — pas besoin d'internet
3. Laissez le terminal ouvert en arrière-plan
4. Passez en plein écran dans le navigateur (F11)

## Pages

### 01 · Client Scoring
- Choisissez un profil de démonstration OU entrez les variables manuellement
- La jauge se met à jour instantanément
- Montrez la différence entre le client "sûr" et le client "critique"

### 02 · Stress Simulator  
- Glissez le curseur Chômage vers 19-20% pour le scénario sévère
- Montrez comment le coussin de capital monte à 466 M TND
- Le jury peut interagir directement

### 03 · Model Dashboard
- Vue synthèse de toute la thèse
- ROC curve, comparaison des sets, scorecard 9/10, coussins

## Astuce démonstration

Ordre recommandé pour la présentation :
1. Commencer par le Dashboard (vue d'ensemble)
2. Passer au Scoring (montrer un client sûr puis un client critique)
3. Finir sur le Stress Simulator (laisser le jury manipuler les sliders)
