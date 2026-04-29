"""
STB Credit Risk Platform — Application Streamlit
=================================================
Lancez avec : streamlit run app.py

Structure :
  app.py          ← ce fichier (point d'entrée)
  model_utils.py  ← coefficients du modèle et fonctions de calcul
  requirements.txt

Pages :
  1. Scoring Client    — entrer les variables d'un client → PD instantanée
  2. Stress Simulator  — sliders macro → NPL + coussin capital en temps réel
  3. Tableau de Bord   — résultats de la thèse, scorecard, ROC curve
"""
# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(
    page_title="STB · Credit Risk Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0a0e1a;
    --bg2:       #111827;
    --bg3:       #1a2235;
    --border:    #1e3a5f;
    --accent:    #00d4ff;
    --accent2:   #ff6b35;
    --accent3:   #00ff88;
    --danger:    #ff3b5c;
    --warn:      #ffb020;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --font-mono: 'IBM Plex Mono', monospace;
    --font-sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font-sans);
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg2);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    color: var(--muted);
    padding: 0.4rem 0;
    cursor: pointer;
    transition: color 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--accent);
}

/* Metric cards */
.metric-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.metric-card.danger::before  { background: var(--danger); }
.metric-card.warn::before    { background: var(--warn); }
.metric-card.success::before { background: var(--accent3); }
.metric-card.orange::before  { background: var(--accent2); }

.metric-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: var(--font-mono);
    font-size: 2rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* Section headers */
.section-header {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    margin-top: 0.5rem;
}

/* Page title */
.page-title {
    font-family: var(--font-mono);
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.02em;
}
.page-subtitle {
    font-family: var(--font-sans);
    font-size: 0.9rem;
    color: var(--muted);
    margin-top: 0.25rem;
    margin-bottom: 2rem;
}

/* Gauge container */
.gauge-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.risk-low      { background: #00ff8820; color: #00ff88; border: 1px solid #00ff8840; }
.risk-moderate { background: #ffb02020; color: #ffb020; border: 1px solid #ffb02040; }
.risk-high     { background: #ff6b3520; color: #ff6b35; border: 1px solid #ff6b3540; }
.risk-critical { background: #ff3b5c20; color: #ff3b5c; border: 1px solid #ff3b5c40; }

/* Scorecard table */
.score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}
.score-row:last-child { border-bottom: none; }
.check-pass { color: var(--accent3); font-family: var(--font-mono); }
.check-fail { color: var(--danger);  font-family: var(--font-mono); }

/* Streamlit overrides */
.stSlider > div > div { background: var(--border) !important; }
div[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}
.stButton > button {
    background: var(--accent);
    color: var(--bg);
    border: none;
    font-family: var(--font-mono);
    font-weight: 600;
    letter-spacing: 0.08em;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #33ddff;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px #00d4ff40;
}
.stSelectbox > div, .stNumberInput > div {
    background: var(--bg2) !important;
    border-color: var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 2rem 0;'>
        <div style='font-family:"IBM Plex Mono",monospace; font-size:1.1rem;
                    font-weight:600; color:#00d4ff; letter-spacing:-0.02em;'>
            STB · CRP
        </div>
        <div style='font-size:0.7rem; color:#64748b; margin-top:0.2rem;
                    font-family:"IBM Plex Mono",monospace; letter-spacing:0.1em;'>
            CREDIT RISK PLATFORM
        </div>
        <div style='margin-top:1rem; padding-top:1rem; border-top:1px solid #1e3a5f;
                    font-size:0.7rem; color:#64748b;'>
            Mémoire de Master · 2025
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        options=["01 · Client Scoring",
                 "02 · Stress Simulator",
                 "03 · Model Dashboard"],
        label_visibility="visible",
    )

    st.markdown("""
    <div style='position:absolute; bottom:2rem; left:1rem; right:1rem;
                font-size:0.65rem; color:#334155; font-family:"IBM Plex Mono",monospace;
                line-height:1.6;'>
        Probit Stage 2<br>
        AUC = 0.9239 · Gini = 0.8478<br>
        AR(1) + Chômage + Inflation<br>
        R²adj = 0.939 · N = 327k clients
    </div>
    """, unsafe_allow_html=True)

# ── Route to pages ────────────────────────────────────────────────────────────
if page == "01 · Client Scoring":
    from pages.page_scoring import render
    render()
elif page == "02 · Stress Simulator":
    from pages.page_stress import render
    render()
else:
    from pages.page_dashboard import render
    render()
