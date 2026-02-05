import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("🏛️ Normas Curitiba PRO")
st.caption("Arquitetura, Urbanismo & OOH/LED")

@st.cache_data
def carregar_normas():
    df = pd.read_csv('leis.csv')
    return df

normas = carregar_normas()
st.caption(f"📊 {len(normas)} normas carregadas")

projeto = st.text_area("Descreva seu projeto:", 
                      placeholder="painel LED OOH 25m² Av Batel ZR-3")

if st.button("🔍 CONSULTAR NORMAS") and projeto:
    for norma in normas.head(5).to_dict('records'):
        with st.expander(norma['nome']):
            st.write(norma['assunto'])
            st.markdown(f"[👉 {norma['url']}]({norma['url']})")
