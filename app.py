import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Analisis Bike Sharing", layout="wide")

st.title("Dashboard Analisis Bike Sharing")

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bike-sharing-dataset", "hour.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df.sample(3000, random_state=42).reset_index(drop=True)
    return None

df = load_data()

if df is None:
    st.error("Dataset tidak ditemukan.")
    st.stop()

st.write(f"Dataset: {df.shape[0]} baris, {df.shape[1]} kolom")

tab1, tab2 = st.tabs(["Data", "Statistik"])

with tab1:
    st.dataframe(df.head(100))

with tab2:
    st.write(df.describe())
