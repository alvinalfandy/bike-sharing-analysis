import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test", layout="wide")
st.title("Test App")
st.write("App berhasil jalan!")

df = pd.read_csv("bike-sharing-dataset/hour.csv")
st.write(f"Dataset: {df.shape[0]} baris, {df.shape[1]} kolom")
st.dataframe(df.head())
