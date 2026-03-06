import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors
from pathlib import Path

# ==============================
# PATHS
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_raw"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(page_title="Ciné Vintage", layout="wide")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_csvs():
    df_display = pd.read_csv(DATA_DIR / "df_display_enriched.csv", delimiter=";")
    df_features = pd.read_csv(DATA_DIR / "df_features_encoded.csv")
    df_display["tconst"] = df_display["tconst"].astype(str)
    df_features["tconst"] = df_features["tconst"].astype(str)
    return df_display, df_features

df_display, df_ml = load_csvs()

# ==============================
# KNN MODEL
# ==============================
@st.cache_resource
def build_knn_model(df):
    X = df.drop(columns=["tconst"])
    knn = NearestNeighbors(metric="cosine")
    knn.fit(X)
    id_to_index = pd.Series(df.index, index=df["tconst"]).to_dict()
    return knn, X, id_to_index

knn, X_df, id_to_idx = build_knn_model(df_ml)

def recommend_movies(tconst, n=5):
    if tconst not in id_to_idx:
        return pd.DataFrame()
    idx = id_to_idx[tconst]
    distances, indices = knn.kneighbors([X_df.iloc[idx].values], n_neighbors=n + 1)
    reco_indices = [i for i in indices[0] if i != idx][:n]
    return df_ml.iloc[reco_indices][["tconst"]]

# ==============================
# POSTER AVEC IMAGE PAR DEFAUT
# ==============================
def poster_url(poster_id):
    if pd.isna(poster_id) or poster_id == "":
        return ASSETS_DIR / "no_image.png"
    return f"https://image.tmdb.org/t/p/w342/{poster_id}"

# ==============================
# LABEL FILM
# ==============================
df_display["label"] = df_display.apply(
    lambda row: f"{row['title']} ({row['originalTitle']})" if row['title'] != row['originalTitle'] else row['title'],
    axis=1
)

# ==============================
# SESSION STATE INIT
# ==============================
if "selected_tconst" not in st.session_state:
    st.session_state["selected_tconst"] = df_display.iloc[0]["tconst"]
if "current_page" not in st.session_state:
    st.session_state["current_page"] = 0
if "show_filtered" not in st.session_state:
    st.session_state["show_filtered"] = True

# ==============================
# BOUTON POUR RÉAFFICHER LES FILTRES
# ==============================
if not st.session_state["show_filtered"]:
    if st.button("← Retour aux filtres"):
        st.session_state["show_filtered"] = True
        st.session_state["current_page"] = 0
        st.rerun()

# ==============================
# SIDEBAR FILTRES (sans "Origine")
# ==============================
with st.sidebar:
    if st.session_state["show_filtered"]:
        st.header("Filtres")
        genre_selected = st.multiselect(
            "Genre",
            sorted({g.strip() for cell in df_display["genres"].dropna() for g in cell.split(",")})
        )
        year_selected = st.slider(
            "Année",
            int(df_display["startYear"].min()),
            int(df_display["startYear"].max()),
            (int(df_display["startYear"].min()), int(df_display["startYear"].max()))
        )
        runtime_selected = st.slider(
            "Durée (min)",
            int(df_display["runtimeMinutes"].min()),
            int(df_display["runtimeMinutes"].max()),
            (int(df_display["runtimeMinutes"].min()), int(df_display["runtimeMinutes"].max()))
        )
        director_selected = st.multiselect(
            "Réalisateur",
            sorted({d.strip() for cell in df_display["directors"].dropna() for d in cell.split(",")})
        )
        actor_selected = st.multiselect(
            "Acteur",
            sorted({a.strip() for cell in df_display["actors"].dropna() for a in cell.split(",")})
        )

