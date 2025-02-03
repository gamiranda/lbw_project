import streamlit as st

st.set_page_config(
        page_title="Página principal",
)


st.title("Pág. Principal")

st.header("Informações sobre Baixo Peso ao Nascer no Brasil")
st.write("Nesse aplicativo você encontrará diversas informações sobre os nascidos vivos do Brasil ao longo dos anos.")
st.write("A principal fonte para os dados aqui apresentados é o Sistema de Informação sobre Nascidos Vivos – Sinasc.")

url = "https://opendatasus.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc"

st.write("Fonte: [clique aqui](%s)" % url)