"""pages/page_stress.py — Page 2 : Stress Simulator"""
# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from model_utils import (project_npl, compute_stress_summary,
                          NPL_2023, PORTFOLIO_MEAN_PD,
                          PORTFOLIO_EAD, LGD)

YEARS    = [2024, 2025, 2026]
COLORS   = {'Baseline': '#00ff88', 'Défavorable': '#ffb020', 'Sévère': '#ff3b5c'}
SCENARIO_PRESETS = {
    'Baseline':    {'chom': [15.1, 15.3, 15.2], 'infl': [7.2,  6.5,  6.0]},
    'Défavorable': {'chom': [15.3, 17.0, 17.5], 'infl': [9.0,  8.5,  8.0]},
    'Sévère':      {'chom': [15.3, 19.5, 18.5], 'infl': [11.0, 9.5,  8.0]},
}


def make_npl_chart(all_scenarios, hist_npl):
    fig = go.Figure()

    # Historique
    hist_years = list(range(2016, 2024))
    fig.add_trace(go.Scatter(
        x=hist_years, y=hist_npl,
        mode='lines+markers',
        name='Historique',
        line=dict(color='#64748b', width=2),
        marker=dict(size=5),
    ))

    for scen_name, projs in all_scenarios.items():
        c     = COLORS[scen_name]
        xs    = [2023] + YEARS
        ys    = [NPL_2023] + [p['npl'] for p in projs]
        lo    = [NPL_2023] + [p['lo']  for p in projs]
        hi    = [NPL_2023] + [p['hi']  for p in projs]

        fig.add_trace(go.Scatter(
            x=xs + xs[::-1], y=hi + lo[::-1],
            fill='toself', fillcolor=c + '18',
            line=dict(width=0), showlegend=False, hoverinfo='skip',
        ))
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines+markers',
            name=scen_name,
            line=dict(color=c, width=2.5,
                      dash='dot' if scen_name != 'Baseline' else 'solid'),
            marker=dict(size=7),
        ))

    fig.add_vline(x=2023.5, line_dash='dash',
                  line_color='#334155', line_width=1)
    fig.add_hline(y=NPL_2023, line_dash='dot',
                  line_color='#334155', line_width=1,
                  annotation_text=f"NPL 2023 : {NPL_2023:.1f}%",
                  annotation_font={'color': '#64748b', 'size': 10})

    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        legend=dict(bgcolor='#111827', bordercolor='#1e3a5f',
                    borderwidth=1, font={'family': 'IBM Plex Mono', 'size': 10}),
        xaxis=dict(showgrid=False,
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        yaxis=dict(showgrid=True, gridcolor='#1e3a5f',
                   ticksuffix='%',
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        hovermode='x unified',
    )
    return fig


def make_buffer_chart(summaries):
    names   = list(summaries.keys())
    buffers = [summaries[n]['buffer'] for n in names]
    cols    = [COLORS[n] for n in names]

    fig = go.Figure(go.Bar(
        x=names, y=buffers,
        marker_color=cols, marker_line_width=0,
        text=[f"{v:.0f} M" for v in buffers],
        textposition='outside',
        textfont={'family': 'IBM Plex Mono', 'size': 12, 'color': '#e2e8f0'},
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        yaxis=dict(showgrid=True, gridcolor='#1e3a5f',
                   ticksuffix=' M',
                   tickfont={'color': '#64748b', 'family': 'IBM Plex Mono'}),
        xaxis=dict(tickfont={'color': '#e2e8f0',
                              'family': 'IBM Plex Mono', 'size': 11}),
        showlegend=False,
    )
    return fig


def render():
    st.markdown('<div class="page-title">02 · Stress Simulator</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Modèle macro AR(1) + Chômage + Inflation · '
                'Glissez les curseurs et observez l\'impact en temps réel</div>',
                unsafe_allow_html=True)

    # ── Tabs : scénarios ──────────────────────────────────────────────────
    tab_b, tab_d, tab_s, tab_custom = st.tabs([
        "📗 Baseline", "📙 Défavorable", "📕 Sévère", "🎛 Scénario personnalisé"
    ])

    scenario_inputs = {}

    with tab_b:
        st.markdown("**FMI WEO avril 2025 — reprise graduelle**")
        p = SCENARIO_PRESETS['Baseline']
        c1, c2 = st.columns(2)
        with c1:
            b_chom = [st.slider(f"Chômage {y} (%)", 10.0, 25.0, p['chom'][i], 0.1,
                                key=f"b_chom_{i}")
                      for i, y in enumerate(YEARS)]
        with c2:
            b_infl = [st.slider(f"Inflation {y} (%)", 2.0, 20.0, p['infl'][i], 0.1,
                                key=f"b_infl_{i}")
                      for i, y in enumerate(YEARS)]
        scenario_inputs['Baseline'] = {'chom': b_chom, 'infl': b_infl}

    with tab_d:
        st.markdown("**Récession modérée — instabilité politique, sécheresse**")
        p = SCENARIO_PRESETS['Défavorable']
        c1, c2 = st.columns(2)
        with c1:
            d_chom = [st.slider(f"Chômage {y} (%)", 10.0, 25.0, p['chom'][i], 0.1,
                                key=f"d_chom_{i}")
                      for i, y in enumerate(YEARS)]
        with c2:
            d_infl = [st.slider(f"Inflation {y} (%)", 2.0, 20.0, p['infl'][i], 0.1,
                                key=f"d_infl_{i}")
                      for i, y in enumerate(YEARS)]
        scenario_inputs['Défavorable'] = {'chom': d_chom, 'infl': d_infl}

    with tab_s:
        st.markdown("**Choc sévère — magnitude COVID-2020 (PIB = −9%)**")
        p = SCENARIO_PRESETS['Sévère']
        c1, c2 = st.columns(2)
        with c1:
            s_chom = [st.slider(f"Chômage {y} (%)", 10.0, 25.0, p['chom'][i], 0.1,
                                key=f"s_chom_{i}")
                      for i, y in enumerate(YEARS)]
        with c2:
            s_infl = [st.slider(f"Inflation {y} (%)", 2.0, 20.0, p['infl'][i], 0.1,
                                key=f"s_infl_{i}")
                      for i, y in enumerate(YEARS)]
        scenario_inputs['Sévère'] = {'chom': s_chom, 'infl': s_infl}

    with tab_custom:
        st.markdown("**Construisez votre propre scénario**")
        st.info("Utilisez les mêmes contrôles — modifiez librement les hypothèses.")
        p = SCENARIO_PRESETS['Défavorable']
        c1, c2 = st.columns(2)
        with c1:
            cu_chom = [st.slider(f"Chômage {y} (%)", 10.0, 25.0, p['chom'][i], 0.1,
                                  key=f"cu_chom_{i}")
                       for i, y in enumerate(YEARS)]
        with c2:
            cu_infl = [st.slider(f"Inflation {y} (%)", 2.0, 20.0, p['infl'][i], 0.1,
                                  key=f"cu_infl_{i}")
                       for i, y in enumerate(YEARS)]
        # Override all scenarios with custom for this tab view
        # (shown in summary below)

    # ── Calculs en temps réel ─────────────────────────────────────────────
    all_projs = {
        name: project_npl(inp['chom'], inp['infl'])
        for name, inp in scenario_inputs.items()
    }
    all_summaries = {
        name: compute_stress_summary(projs)
        for name, projs in all_projs.items()
    }

    # ── Résultats en temps réel ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Résultats en temps réel</div>',
                unsafe_allow_html=True)

    # KPIs par scénario
    cols = st.columns(3)
    for i, (scen_name, summ) in enumerate(all_summaries.items()):
        c = COLORS[scen_name]
        card_type = ('success' if scen_name == 'Baseline' else
                     'warn' if scen_name == 'Défavorable' else 'danger')
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card {card_type}" style="border-left-color:{c}">
                <div class="metric-label" style="color:{c}">{scen_name}</div>
                <div style="margin: 0.5rem 0;">
                    <div style="display:flex; justify-content:space-between;
                                font-size:0.82rem; padding:0.3rem 0;
                                border-bottom:1px solid #1e3a5f;">
                        <span style="color:#64748b; font-family:'IBM Plex Mono'">NPL max</span>
                        <span style="color:#e2e8f0; font-family:'IBM Plex Mono';
                                     font-weight:600">{summ['max_npl']:.1f}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                font-size:0.82rem; padding:0.3rem 0;
                                border-bottom:1px solid #1e3a5f;">
                        <span style="color:#64748b; font-family:'IBM Plex Mono'">ΔNPL</span>
                        <span style="color:{c}; font-family:'IBM Plex Mono';
                                     font-weight:600">{summ['delta_npl']:+.1f} pp</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                font-size:0.82rem; padding:0.3rem 0;
                                border-bottom:1px solid #1e3a5f;">
                        <span style="color:#64748b; font-family:'IBM Plex Mono'">PD stressée</span>
                        <span style="color:#e2e8f0; font-family:'IBM Plex Mono';
                                     font-weight:600">{summ['pd_stress']*100:.2f}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                font-size:0.82rem; padding:0.3rem 0;
                                border-bottom:1px solid #1e3a5f;">
                        <span style="color:#64748b; font-family:'IBM Plex Mono'">EL (M TND)</span>
                        <span style="color:#e2e8f0; font-family:'IBM Plex Mono';
                                     font-weight:600">{summ['el_stress']:.0f} M</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                font-size:0.82rem; padding:0.3rem 0;">
                        <span style="color:#64748b; font-family:'IBM Plex Mono'">Coussin Pilier 2</span>
                        <span style="color:{c}; font-family:'IBM Plex Mono';
                                     font-weight:700; font-size:1rem">
                            {summ['buffer']:.0f} M
                        </span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col_npl, col_buf = st.columns([3, 2], gap="large")

    with col_npl:
        st.markdown('<div class="section-header">Projection NPL 2024-2026 '
                    '(IC 90%)</div>', unsafe_allow_html=True)
        hist_npl = [15.6, 13.9, 13.4, 13.1, 13.1, 13.5, 14.5, 15.7]
        st.plotly_chart(make_npl_chart(all_projs, hist_npl),
                        use_container_width=True,
                        config={'displayModeBar': False})

    with col_buf:
        st.markdown('<div class="section-header">Coussin de capital Pilier 2 '
                    '(M TND)</div>', unsafe_allow_html=True)
        st.plotly_chart(make_buffer_chart(all_summaries),
                        use_container_width=True,
                        config={'displayModeBar': False})

    # Interprétation dynamique
    severe = all_summaries.get('Sévère', {})
    if severe:
        npl_s  = severe['max_npl']
        buf_s  = severe['buffer']
        delta_s= severe['delta_npl']
        msg_color = "#ff3b5c" if delta_s > 4 else "#ffb020"
        st.markdown(f"""
        <div style='background:#1a0a0e; border:1px solid #ff3b5c30;
                    border-radius:12px; padding:1.25rem 1.5rem; margin-top:1rem;'>
            <div style='font-family:"IBM Plex Mono"; font-size:0.7rem;
                        letter-spacing:0.2em; color:#ff3b5c; margin-bottom:0.75rem;'>
                INTERPRÉTATION AUTOMATIQUE — SCÉNARIO SÉVÈRE
            </div>
            <div style='font-size:0.88rem; color:#e2e8f0; line-height:1.7;'>
                Sous le scénario sévère, le NPL atteint
                <span style='color:{msg_color}; font-weight:600;
                              font-family:"IBM Plex Mono"'>{npl_s:.1f}%</span>
                en 2026 (ΔNPL = <span style='color:{msg_color};
                font-family:"IBM Plex Mono"'>{delta_s:+.1f} pp</span>
                vs 2023). La STB devrait constituer un coussin additionnel de
                <span style='color:#ff3b5c; font-weight:700;
                              font-family:"IBM Plex Mono"'>{buf_s:.0f} M TND</span>
                au titre du Pilier 2 / ICAAP pour couvrir ce risque.
                Ce scénario est calibré sur le choc COVID-2020 (PIB = −9%)
                et représente la magnitude de stress maximale observée
                en Tunisie sur la période 1985-2024.
            </div>
        </div>""", unsafe_allow_html=True)
