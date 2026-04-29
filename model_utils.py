"""
model_utils.py
==============
Coefficients du modèle Probit Stage 2 et du modèle macro AR(1).
Ces valeurs viennent directement des résultats de votre pipeline.
"""

import numpy as np
from scipy.stats import norm

# ══════════════════════════════════════════════════════════════════════════════
#  NIVEAU 1 — PROBIT Stage 2
#  Coefficients HAC du modèle retenu (résultats document 7)
# ══════════════════════════════════════════════════════════════════════════════

PROBIT_INTERCEPT = -1.4800

PROBIT_COEFS = {
    'ENG'       : 0.0080,
    'CA_Confie' : -0.1156,
    'IMP'       : 0.1675,
    'GEL'       : 0.0352,
    'PR_log'    : 0.1298,
    'AGIOS_bin' : 0.2916,
    'SECT_2'    : 0.3912,
    'SECT_3'    : 0.0079,
    'SECT_4'    : 0.0296,
    'SECT_5'    : 0.0210,
    'SECT_6'    : 0.0270,
    'SECT_7'    : -0.4144,
    'SECT_8'    : -0.1452,
    'SECT_9'    : 0.0300,
    'SECT_10'   : 0.0107,
    'SECT_11'   : 0.0291,
    'PIB'       : 0.1054,
    'Inflation' : -0.0894,
}

# Secteurs d'activité (codes ACTIVITE dans les données)
SECTOR_LABELS = {
    1:  "Agriculture (référence)",
    2:  "Industrie manufacturière",
    3:  "Construction & BTP",
    4:  "Commerce de gros",
    5:  "Commerce de détail",
    6:  "Transport & logistique",
    7:  "Hôtellerie & tourisme",
    8:  "Services financiers",
    9:  "Immobilier",
    10: "Services aux entreprises",
    11: "Autres services",
}

# Statistiques du portefeuille (pour contextualiser le score)
PORTFOLIO_MEAN_PD = 0.1484
PORTFOLIO_EAD     = 27_451_439_295
LGD               = 0.45
NPL_2023          = 15.7

