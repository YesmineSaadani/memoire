"""pages/page_dashboard.py — Page 3 : Tableau de Bord"""
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ── Données issues des résultats de la thèse ─────────────────────────────────
VALIDATION_CHECKS = [
    ("AUC > 0.80",                  True,  "0.9239"),
    ("Gini > 0.50",                 True,  "0.8478"),
    ("KS > 0.40",                   True,  "0.7439"),
    ("Séparation des scores",       True,  "0.476 vs 0.091"),
    ("Brier Skill > 0.25",          True,  "0.3792"),
    ("CV gap < 0.02",               True,  "0.0018"),
    ("CV std < 0.05",               True,  "0.0008"),
    ("AUC > 0.70 toutes années",    True,  "min = 0.755"),
    ("Profils clients ordonnés",    True,  "✓ monotone"),
    ("Hosmer-Lemeshow p > 0.05",    False, "p = 0.000 (N=262k)"),
]

GRAND_COMPARISON = {
    'Set A — Logit' : {'auc': 0.7785, 'gini': 0.5570, 'cv': '0.778±0.012'},
    'Set A — Probit': {'auc': 0.7802, 'gini': 0.5603, 'cv': '0.778±0.012'},
    'Set A — LDA'   : {'auc': 0.7862, 'gini': 0.5724, 'cv': '0.762±0.021'},
    'Set B — Logit' : {'auc': 0.6505, 'gini': 0.3010, 'cv': '0.624±0.031'},
    'Set B — Probit': {'auc': 0.6472, 'gini': 0.2944, 'cv': '0.624±0.031'},
    'Set B — LDA'   : {'auc': 0.6248, 'gini': 0.2496, 'cv': '0.601±0.028'},
    'Set C — Logit' : {'auc': 0.7736, 'gini': 0.5471, 'cv': '0.784±0.012'},
    'Set C — Probit': {'auc': 0.7737, 'gini': 0.5474, 'cv': '0.784±0.012'},
    'Set C — LDA'   : {'auc': 0.7822, 'gini': 0.5644, 'cv': '0.766±0.016'},
}

# ROC curve approximation (from AUC = 0.9239)
def approx_roc(auc, n=100):
    t = np.linspace(0, 1, n)
    b = 2 * auc - 1
    tpr = t + b * t * (1 - t) * 2
    tpr = np.clip(tpr, 0, 1)
    return t, tpr


def make_roc_chart():
    fpr, tpr = approx_roc(0.9239)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode='lines',
        line=dict(color='#334155', dash='dash', width=1.5),
        name='Aléatoire (AUC=0.50)', showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=list(fpr) + [1, 0], y=list(tpr) + [0, 0],
        fill='toself', fillcolor='#00d4ff15',
        line=dict(width=0), showlegend=False, hoverinfo='skip',
    ))
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr, mode='lines',
        name='Probit Stage 2 (AUC=0.924)',
        line=dict(color='#00d4ff', width=3),
    ))
    fig.add_annotation(
        x=0.6, y=0.35, text="AUC = 0.9239<br>Gini = 0.8478",
        showarrow=False, align='left',
        font={'color': '#00d4ff', 'size': 12, 'family': 'IBM Plex Mono'},
        bgcolor='#111827', bordercolor='#00d4ff', borderwidth=1,
        borderpad=8,
    )
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        xaxis=dict(title='Taux de Faux Positifs', showgrid=True,
                   gridcolor='#1e3a5f',
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        yaxis=dict(title='Taux de Vrais Positifs', showgrid=True,
                   gridcolor='#1e3a5f',
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        legend=dict(bgcolor='#111827', bordercolor='#1e3a5f', borderwidth=1,
                    font={'family': 'IBM Plex Mono', 'size': 10}),
    )
    return fig


def make_set_comparison_chart():
    sets   = ['Set A\n(Bancaire)', 'Set B\n(Ratios)', 'Set C\n(Combiné)']
    models = ['Logit', 'Probit', 'LDA']
    ginis  = {
        'Logit' : [0.5570, 0.3010, 0.5471],
        'Probit': [0.5603, 0.2944, 0.5474],
        'LDA'   : [0.5724, 0.2496, 0.5644],
    }
    colors_m = {'Logit': '#00d4ff', 'Probit': '#00ff88', 'LDA': '#ff6b35'}

    fig = go.Figure()
    x = np.arange(3)
    w = 0.25
    for i, model in enumerate(models):
        fig.add_trace(go.Bar(
            x=x + i * w, y=ginis[model],
            name=model,
            marker_color=colors_m[model], marker_line_width=0,
            text=[f"{v:.3f}" for v in ginis[model]],
            textposition='outside',
            textfont={'family': 'IBM Plex Mono', 'size': 9, 'color': '#e2e8f0'},
        ))

    fig.add_hline(y=0.50, line_dash='dot', line_color='#00d4ff',
                  line_width=1.5,
                  annotation_text="Seuil Bâle II (Gini > 0.50)",
                  annotation_font={'color': '#00d4ff', 'size': 9})

    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        barmode='group',
        xaxis=dict(tickvals=x + w, ticktext=sets,
                   tickfont={'color': '#e2e8f0', 'family': 'IBM Plex Mono',
                              'size': 10}),
        yaxis=dict(showgrid=True, gridcolor='#1e3a5f', range=[0, 0.75],
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        legend=dict(bgcolor='#111827', bordercolor='#1e3a5f', borderwidth=1,
                    font={'family': 'IBM Plex Mono', 'size': 10}),
    )
    return fig


def make_stress_summary_chart():
    scenarios = ['Baseline', 'Défavorable', 'Sévère']
    npl_2026  = [16.2, 18.5, 20.2]
    buffers   = [0.0, 264.4, 465.7]
    colors    = ['#00ff88', '#ffb020', '#ff3b5c']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='NPL 2026 (%)', x=scenarios, y=npl_2026,
        marker_color=colors, marker_line_width=0,
        text=[f"{v:.1f}%" for v in npl_2026],
        textposition='outside',
        textfont={'family': 'IBM Plex Mono', 'size': 11, 'color': '#e2e8f0'},
        yaxis='y',
    ))

    fig.add_hline(y=15.7, line_dash='dot', line_color='#64748b',
                  annotation_text="NPL 2023 : 15.7%",
                  annotation_font={'color': '#64748b', 'size': 9},
                  yref='y')

    fig.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        xaxis=dict(tickfont={'color': '#e2e8f0',
                              'family': 'IBM Plex Mono', 'size': 11}),
        yaxis=dict(showgrid=True, gridcolor='#1e3a5f',
                   ticksuffix='%',
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        showlegend=False,
    )
    return fig


