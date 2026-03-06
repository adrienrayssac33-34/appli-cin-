import os
import sqlite3
import hashlib
import base64
import streamlit as st

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Connexion - Ciné Vintage", page_icon="📽", layout="wide")

# ==============================
# BACKGROUND + HIDE SIDEBAR
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
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ padding-top: 3rem; }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("assets/landing_background.png")

st.markdown("""
<style>

/* 1) Overlay sombre global pour le contraste */
[data-testid="stAppViewContainer"]::before{
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);   /* ajuste 0.35 -> 0.60 */
  z-index: 0;
}

/* 2) Remettre le contenu au-dessus de l'overlay */
[data-testid="stAppViewContainer"] > .main{
  position: relative;
  z-index: 1;
}

/* 3) Titres et textes lisibles */
h1, h2, h3, p, label, span {
  color: #F8E7C2 !important;
  text-shadow: 1px 1px 10px rgba(0,0,0,0.8);
}

/* 4) Inputs : fond clair + coins arrondis */
div[data-baseweb="input"] > div{
  background: rgba(255,255,255,0.92) !important;
  border-radius: 10px !important;
  border: 1px solid rgba(255,210,140,0.35) !important;
}

/* 5) Bouton principal cuivré */
.stButton > button[kind="primary"]{
  background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
  color: #FFF3D6 !important;
  border: 1px solid rgba(255,210,140,0.35) !important;
  border-radius: 12px !important;
  font-weight: 800 !important;
  box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;
}

/* 6) Boutons secondaires plus soft */
.stButton > button[kind="secondary"]{
  background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
  color: #FFF3D6 !important;
  border: 1px solid rgba(255,210,140,0.35) !important;
  border-radius: 12px !important;
  font-weight: 800 !important;
  box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;, .stButton > button{
  border-radius: 12px !important; color: #B22222 !important;

}
            
            /* centrer les boutons */
.stButton{
    display:flex;
    justify-content:center;
}

/* 7) Un peu de largeur/respiration */
.block-container{
  padding-top: 3rem !important;
  max-width: 950px !important;   /* centre naturellement */
}
            

}           
</style>
""", unsafe_allow_html=True)

# ==============================
# CARD CSS (cible le wrapper "border" du container)
# ==============================
st.markdown("""
<style>
/* Card native (container border=True) */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: rgba(10, 8, 6, 0.66) !important;
  border: 1px solid rgba(255, 210, 140, 0.30) !important;
  border-radius: 22px !important;
  padding: 30px 28px 22px 28px !important;
  box-shadow: 0 22px 65px rgba(0,0,0,0.60) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
}

/* Titre & sous-titre */
.auth-title{
  font-size: 46px;
  font-weight: 800;
  color: #F8E7C2;
  text-align: center;
  margin: 0 0 8px 0;
  text-shadow: 2px 2px 16px rgba(0,0,0,0.85);
}
.auth-sub{
  text-align: center;
  color: rgba(255, 232, 194, 0.90);
  margin-bottom: 18px;
}

/* Labels lisibles */
label, p { color: rgba(255, 232, 194, 0.92) !important; }

/* Inputs plus premium */
div[data-baseweb="input"] > div{
  background: rgba(255,255,255,0.92) !important;
  border-radius: 10px !important;
}

/* Boutons */
.stButton > button{
  width: 100%;
  border-radius: 12px !important;
  padding: 0.8rem 1rem !important;
  font-weight: 800 !important;
  border: 1px solid rgba(255, 210, 140, 0.30) !important;
  box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;
}
.stButton > button[kind="primary"]{
  background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
  color: #FFF3D6 !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# DB
# ==============================
DB_PATH = os.path.join("data_raw", "users.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# AUTH GUARD
# ==============================
if st.session_state.get("authenticated", False):
    st.switch_page("pages/page_principale.py")

# ==============================
# UI (CARD CENTRÉE)
# ==============================
left, center, right = st.columns([1, 2, 1])

with center:
    # ✅ card native streamlit
    with st.container(border=True):
        st.markdown('<div class="auth-title">Connexion</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Accédez à votre espace Ciné Vintage</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            login = st.text_input("Nom d'utilisateur ou email")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", type="primary")

        if submitted:
            login_clean = (login or "").strip()
            password_clean = (password or "").strip()

            if not login_clean or not password_clean:
                st.warning("Merci de remplir les deux champs.")
            else:
                password_hash = hashlib.sha256(password_clean.encode()).hexdigest()

                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, username
                    FROM users
                    WHERE (username = ? OR email = ?)
                      AND password_hash = ?
                    """,
                    (login_clean, login_clean, password_hash)
                )
                row = cur.fetchone()
                conn.close()

                if row is None:
                    st.error("Identifiant ou mot de passe incorrects.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = row[1]
                    st.success(f"Heureux de vous revoir {row[1]} ✅")
                    st.switch_page("pages/page_principale.py")

        st.divider()
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Créer un compte"):
                st.switch_page("pages/inscription.py")
        with b2:
            if st.button("Retour landing"):
                st.switch_page("app.py")