# ==============================
# FILTRAGE
# ==============================
df_filtered = df_display.copy()
if st.session_state["show_filtered"]:
    if genre_selected:
        df_filtered = df_filtered[df_filtered["genres"].fillna("").apply(lambda x: any(g in x for g in genre_selected))]
    if year_selected:
        df_filtered = df_filtered[df_filtered["startYear"].between(year_selected[0], year_selected[1])]
    if runtime_selected:
        df_filtered = df_filtered[df_filtered["runtimeMinutes"].between(runtime_selected[0], runtime_selected[1])]
    if director_selected:
        df_filtered = df_filtered[df_filtered["directors"].fillna("").apply(lambda x: any(d in x for d in director_selected))]
    if actor_selected:
        df_filtered = df_filtered[df_filtered["actors"].fillna("").apply(lambda x: any(a in x for a in actor_selected))]

# ==============================
# PAGINATION
# ==============================
films_per_page = 20
total_pages = max(1, len(df_filtered) // films_per_page) if st.session_state["show_filtered"] else 0

# ==============================
# FONCTION POUR AFFICHER LES FILMS CLIQUABLES AVEC PAGINATION
# ==============================
def display_paginated_movies(df, section_title, button_prefix, page):
    st.markdown(f"## {section_title}")
    if df.empty:
        st.warning("Aucun film correspondant")
    else:
        start_idx = page * films_per_page
        end_idx = start_idx + films_per_page
        paginated_df = df.iloc[start_idx:end_idx]

        n_cols = 5
        for i in range(0, len(paginated_df), n_cols):
            cols = st.columns(n_cols)
            for j, (_, row) in enumerate(paginated_df.iloc[i:i+n_cols].iterrows()):
                with cols[j]:
                    st.image(str(poster_url(row["poster_id"])), width=150)
                    if st.button(
                        row["label"],
                        key=f"{button_prefix}_{row['tconst']}"
                    ):
                        st.session_state["selected_tconst"] = row["tconst"]
                        st.session_state["show_filtered"] = False
                        st.rerun()

        # Pagination controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Précédent") and st.session_state["current_page"] > 0:
                st.session_state["current_page"] -= 1
                st.rerun()
        with col2:
            st.write(f"Page {st.session_state['current_page'] + 1} / {total_pages + 1}")
        with col3:
            if st.button("Suivant") and st.session_state["current_page"] < total_pages:
                st.session_state["current_page"] += 1
                st.rerun()

# ==============================
# AFFICHAGE CONDITIONNEL DES FILMS FILTRÉS AVEC PAGINATION
# ==============================
if st.session_state["show_filtered"]:
    display_paginated_movies(df_filtered, "Films filtrés", "filtered", st.session_state["current_page"])

# ==============================
# FILM SELECTIONNE (toujours affiché)
# ==============================
selected_row = df_display[df_display["tconst"] == st.session_state["selected_tconst"]].iloc[0]
st.markdown("## Film sélectionné")
cols = st.columns([1, 2])
with cols[0]:
    st.image(str(poster_url(selected_row["poster_id"])), width=250)
with cols[1]:
    st.subheader(selected_row["label"])
    st.write("Année :", selected_row.get("startYear"))
    st.write("Genres :", selected_row.get("genres"))
    st.write("Réalisateur(s) :", selected_row.get("directors"))
    st.write("Acteurs :", selected_row.get("actors"))
    st.write("Durée :", selected_row.get("runtimeMinutes"), "min")
    if pd.notna(selected_row.get("overview")):
        st.markdown("### Synopsis")
        st.write(selected_row.get("overview"))

# ==============================
# RECOMMANDATIONS KNN (sans pagination, toujours affichées)
# ==============================
st.markdown("## Vous pourriez aussi aimer")
reco_df = recommend_movies(st.session_state["selected_tconst"])
if not reco_df.empty:
    df_reco = df_display[df_display["tconst"].isin(reco_df["tconst"])].copy()
    n_cols = 5
    for i in range(0, len(df_reco), n_cols):
        cols = st.columns(n_cols)
        for j, (_, row) in enumerate(df_reco.iloc[i:i+n_cols].iterrows()):
            with cols[j]:
                st.image(str(poster_url(row["poster_id"])), width=150)
                if st.button(
                    row["label"],
                    key=f"reco_{row['tconst']}"
                ):
                    st.session_state["selected_tconst"] = row["tconst"]
                    st.rerun()