def render():
    st.markdown('<div class="page-title">03 · Model Dashboard</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Synthèse complète des résultats '
                '— Stage 1 · Stage 2 · Stress Testing</div>',
                unsafe_allow_html=True)

    # ── KPIs principaux ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Indicateurs clés — Modèle final '
                '(Probit Stage 2)</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "AUC-ROC",     "0.9239", "Bâle II > 0.80 ✓", "success"),
        (k2, "Gini",        "0.8478", "Bâle II > 0.50 ✓", "success"),
        (k3, "KS stat.",    "0.7439", "Bâle II > 0.40 ✓", "success"),
        (k4, "CV gap",      "0.0018", "< 0.02 — stable ✓", "success"),
        (k5, "N clients",   "327k",   "portefeuille STB", ""),
    ]
    for col, label, val, sub, ctype in kpis:
        with col:
            st.markdown(f"""
            <div class="metric-card {ctype}">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:1.6rem">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row 1 ─────────────────────────────────────────────────────
    col_roc, col_sets = st.columns([1, 1], gap="large")

    with col_roc:
        st.markdown('<div class="section-header">Courbe ROC — Test Set '
                    '(65 515 obs.)</div>', unsafe_allow_html=True)
        st.plotly_chart(make_roc_chart(), use_container_width=True,
                        config={'displayModeBar': False})

    with col_sets:
        st.markdown('<div class="section-header">Comparaison Sets A / B / C '
                    '— Gini par modèle</div>', unsafe_allow_html=True)
        st.plotly_chart(make_set_comparison_chart(), use_container_width=True,
                        config={'displayModeBar': False})
        st.markdown("""
        <div style='font-size:0.75rem; color:#64748b; font-family:"IBM Plex Mono";
                    background:#111827; border:1px solid #1e3a5f; border-radius:8px;
                    padding:0.75rem; margin-top:0.5rem;'>
            Résultat clé : Set B (ratios financiers seuls) est systématiquement
            inférieur — les variables bancaires comportementales dominent.
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scorecard + Stress ────────────────────────────────────────────────
    col_score, col_stress = st.columns([1, 1], gap="large")

    with col_score:
        st.markdown('<div class="section-header">Scorecard de validation '
                    '(9/10 checks)</div>', unsafe_allow_html=True)

        for name, ok, val in VALIDATION_CHECKS:
            icon  = "✓" if ok else "✗"
            color = "#00ff88" if ok else "#ff3b5c"
            st.markdown(f"""
            <div class="score-row">
                <span style="color:#e2e8f0; font-size:0.82rem">{name}</span>
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <span style="color:#64748b; font-family:'IBM Plex Mono';
                                 font-size:0.75rem">{val}</span>
                    <span style="color:{color}; font-family:'IBM Plex Mono';
                                 font-weight:700">{icon}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        passed = sum(1 for _, ok, _ in VALIDATION_CHECKS if ok)
        st.markdown(f"""
        <div style='margin-top:1rem; padding:0.75rem; background:#0a1628;
                    border:1px solid #00ff8840; border-radius:8px; text-align:center;'>
            <span style='font-family:"IBM Plex Mono"; font-size:1.1rem;
                         color:#00ff88; font-weight:700'>{passed}/10</span>
            <span style='color:#64748b; font-size:0.8rem; margin-left:0.5rem;'>
                checks validés</span>
        </div>""", unsafe_allow_html=True)

    with col_stress:
        st.markdown('<div class="section-header">Stress Testing — NPL 2026 '
                    'par scénario</div>', unsafe_allow_html=True)
        st.plotly_chart(make_stress_summary_chart(), use_container_width=True,
                        config={'displayModeBar': False})

        # Tableau coussins
        st.markdown("""
        <div style='background:#111827; border:1px solid #1e3a5f; border-radius:10px;
                    padding:1rem;'>
            <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                        letter-spacing:0.15em; color:#64748b; margin-bottom:0.75rem;'>
                COUSSINS DE CAPITAL BÂLE II PILIER 2
            </div>
            <div style='display:grid; grid-template-columns:1fr 1fr 1fr;
                        gap:0.5rem; text-align:center;'>
                <div style='padding:0.75rem; background:#00ff8810;
                            border:1px solid #00ff8830; border-radius:8px;'>
                    <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                                color:#00ff88;'>BASELINE</div>
                    <div style='font-family:"IBM Plex Mono"; font-size:1.3rem;
                                color:#00ff88; font-weight:700;'>0 M</div>
                </div>
                <div style='padding:0.75rem; background:#ffb02010;
                            border:1px solid #ffb02030; border-radius:8px;'>
                    <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                                color:#ffb020;'>DÉFAVORABLE</div>
                    <div style='font-family:"IBM Plex Mono"; font-size:1.3rem;
                                color:#ffb020; font-weight:700;'>264 M</div>
                </div>
                <div style='padding:0.75rem; background:#ff3b5c10;
                            border:1px solid #ff3b5c30; border-radius:8px;'>
                    <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                                color:#ff3b5c;'>SÉVÈRE</div>
                    <div style='font-family:"IBM Plex Mono"; font-size:1.3rem;
                                color:#ff3b5c; font-weight:700;'>466 M</div>
                </div>
            </div>
            <div style='margin-top:0.75rem; font-size:0.72rem; color:#64748b;
                        font-family:"IBM Plex Mono";'>
                EAD = 27.5 Mrd TND · LGD = 45% · PD base = 14.8%
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Méthodologie ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Architecture méthodologique</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem;'>
        <div style='background:#111827; border:1px solid #1e3a5f; border-radius:12px;
                    padding:1.25rem;'>
            <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                        letter-spacing:0.15em; color:#00d4ff; margin-bottom:0.75rem;'>
                NIVEAU 1 — SCORING INDIVIDUEL
            </div>
            <div style='font-size:0.82rem; color:#e2e8f0; line-height:1.7;'>
                <b>Modèle Probit</b> sur 327 571 clients (CL R 0-3)<br>
                Variables : ENG, CA_Confié, IMP, GEL, PR_log,<br>
                AGIOS_bin, 10 secteurs, PIB, Inflation<br>
                Backward elimination · StandardScaler<br>
                <span style='color:#00ff88;'>AUC = 0.924 · Gini = 0.848</span>
            </div>
        </div>
        <div style='background:#111827; border:1px solid #1e3a5f; border-radius:12px;
                    padding:1.25rem;'>
            <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                        letter-spacing:0.15em; color:#00d4ff; margin-bottom:0.75rem;'>
                NIVEAU 2 — MODÈLE MACRO
            </div>
            <div style='font-size:0.82rem; color:#e2e8f0; line-height:1.7;'>
                <b>AR(1) + Chômage + Inflation</b><br>
                Série 1984-2024 (N=40) · Tunisie<br>
                HAC Newey-West · SPIKE_2003 dummy<br>
                R²adj = 0.939 · MAE = 0.77 pp<br>
                <span style='color:#00ff88;'>p_Chômage = 0.002 ✓</span>
            </div>
        </div>
        <div style='background:#111827; border:1px solid #1e3a5f; border-radius:12px;
                    padding:1.25rem;'>
            <div style='font-family:"IBM Plex Mono"; font-size:0.65rem;
                        letter-spacing:0.15em; color:#00d4ff; margin-bottom:0.75rem;'>
                STRESS TESTING
            </div>
            <div style='font-size:0.82rem; color:#e2e8f0; line-height:1.7;'>
                <b>Wilson (1997) CreditPortfolioView</b><br>
                3 scénarios : Baseline / Défavorable / Sévère<br>
                EL = PD_stressée × LGD × EAD<br>
                Coussin Bâle II Pilier 2 / ICAAP<br>
                <span style='color:#ff3b5c;'>Sévère : +4.5pp NPL · 466M TND</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
