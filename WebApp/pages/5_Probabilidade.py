
import streamlit as st
import joblib
import pandas as pd
import numpy as np

st.title("Calcule a Probabilidade do evento")

#### Lendo a função do FunctionTransformer (provisório)
def columnTrunc(data, vars):
    for var in vars:
        data[var] = np.where(data[var] > 10.0, 10.0, data[var])

    return data

#### Lendo o pipeline do modelo
pipe = joblib.load('C:\\Users\\Usuario\\Desktop\\GitHub\\LWB_article\\LBW_article\\model_lbw.joblib') 

data = {
    "NOME_PACIENTE"	: "Paciente 1"
    ,"IDADEMAE"	    : "25.0"
    ,"IDADEPAI"	    : "26.0"
    ,"ESTCIVMAE"	: "1.0"
    ,"ESCMAE"	    : "0.0"
    ,"QTDFILVIVO"   : "0.0"	
    ,"QTDFILMORT"   : "0.0"		
    ,"QTDPARTNOR"   : "0.0"		
    ,"QTDPARTCES"   : "0.0"		
    ,"QTDGESTANT"   : "0.0"		
    ,"GRAVIDEZ"	    : "1.0"	
    ,"RACACORMAE"   : "4.0"	
}

# Convert the data to a DataFrame
data = pd.DataFrame(data, index=[0])

# Convert the DataFrame to a CSV string
csv = data.to_csv("Planilha_Exemplo.csv",index=False)

st.write("Planilha com estrutura de exemplo:")
st.dataframe(data)

#st.download_button(
#    label="Download data as CSV",
#    data=csv,
#    file_name='Planilha_exemplo.csv',
#    mime='text/csv',
#)

#st.header("Prob. Baixo Peso ao Nascer")
new_data = st.file_uploader("Adicione a planilha:", type = ["csv"])
if new_data is not None:
    new_data = pd.read_csv(new_data)
    st.write("Tabela anexada:")
    st.dataframe(new_data)

    new_pred = pipe.predict_proba(new_data)[:, 1]

    output_data = pd.DataFrame(
        {
            'NOME_PACIENTE': [data['NOME_PACIENTE'].to_numpy()],
            'RISCO': [new_pred]
        }
    )

    output_data['RISCO'] = np.select(
        [
            output_data['RISCO'] < 0.3,
            (output_data['RISCO'] >= 0.3) & (output_data['RISCO'] < 0.6),
            (output_data['RISCO'] >= 0.6) & (output_data['RISCO'] < 0.8),
            output_data['RISCO'] >= 0.8
        ],
        [
            "Baixo",
            "Moderado",
            "Alto",
            "Muito Alto"
        ]
    )

    st.dataframe(output_data)
    

#### Calculando a previsão




