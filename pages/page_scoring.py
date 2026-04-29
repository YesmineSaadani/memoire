"""pages/page_scoring.py — Page 1 : Scoring Client"""
# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from model_utils import compute_pd, SECTOR_LABELS, PORTFOLIO_MEAN_PD

def make_gauge(pd_value):
    color = ("#00ff88" if pd_value < 0.05 else
             "#ffb020" if pd_value < 0.15 else
             "#ff6b35" if pd_value < 0.35 else
             "#ff3b5c")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(pd_value * 100, 1),
        number={
            'suffix': '%',
            'font': {'size': 42, 'color': color,
                     'family': 'IBM Plex Mono'},
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': '#1e3a5f',
                'tickfont': {'color': '#64748b', 'size': 10,
                             'family': 'IBM Plex Mono'},
            },
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': '#111827',
            'borderwidth': 0,
            'steps': [
                {'range': [0,  5],  'color': '#00ff8812'},
                {'range': [5,  15], 'color': '#ffb02012'},
                {'range': [15, 35], 'color': '#ff6b3512'},
                {'range': [35, 100],'color': '#ff3b5c12'},
            ],
            'threshold': {
                'line': {'color': '#00d4ff', 'width': 2},
                'thickness': 0.75,
                'value': PORTFOLIO_MEAN_PD * 100,
            },
        },
        domain={'x': [0, 1], 'y': [0, 1]},
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='#111827',
        font={'family': 'IBM Plex Mono'},
    )
    fig.add_annotation(
        x=0.5, y=0.12,
        text=f"Moyenne portefeuille : {PORTFOLIO_MEAN_PD*100:.1f}%",
        showarrow=False,
        font={'color': '#00d4ff', 'size': 10, 'family': 'IBM Plex Mono'},
    )
    return fig


def make_comparison_bar(pd_value):
    categories = ['Ce client', 'Moy. portefeuille', 'Seuil modéré', 'Seuil élevé']
    values     = [pd_value * 100, PORTFOLIO_MEAN_PD * 100, 15.0, 35.0]
    colors     = ['#00d4ff', '#64748b', '#ffb020', '#ff3b5c']

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v:.1f}%" for v in values],
        textposition='outside',
        textfont={'family': 'IBM Plex Mono', 'size': 11, 'color': '#e2e8f0'},
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        yaxis=dict(
            showgrid=True, gridcolor='#1e3a5f',
            ticksuffix='%', tickfont={'color': '#64748b',
                                       'family': 'IBM Plex Mono', 'size': 10},
            range=[0, max(max(values) * 1.3, 40)],
        ),
        xaxis=dict(tickfont={'color': '#e2e8f0',
                              'family': 'IBM Plex Mono', 'size': 10}),
        showlegend=False,
    )
    return fig