# ── Fonction de scoring ───────────────────────────────────────────────────────
def compute_pd(eng, ca_confie, imp, gel, pr_raw, agios_flag,
               sector_code, pib=1.614, inflation=7.2):
    """
    Calcule la PD d'un client avec le modèle Probit Stage 2.

    Paramètres :
      eng         : Engagements totaux (TND)
      ca_confie   : Chiffre d'affaires confié (TND)
      imp         : Impayés (scalé, 0-3)
      gel         : Gel (scalé, 0-2)
      pr_raw      : Provisions brutes (TND) — on calcule log1p
      agios_flag  : 1 si AGIOS > 0, sinon 0
      sector_code : 1-11
      pib         : Croissance PIB (%, défaut = 2024 baseline)
      inflation   : Inflation (%, défaut = 2024 baseline)

    Retourne : dict avec PD, XB, catégorie de risque
    """
    pr_log = np.log1p(max(pr_raw, 0))

    # Construction du vecteur X (standardisé dans le pipeline — ici on
    # utilise les coefficients directement sur les valeurs standardisées.
    # IMPORTANT : Dans une vraie implémentation, il faudrait appliquer
    # le StandardScaler sauvegardé. Ici on applique les coefficients
    # directement — suffisant pour la démo.)

    # Normalisation approx basée sur les statistiques du portefeuille Stage 2
    # (μ et σ estimés à partir des données)
    MEANS = {
        'ENG': 83_800, 'CA_Confie': 45_000, 'IMP': 0.05,
        'GEL': 0.08, 'PR_log': 1.2, 'AGIOS_bin': 0.42,
        'PIB': 1.0, 'Inflation': 6.5,
    }
    STDS = {
        'ENG': 210_000, 'CA_Confie': 180_000, 'IMP': 0.22,
        'GEL': 0.27, 'PR_log': 2.1, 'AGIOS_bin': 0.49,
        'PIB': 5.8, 'Inflation': 2.1,
    }

    def scale(val, key):
        return (val - MEANS[key]) / STDS[key]

    xb = PROBIT_INTERCEPT
    xb += PROBIT_COEFS['ENG']       * scale(eng, 'ENG')
    xb += PROBIT_COEFS['CA_Confie'] * scale(ca_confie, 'CA_Confie')
    xb += PROBIT_COEFS['IMP']       * scale(imp, 'IMP')
    xb += PROBIT_COEFS['GEL']       * scale(gel, 'GEL')
    xb += PROBIT_COEFS['PR_log']    * scale(pr_log, 'PR_log')
    xb += PROBIT_COEFS['AGIOS_bin'] * scale(agios_flag, 'AGIOS_bin')
    xb += PROBIT_COEFS['PIB']       * scale(pib, 'PIB')
    xb += PROBIT_COEFS['Inflation'] * scale(inflation, 'Inflation')

    # Secteur (dummies, référence = secteur 1)
    if sector_code >= 2:
        key = f'SECT_{sector_code}'
        if key in PROBIT_COEFS:
            xb += PROBIT_COEFS[key]   # dummies déjà en 0/1, pas de scaling

    pd_val = float(norm.cdf(xb))
    pd_val = max(0.001, min(0.999, pd_val))

    if pd_val < 0.05:
        category, css_class = "FAIBLE", "risk-low"
    elif pd_val < 0.15:
        category, css_class = "MODÉRÉ", "risk-moderate"
    elif pd_val < 0.35:
        category, css_class = "ÉLEVÉ", "risk-high"
    else:
        category, css_class = "CRITIQUE", "risk-critical"

    return {
        'pd'       : pd_val,
        'xb'       : xb,
        'category' : category,
        'css_class': css_class,
        'el'       : pd_val * LGD * eng,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  NIVEAU 2 — MODÈLE MACRO AR(1)
#  Coefficients OLS du modèle MB v5 (résultats document 14)
# ══════════════════════════════════════════════════════════════════════════════

MACRO_COEFS = {
    'const'         : -0.4988,
    'logit_NPL_lag1':  0.9524,
    'Chomage_lag1'  :  0.0237,
    'Inflation'     :  0.0110,
    'COVID'         : -0.0603,
    'LEGACY'        :  0.0014,
    'SPIKE_2003'    :  0.1524,
}

# HAC standard errors (pour les IC)
MACRO_SE_HAC = {
    'const'         : 0.1524,
    'logit_NPL_lag1': 0.0880,
    'Chomage_lag1'  : 0.0077,
    'Inflation'     : 0.0065,
    'COVID'         : 0.0314,
    'LEGACY'        : 0.0445,
    'SPIKE_2003'    : 0.0356,
}

NPL_2023_LOGIT = np.log(0.157 / (1 - 0.157))   # = -1.6807

def logit_to_npl(x):
    return float(np.exp(x) / (1 + np.exp(x)) * 100)

def npl_to_logit(npl_pct):
    r = npl_pct / 100
    return float(np.log(r / (1 - r)))


def project_npl(chomage_path, inflation_path, years=3,
                logit_start=NPL_2023_LOGIT, z=1.645):
    """
    Projette le NPL sur `years` années via le modèle AR(1).

    chomage_path   : liste de valeurs de chômage (t-1) pour chaque année
    inflation_path : liste de valeurs d'inflation pour chaque année
    z              : quantile pour IC (1.645 = IC 90%)

    Retourne : liste de dicts {npl, lo, hi, logit}
    """
    results    = []
    logit_prev = logit_start

    for t in range(years):
        chom = chomage_path[t]
        infl = inflation_path[t]

        logit_pred = (MACRO_COEFS['const']
                      + MACRO_COEFS['logit_NPL_lag1'] * logit_prev
                      + MACRO_COEFS['Chomage_lag1']   * chom
                      + MACRO_COEFS['Inflation']      * infl
                      + MACRO_COEFS['COVID']          * 0
                      + MACRO_COEFS['LEGACY']         * 0
                      + MACRO_COEFS['SPIKE_2003']     * 0)

        # IC approx : propagation d'erreur sur le terme AR(1)
        # SE augmente avec le temps car les erreurs s'accumulent
        se_pred = MACRO_SE_HAC['const'] * (1 + t * 0.3)
        lo = logit_pred - z * se_pred
        hi = logit_pred + z * se_pred

        npl    = logit_to_npl(logit_pred)
        npl_lo = logit_to_npl(lo)
        npl_hi = logit_to_npl(hi)

        results.append({
            'year'  : 2024 + t,
            'npl'   : npl,
            'lo'    : npl_lo,
            'hi'    : npl_hi,
            'logit' : logit_pred,
            'delta' : npl - NPL_2023,
        })
        logit_prev = logit_pred

    return results


def compute_stress_summary(npl_projections,
                            pd_base=PORTFOLIO_MEAN_PD,
                            ead=PORTFOLIO_EAD,
                            lgd=LGD,
                            npl_ref=NPL_2023):
    """
    Calcule EL et coussin de capital à partir des projections NPL.
    Retourne le worst-case (année où EL est max).
    """
    max_npl   = max(p['npl'] for p in npl_projections)
    pd_stress = min(pd_base * (max_npl / npl_ref), 0.999)
    el_stress = pd_stress * lgd * ead
    el_base   = pd_base * lgd * ead
    buffer    = max(0.0, el_stress - el_base)

    return {
        'max_npl'   : max_npl,
        'pd_stress' : pd_stress,
        'el_stress' : el_stress / 1e6,
        'el_base'   : el_base / 1e6,
        'buffer'    : buffer / 1e6,
        'delta_npl' : max_npl - npl_ref,
    }
