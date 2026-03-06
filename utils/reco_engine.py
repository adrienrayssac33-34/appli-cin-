import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors

@st.cache_data
def load_data(path_display: str, path_features: str):
    df_display = pd.read_csv(path_display)
    df_features = pd.read_csv(path_features)
    # sécurité basique
    df_display["tconst"] = df_display["tconst"].astype(str)
    df_features["tconst"] = df_features["tconst"].astype(str)
    return df_display, df_features

@st.cache_resource
def build_knn(df_features: pd.DataFrame):
    X = df_features.drop(columns=["tconst"])
    knn = NearestNeighbors(metric="cosine")
    knn.fit(X.values)
    # mapping tconst -> index ligne
    id_to_idx = pd.Series(df_features.index, index=df_features["tconst"]).to_dict()
    return knn, X, id_to_idx

def recommend_by_tconst(tconst: str, knn, X: pd.DataFrame, id_to_idx: dict, n_reco: int = 5):
    if tconst not in id_to_idx:
        raise ValueError("tconst introuvable dans df_features_encoded.")
    idx = id_to_idx[tconst]

    distances, indices = knn.kneighbors([X.iloc[idx].values], n_neighbors=n_reco + 1)

    reco_idx = [i for i in indices[0] if i != idx][:n_reco]
    reco_dist = [d for i, d in zip(indices[0], distances[0]) if i != idx][:n_reco]

    return pd.DataFrame({"idx": reco_idx, "distance_cosine": reco_dist})