def render():
    st.markdown('<div class="page-title">01 · Client Scoring</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Calcul instantané de la Probabilité de Défaut '
                '— Modèle Probit Stage 2 · AUC = 0.924</div>',
                unsafe_allow_html=True)

    # ── Layout : formulaire gauche / résultats droite ─────────────────────
    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="section-header">Variables bancaires du client</div>',
                    unsafe_allow_html=True)

        # Profils de démonstration
        st.markdown("**Charger un profil de démonstration**")
        demo = st.selectbox("", [
            "— saisie manuelle —",
            "Client sûr (agriculture, aucun incident)",
            "Client moyen (commerce, AGIOS actifs)",
            "Client à risque (industrie, impayés + provisions)",
            "Client critique (tous les signaux d'alerte)",
        ], label_visibility="collapsed")

        DEMOS = {
            "Client sûr (agriculture, aucun incident)": {
                'eng': 50000, 'ca': 80000, 'imp': 0.0, 'gel': 0.0,
                'pr': 0, 'agios': 0, 'sector': 1,
            },
            "Client moyen (commerce, AGIOS actifs)": {
                'eng': 120000, 'ca': 95000, 'imp': 0.0, 'gel': 0.0,
                'pr': 5000, 'agios': 1, 'sector': 5,
            },
            "Client à risque (industrie, impayés + provisions)": {
                'eng': 350000, 'ca': 180000, 'imp': 0.5, 'gel': 0.3,
                'pr': 45000, 'agios': 1, 'sector': 2,
            },
            "Client critique (tous les signaux d'alerte)": {
                'eng': 800000, 'ca': 60000, 'imp': 1.5, 'gel': 1.2,
                'pr': 250000, 'agios': 1, 'sector': 2,
            },
        }

        d = DEMOS.get(demo, {})

        st.markdown("---")
        eng      = st.number_input("Engagements totaux — ENG (TND)",
                                    min_value=0, max_value=50_000_000,
                                    value=d.get('eng', 100000), step=10000,
                                    format="%d")
        ca       = st.number_input("CA confié (TND)",
                                    min_value=0, max_value=100_000_000,
                                    value=d.get('ca', 80000), step=5000,
                                    format="%d")
        imp      = st.slider("Impayés — IMP (score 0-3)",
                              0.0, 3.0, float(d.get('imp', 0.0)), 0.1)
        gel      = st.slider("Gel (score 0-2)",
                              0.0, 2.0, float(d.get('gel', 0.0)), 0.1)
        pr       = st.number_input("Provisions brutes — PR (TND)",
                                    min_value=0, max_value=10_000_000,
                                    value=d.get('pr', 0), step=1000,
                                    format="%d")
        agios    = st.toggle("AGIOS actifs (frais sur compte débiteur)", 
                              value=bool(d.get('agios', 0)))
        sector   = st.selectbox("Secteur d'activité",
                                 options=list(SECTOR_LABELS.keys()),
                                 format_func=lambda x: SECTOR_LABELS[x],
                                 index=d.get('sector', 1) - 1)

        st.markdown("---")
        st.markdown('<div class="section-header">Contexte macroéconomique</div>',
                    unsafe_allow_html=True)
        pib_val  = st.slider("Croissance PIB (%)", -10.0, 8.0, 1.6, 0.1)
        infl_val = st.slider("Inflation (%)", 2.0, 15.0, 7.2, 0.1)

    with col_result:
        result = compute_pd(
            eng=eng, ca_confie=ca, imp=imp, gel=gel,
            pr_raw=pr, agios_flag=int(agios),
            sector_code=sector, pib=pib_val, inflation=infl_val,
        )
        pd_val = result['pd']

        st.markdown('<div class="section-header">Résultat du scoring</div>',
                    unsafe_allow_html=True)

        # Gauge principale
        st.plotly_chart(make_gauge(pd_val), use_container_width=True,
                        config={'displayModeBar': False})

        # Badge de risque
        st.markdown(
            f"<div style='text-align:center; margin: 0.5rem 0 1.5rem;'>"
            f"<span class='risk-badge {result['css_class']}'>"
            f"RISQUE {result['category']}</span></div>",
            unsafe_allow_html=True,
        )

        # Métriques
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            delta_vs_portfolio = (pd_val - PORTFOLIO_MEAN_PD) * 100
            st.markdown(f"""
            <div class="metric-card {'danger' if delta_vs_portfolio > 5 else
                                     'warn' if delta_vs_portfolio > 0 else 'success'}">
                <div class="metric-label">PD calculée</div>
                <div class="metric-value">{pd_val*100:.1f}%</div>
                <div class="metric-sub">{delta_vs_portfolio:+.1f}pp vs portefeuille</div>
            </div>""", unsafe_allow_html=True)
        with mc2:
            el_k = result['el'] / 1000
            st.markdown(f"""
            <div class="metric-card orange">
                <div class="metric-label">Perte Attendue</div>
                <div class="metric-value">{el_k:.0f}k</div>
                <div class="metric-sub">TND · PD × LGD × ENG</div>
            </div>""", unsafe_allow_html=True)
        with mc3:
            lgd_pct = 45
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">LGD appliqué</div>
                <div class="metric-value">{lgd_pct}%</div>
                <div class="metric-sub">Bâle II standard</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphique comparatif
        st.markdown('<div class="section-header">Positionnement relatif</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(make_comparison_bar(pd_val), use_container_width=True,
                        config={'displayModeBar': False})

        # Facteurs de risque
        st.markdown('<div class="section-header">Facteurs de risque actifs</div>',
                    unsafe_allow_html=True)

        factors = []
        if agios:
            factors.append(("⚠", "AGIOS actifs",
                             "+4.0pp sur PD moyenne (effet marginal Probit)"))
        if imp > 0.5:
            factors.append(("⚠", f"Impayés élevés (IMP={imp:.1f})",
                             "+2.3pp sur PD moyenne"))
        if gel > 0.3:
            factors.append(("⚠", f"Gel actif (GEL={gel:.1f})",
                             "+0.5pp sur PD moyenne"))
        if pr > 10000:
            factors.append(("⚠", f"Provisions {pr/1000:.0f}k TND",
                             "+1.8pp sur PD moyenne"))
        if sector == 2:
            factors.append(("ℹ", "Secteur AUTRES (SECT_2)",
                             "+5.4pp sur Agriculture"))
        if sector == 7:
            factors.append(("✓", "Hôtellerie & tourisme (SECT_7)",
                             "−5.7pp sur Agriculture"))
        if ca < eng * 0.3:
            factors.append(("⚠", "CA confié faible vs engagements",
                             "Signal de dépendance"))
        if not factors:
            factors.append(("✓", "Aucun facteur de risque majeur détecté", ""))

        for icon, title, detail in factors:
            color = "#ff6b35" if icon == "⚠" else ("#00ff88" if icon == "✓" else "#00d4ff")
            st.markdown(f"""
            <div style='display:flex; gap:0.75rem; align-items:flex-start;
                        padding:0.6rem 0; border-bottom:1px solid #1e3a5f;'>
                <span style='color:{color}; font-size:1rem;'>{icon}</span>
                <div>
                    <div style='font-size:0.85rem; color:#e2e8f0;'>{title}</div>
                    <div style='font-size:0.75rem; color:#64748b;'>{detail}</div>
                </div>
            </div>""", unsafe_allow_html=True)
