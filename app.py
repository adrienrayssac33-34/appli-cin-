import base64
import streamlit as st

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Ciné Vintage", page_icon="📽",layout="wide")

# ==============================
# BACKGROUND LANDING
# ==============================
def set_bg(path: str):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_bg("assets/landing_background.png")

# ==============================
# CSS LANDING
# ==============================
st.markdown(
    """
<style>
/* Cache sidebar uniquement sur landing */
[data-testid="stSidebar"] { display: none !important; }

/* Police vintage */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&display=swap');

/* ================= Banner ================= */
.landing-banner{
  max-width: 1100px;
  margin: 6vh auto 0 auto;
  height: 340px;
  border-radius: 18px;

  background-image: url("assets/banner.png");
  background-size: cover;
  background-position: center;

  display: flex;
  align-items: center;
  justify-content: center;

  box-shadow: inset 0 0 0 1000px rgba(0,0,0,0.45);
  border: 1px solid rgba(255, 210, 140, 0.25);
}

.landing-content{
  text-align: center;
  padding: 30px;
}

.landing-content h1{
  font-family: 'Cinzel', serif;
  font-size: 56px;
  margin: 0 0 12px 0;
  color: #F8E7C2;
  text-shadow: 2px 2px 16px rgba(0,0,0,0.9);
}

.landing-content p{
  font-size: 18px;
  margin: 0;
  color: #FFE7B5;
  text-shadow: 1px 1px 10px rgba(0,0,0,0.9);
}

/* ================= Buttons ================= */
div.stButton > button {
    border-radius: 12px !important;
    padding: 0.8rem 1.2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    border: 1px solid rgba(255, 210, 140, 0.3) !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;
}

/* Orange cinéma */
div.stButton > button[kind="primary"]{
    background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
    color: #FFF3D6 !important;
}

/* Bleu vintage */
div.stButton > button[kind="secondary"]{
    background: linear-gradient(180deg, #24586B, #163844) !important;
    color: #FFF3D6 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================
# LANDING UI
# ==============================
st.markdown(
    """
<div class="landing-banner">
    <div class="landing-content">
        <h1>Redécouvrez le cinéma selon vos goûts</h1>
        <p>Une plateforme de recommandation dédiée aux amateurs de films classiques et intemporels.</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Boutons centrés sous la bannière
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    left, right = st.columns(2)

    with left:
        if st.button("S'inscrire", type="secondary", use_container_width=True):
            st.switch_page("pages/inscription.py")

    with right:
        if st.button("Se connecter", type="primary", use_container_width=True):
            st.switch_page("pages/connexion.py")