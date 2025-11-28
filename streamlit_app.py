import streamlit as st
import requests
import pandas as pd

# ----------------------------------------------------
# CONFIG PAGE
# ----------------------------------------------------
st.set_page_config(
    page_title="PFOS – Prédiction d’Orientation",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# STYLE PERSONNALISÉ PFOS / EIME
# ----------------------------------------------------
PRIMARY_COLOR = "#004b7f"   # bleu PFOS
ACCENT_COLOR = "#f0a500"    # jaune / or
LIGHT_BG = "#f7f9fc"

st.markdown(
    f"""
    <style>
    .main {{
        background-color: {LIGHT_BG};
    }}
    .pfos-header {{
        background: linear-gradient(90deg, {PRIMARY_COLOR}, #0a99c2);
        padding: 1.4rem 1.8rem;
        border-radius: 0 0 1.5rem 1.5rem;
        color: white;
        margin-bottom: 1.2rem;
    }}
    .pfos-title {{
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }}
    .pfos-subtitle {{
        font-size: 0.95rem;
        opacity: 0.9;
    }}
    .pfos-badge {{
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background-color: white;
        color: {PRIMARY_COLOR};
        font-weight: 600;
        font-size: 0.8rem;
        margin-right: 0.4rem;
    }}
    .pfos-footer {{
        font-size: 0.75rem;
        color: #8c8c8c;
        text-align: right;
        margin-top: 1.5rem;
        border-top: 1px solid #e1e4eb;
        padding-top: 0.6rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pfos-header">
        <div class="pfos-title">PFOS – Assistant de Prédiction d’Orientation</div>
        <div class="pfos-subtitle">
            Module de démonstration connecté au modèle de scoring d’orientation (G0, G1, G2, G3, G4, EEP, UP).
            Cette interface est destinée au projet de fin de Bootcamp
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# PARAMÈTRES GLOBAUX
# ----------------------------------------------------
# URL de l’API FastAPI déployée
DEFAULT_API_URL = "https://apipredict.pfos.education/predict"

# Description fonctionnelle des catégories
CATEGORIES_DESCRIPTIONS = {
    "EEP": "Écoles d’État à prestige (concours nationaux, filières publiques très sélectives).",
    "G0": "Grandes écoles privées à très forte exigence académique et coût de scolarité élevé.",
    "G1": "Grandes écoles privées de bon niveau, sélectives et orientées employabilité internationale.",
    "G2": "Écoles privées solides, bon compromis coût / qualité / insertion.",
    "G3": "Écoles privées plus accessibles, profils davantage orientés vers le territoire local.",
    "G4": "Formations locales, offres alternatives ou parcours moins structurés.",
    "UP": "Université(s) publique(s), filières longues à coût réduit mais très massifiées.",
}

# ----------------------------------------------------
# SIDEBAR : CONFIG GÉNÉRALE
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### Paramètres de connexion")
    api_url = st.text_input("URL de l’API PFOS", value="https://apipredict.pfos.education/predict")

    st.caption(
        "Cette interface appelle la première version de l’API de scoring PFOS. "
        "Le modèle ne contrôle pas encore correctement les mauvaises valeurs "
        "(collège ou ville inconnus, codes RIASEC non entraînés, etc.). "
        "Les prédictions doivent donc être interprétées avec prudence."
    )

    st.markdown("---")
    st.markdown("### Rappel des catégories")
    for code, desc in CATEGORIES_DESCRIPTIONS.items():
        st.markdown(f"**{code}** – {desc}")

# ----------------------------------------------------
# OPTIONS DE SAISIE (LISTES SIMPLIFIÉES + MANUEL)
# ----------------------------------------------------
st.markdown("### Saisie du profil élève")

col_left, col_right = st.columns([1.2, 1])

with col_left:
    # Exemples à adapter selon ta base
    colleges_options = [
        "Collège Diderot",
        "Lycée Général Leclerc",
        "Collège Vogt",
        "Autre (saisie manuelle)",
    ]
    villes_options = [
        "Yaoundé",
        "Douala",
        "Bafoussam",
        "Garoua",
        "Autre (saisie manuelle)",
    ]
    series_options = [
        "C", "D", "A4", "A1", "TI", "G2", "Autre (saisie manuelle)",
    ]
    souhait_options = [
        "Mobilité internationale",
        "Entrepreneuriat",
        "Santé",
        "Informatique / Digital",
        "Commerce / Gestion",
        "Autre (saisie manuelle)",
    ]
    riasec_options = [
        "R-I-A",
        "S-E-C",
        "I-R-A",
        "A-S-E",
        "C-E-S",
        "Code personnalisé",
    ]

    college_choice = st.selectbox("Collège / Lycée d’origine", colleges_options)
    ville_choice = st.selectbox("Ville", villes_options)
    serie_choice = st.selectbox("Série du Bac / Filière", series_options)
    souhait_choice = st.selectbox("Souhait principal d’orientation", souhait_options)
    riasec_choice = st.selectbox("Code RIASEC dominant", riasec_options)

    # Saisie libre si "Autre"
    college_manual = ""
    ville_manual = ""
    serie_manual = ""
    souhait_manual = ""
    riasec_manual = ""

    if "Autre" in college_choice:
        college_manual = st.text_input("Collège (saisie manuelle)")
    if "Autre" in ville_choice:
        ville_manual = st.text_input("Ville (saisie manuelle)")
    if "Autre" in serie_choice:
        serie_manual = st.text_input("Série (saisie manuelle)")
    if "Autre" in souhait_choice:
        souhait_manual = st.text_input("Souhait principal (saisie manuelle)")
    if "Code personnalisé" in riasec_choice:
        riasec_manual = st.text_input("Code RIASEC (ex : R-I-A)")

    # Valeurs finales envoyées à l’API
    college_final = college_manual if college_manual else college_choice
    ville_final = ville_manual if ville_manual else ville_choice
    serie_final = serie_manual if serie_manual else serie_choice
    souhait_final = souhait_manual if souhait_manual else souhait_choice
    riasec_final = riasec_manual if riasec_manual else riasec_choice

with col_right:
    st.info(
        "Cette interface est une vitrine du moteur d’orientation PFOS.\n\n"
        "- Les données sont envoyées vers l’API PFOS (FastAPI).\n"
        "- L’API renvoie :\n"
        "    - une classe prédite (EEP, G0, G1, etc.).\n"
        "    - les probabilités par classe.\n"
        "    - un score G0 (probabilité d’intégrer une école G0).\n"
        "    - une phrase d’interprétation du score G0."
    )

# ----------------------------------------------------
# BOUTON D’APPEL API
# ----------------------------------------------------
st.markdown("---")
launch = st.button("Lancer la prédiction", type="primary")

result = None
error_msg = None

if launch:
    if not api_url:
        st.error("Merci de renseigner l’URL de l’API PFOS dans le panneau de gauche.")
    else:
        payload = {
            "college": college_final,
            "ville": ville_final,
            "serie": serie_final,
            "souhait": souhait_final,
            "code_riasec": riasec_final,
        }

        try:
            with st.spinner("Appel de l’API PFOS en cours..."):
                resp = requests.post(api_url, json=payload, timeout=15)

            if resp.status_code == 200:
                result = resp.json()
            else:
                error_msg = f"Erreur API {resp.status_code} : {resp.text}"
        except Exception as e:
            error_msg = f"Impossible de joindre l’API ({e})"

# ----------------------------------------------------
# AFFICHAGE DES RÉSULTATS
# ----------------------------------------------------
if error_msg:
    st.error(error_msg)

if result:
    st.markdown("## Résultats de la prédiction")

    col_a, col_b = st.columns([1.1, 1])

    # --- COLONNE GAUCHE : CLASSE + DESCRIPTION + SCORE G0 ---
    with col_a:
        classe_predite = result.get("classe_predite")
        score_G0 = float(result.get("score_G0", 0.0))
        interpretation_G0 = result.get("interpretation_G0", "")

        st.markdown("#### Classe d’orientation principale")

        if classe_predite:
            st.markdown(
                f"""
                <div class="pfos-badge">{classe_predite}</div>
                """,
                unsafe_allow_html=True,
            )
            st.write(CATEGORIES_DESCRIPTIONS.get(classe_predite, ""))
        else:
            st.warning("Aucune classe prédite renvoyée par l’API.")

        st.markdown("---")
        st.markdown("#### Score G0 (probabilité d’intégrer une école G0)")

        # Jauge simple avec progress bar
        gauge_col1, gauge_col2 = st.columns([3, 1])
        with gauge_col1:
            st.progress(min(max(score_G0 / 100.0, 0.0), 1.0))
        with gauge_col2:
            st.markdown(f"<b>{score_G0:.1f} %</b>", unsafe_allow_html=True)

        st.caption(interpretation_G0)

        st.markdown(
            "Première version du modèle : aucune validation n’est encore faite sur la "
            "qualité des entrées (ville ou collège inconnus, codes RIASEC atypiques, etc.). "
            "Les résultats restent expérimentaux."
        )

    # --- COLONNE DROITE : PROBA PAR CLASSE (GRAPHIQUE) ---
    with col_b:
        st.markdown("#### Distribution des probabilités par groupe")

        probas = result.get("probabilites_par_classe", {})

        if probas:
            df_proba = (
                pd.DataFrame(
                    [
                        {"Groupe": k, "Probabilité": float(v)}
                        for k, v in probas.items()
                    ]
                )
                .sort_values("Probabilité", ascending=False)
                .reset_index(drop=True)
            )
            df_proba["Probabilité (%)"] = df_proba["Probabilité"] * 100

            st.bar_chart(
                df_proba.set_index("Groupe")["Probabilité (%)"],
                height=260,
            )

            st.dataframe(
                df_proba[["Groupe", "Probabilité (%)"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Aucune probabilité détaillée n’a été renvoyée par l’API.")

    st.markdown(
        '<div class="pfos-footer">'
        'PFOS – Plateforme d’Orientation Scolaire · Interface de démonstration '
        'connectée au moteur d’IA interne.'
        '</div>',
        unsafe_allow_html=True,
    )