import os
import sqlite3
import streamlit as st
import hashlib
import base64

st.set_page_config(page_title="Inscription - Ciné Vintage", page_icon="📽", layout="wide")

# ==============================
# BACKGROUND
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

        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        /* Overlay sombre pour lisibilité */
        [data-testid="stAppViewContainer"]::before {{
            content:"";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.45);
            z-index: 0;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            position: relative;
            z-index: 1;
        }}

        /* Centre et limite la largeur */
        .block-container {{
            padding-top: 3rem;
            max-width: 950px;
        }}

        /* Textes lisibles */
        h1, h2, h3, p, label, span {{
            color: #F8E7C2 !important;
            text-shadow: 1px 1px 10px rgba(0,0,0,0.8);
        }}

        /* Inputs */
        div[data-baseweb="input"] > div {{
            background: rgba(255,255,255,0.92) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,210,140,0.35) !important;
        }}

        div[data-baseweb="input"]:focus-within {{
            box-shadow: 0 0 0 2px rgba(255,200,120,0.6);
        }}

        /* Boutons */
        .stButton > button {{
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
            font-weight: 800 !important;
            border: 1px solid rgba(255, 210, 140, 0.30) !important;
            box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;
            background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
            color: #FFF3D6 !important;
        }}

        /* bouton principal */
        .stButton > button[kind="primary"] {{
            background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
            color: #FFF3D6 !important;
        }}

        /* bouton secondaire */
        .stButton > button[kind="secondary"] {{
            background: linear-gradient(180deg, #C96A22, #8B3E12) !important;
            color: #FFF3D6 !important;
            border: 1px solid rgba(255,210,140,0.35) !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("assets/landing_background.png")

# ==============================
# DB
# ==============================
DB_PATH = os.path.join("data_raw", "users.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

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

# ==============================
# UI CENTRÉE
# ==============================
left, center, right = st.columns([1, 2, 1])

with center:

    st.markdown("<h1 style='text-align:center;'>Inscription</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Créez votre compte Ciné Vintage</p>", unsafe_allow_html=True)

    st.markdown("---")

    with st.form("register_form"):

        username = st.text_input("Nom d'utilisateur ou email", key="reg_username")

        password = st.text_input(
            "Mot de passe",
            type="password",
            key="reg_password"
        )

        submit = st.form_submit_button(
            "S'inscrire",
            type="primary",
            use_container_width=True
        )

    if submit:

        init_db()

        if username.strip() and password.strip():

            password_hash = hashlib.sha256(
                password.strip().encode()
            ).hexdigest()

            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

            conn = sqlite3.connect(DB_PATH, check_same_thread=False)

            cursor = conn.cursor()

            try:

                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username.strip(), password_hash)
                )

                conn.commit()

                st.success("Inscription réussie ✅")

                st.info(
                    f"Compte créé pour **{username.strip()}**. Veuillez vous connecter."
                )

            except sqlite3.IntegrityError:

                st.error("Nom d'utilisateur déjà existant ❌")

            except sqlite3.Error as e:

                st.error(f"Erreur SQLite: {e}")

            finally:

                conn.close()

        else:

            st.error("Veuillez saisir tous les champs.")

    st.markdown("---")

    # ==============================
    # Boutons navigation
    # ==============================

    b1, b2 = st.columns(2)

    with b1:

        if st.button(
            "Se connecter",
            type="secondary",
            use_container_width=True
        ):

            st.switch_page("pages/connexion.py")

    with b2:

        if st.button(
            "Retour landing",
            type="secondary",
            use_container_width=True
        ):

            st.switch_page("app.py")
