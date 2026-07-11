import streamlit as st
import pandas as pd

st.title("Test App")
st.write("App berhasil jalan!")

df = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6]})
st.dataframe(df)
