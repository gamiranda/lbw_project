from langchain_community.llms import Ollama
import streamlit as st
import funcoesLBW as fl

st.title("Faça perguntas")

llm = Ollama(model = "mistral")

st.write("Nessa seção você pode fazer perguntas sobre Baixo Peso ao Nascer. Tire suas dúvidas sobre o tema:")

prompt = st.text_area("")
if st.button("Pressione"):
    if prompt:
        with st.spinner(""):
            #st.write_stream(llm.stream(prompt, stop=['<|eot_id|>']))
            st.write(fl.promptTemp(llm, prompt))

######################################################################################

