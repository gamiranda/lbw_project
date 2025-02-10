
import pandas as pd
import streamlit as st
import streamlit_folium as stf
import funcoesLBW as fl

st.title("Mapa do Baixo Peso ao Nascer - BR")

#dt_group_ANO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO.csv", sep = ";")
#dt_group_ANO_REGIAO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO_REGIAO.csv")
dt_group_ANO_ESTADO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO_ESTADO.csv", sep = ";")

#dt_group_ANO_ESTADO = dt_group_ANO_ESTADO[dt_group_ANO_ESTADO['ANO'] == 2023]

# Create a DataFrame
df = pd.DataFrame({
    'Estado': dt_group_ANO_ESTADO['ESTADO'].to_numpy(),
    'Ano': dt_group_ANO_ESTADO['ANO'].to_numpy(),
    'Proporção': dt_group_ANO_ESTADO['AVG_BAIXO_PESO'].to_numpy()
})

df = pd.DataFrame(df)

if "selected_year" not in st.session_state:
    st.session_state.selected_year = None

col1, col2, col3, col4, col5, col6, col7, = st.columns(7)

col8, col9, col10, col11, col12, col13, right  = st.columns(7)


with col1:
    if st.button("2011"):
        st.session_state.selected_year = 2011

with col2:
    if st.button("2012"):
        st.session_state.selected_year = 2012

with col3:
    if st.button("2013"):
        st.session_state.selected_year = 2013

with col4:
    if st.button("2014"):
        st.session_state.selected_year = 2014

with col5:
    if st.button("2015"):
        st.session_state.selected_year = 2015

with col6:
    if st.button("2016"):
        st.session_state.selected_year = 2016

with col7:
    if st.button("2017"):
        st.session_state.selected_year = 2017

with col8:
    if st.button("2018"):
        st.session_state.selected_year = 2018

with col9:
    if st.button("2019"):
        st.session_state.selected_year = 2019

with col10:
    if st.button("2020"):
        st.session_state.selected_year = 2020

with col11:
    if st.button("2021"):
        st.session_state.selected_year = 2021

with col12:
    if st.button("2022"):
        st.session_state.selected_year = 2022

with col13:
    if st.button("2023"):
        st.session_state.selected_year = 2023


# Filter the data based on the selected year
if st.session_state.selected_year is not None:
    filtered_df = df.query("Ano == @st.session_state.selected_year").drop("Ano", axis=1)
    st.header(f"Mapa iterativo para o ano de {st.session_state.selected_year}:")

    # Generate the map
    m = fl.brazil_map(filtered_df)
    map_data = stf.st_folium(m, width=700, height=500)
    st.write(map_data)
else:
    st.write("")

