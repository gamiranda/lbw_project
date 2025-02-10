from langchain_ollama import ChatOllama
from langchain.cache import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
import funcoesLBW as fl

st.title("Faça perguntas")

set_llm_cache(InMemoryCache())

### Carregando o LLM llama3 no modo Chat.
llm = ChatOllama(
        model="llama3",
        temperature=0.1,
    )

st.write("Nessa seção você pode conversar com um especialista virtual sobre Baixo Peso ao Nascer. Tire suas dúvidas sobre o tema:")

if "chat_history" not in st.session_state: ### Inicia a sessão para manter registro das mensagens já enviadas na sessão.
    st.session_state.chat_history = [
        AIMessage(content="Olá! Como posso ajudar você?"),
    ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):  ### Verifica se a mensagem foi enviada pela "IA"
        with st.chat_message("AI"):  ### Configura o avatar de IA que aparece no chat
            st.write(message.content)  ### Retorna em tela a mensagem da "IA"
    elif isinstance(message, HumanMessage): ### Verifica se a mensagem foi enviada pelo "Humano"
        with st.chat_message("Human"): ### Configura o avatar de IA que aparece no chat
            st.write(message.content)  ### Retorna em tela a mensagem do "Humano"

user_query = st.chat_input("Digite sua mensagem aqui...") ### Recebe a mensagem do "Humano"
if user_query is not None and user_query != "":  ### Verifica se o "Humano" passou alguma mensagem (não passa vazio para o llm)
    st.session_state.chat_history.append(HumanMessage(content=user_query)) ### Adiciona a mensagem passada pelo "Humano" no historico do chat

    with st.chat_message("Human"):
        st.markdown(user_query) ### Registra a mensagem do "Humano" em tela

    with st.chat_message("AI"):
        resp = st.write_stream(fl.promptTemp(llm=llm, user_query=user_query, chat_history=st.session_state.chat_history)) ### Retorna a mensagem da "IA"
        print(st.session_state.chat_history) ### 

    st.session_state.chat_history.append(AIMessage(content=resp))


######################################################################################

