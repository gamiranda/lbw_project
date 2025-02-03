#############################################

import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
import funcoesLBW as fl

# COLOCAR AS MARCAÇÕES NO MENOR E NO MAIOR ANO

dt_group_ANO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO.csv", sep = ";")
#dt_group_ANO_REGIAO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO_REGIAO.csv")
#dt_group_ANO_ESTADO = pd.read_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ESTADO.csv")

# Create a DataFrame
data = pd.DataFrame({
    'Ano': dt_group_ANO['ANO'].to_numpy(),
    'Proporção': dt_group_ANO['AVG_BAIXO_PESO'].to_numpy()
})

fig = fl.evol_lbw(data)

# Show the plot
st.plotly_chart(fig)