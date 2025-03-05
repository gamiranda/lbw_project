import folium
import plotly.express as px
import requests

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

from langchain_community.llms import Ollama 

def brazil_map(data):
    
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    response = requests.get(url)
    brazil_geojson = response.json()

    # Add proportion data to the GeoJSON features
    for feature in brazil_geojson["features"]:
        state_code = feature["properties"]["sigla"]
        proportion = data[data["Estado"] == state_code]["Proporção"].values
        if len(proportion) > 0:
            feature["properties"]["proportion"] = proportion[0]
        else:
            feature["properties"]["proportion"] = "N/A"  # Handle missing data

    # Create a base map centered on Brazil
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

    # Add a choropleth layer
    folium.Choropleth(
        geo_data=brazil_geojson,  # GeoJSON file
        name="choropleth",
        data=data,  # Dataframe with proportions
        columns=["Estado", "Proporção"],  # Columns for state IDs and values
        key_on="feature.properties.sigla",  # Key in GeoJSON to match with state IDs
        fill_color="YlOrRd",  # Color scale
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Proporção BPN (%)",
        highlight=True,
    ).add_to(m)

    # Add tooltips to show state names, codes, and proportions
    folium.GeoJson(
        brazil_geojson,
        name="Proporção de Baixo Peso ao Nascer",
        style_function=lambda feature: {
            "fillColor": "#ffffff",
            "color": "black",
            "weight": 0.3,
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=["name", "sigla", "proportion"],  # Fields from GeoJSON
            aliases=["Estado: ", "Codigo: ", "Proporção (%): "],  # Labels for fields
            localize=True,
            style=("font-weight: bold;"),  # Customize tooltip style
        ),
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m


def evol_lbw(data):
    # Create the line chart
    fig = px.line(data, x='Ano', y='Proporção',
                title='<b>Proporção BPN de 2010 to 2023</b>',
                markers=True,
                color_discrete_sequence=['#1f77b4'],  # Custom line color
                template='plotly_white')

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title='<b>Ano</b>',
        yaxis_title='<b>Proporção BPN (%)</b>',
        font=dict(family='Arial', size=12, color='#2a3f5f'),
        title_font=dict(size=20, color='#2a3f5f', family='Arial Black'),
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            showgrid=True,
            gridcolor='lightgray',
            linecolor='gray',
            linewidth=2,
            mirror=True
        ),
        yaxis=dict(
            range=[7, 10.5],
            showgrid=True,
            gridcolor='lightgray',
            linecolor='gray',
            linewidth=2,
            mirror=True
        ),
        plot_bgcolor='rgba(255, 255, 255, 1)',  # White background
        paper_bgcolor='rgba(255, 255, 255, 1)',  # White paper background
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial'
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Add annotations for the first and last data points
    fig.add_annotation(
        x=data.loc[data['Proporção'].idxmin(), 'Ano'],
        y=data.loc[data['Proporção'].idxmin(), 'Proporção'],
        text=f"{data.loc[data['Proporção'].idxmin(), 'Proporção']:.2f}%",
        showarrow=True,
        arrowhead=1,
        ax=-50,
        ay=-40,
        font=dict(size=12, color='#2a3f5f')
    )

    fig.add_annotation(
        x=data.loc[data['Proporção'].idxmax(), 'Ano'],
        y=data.loc[data['Proporção'].idxmax(), 'Proporção'],
        text=f"{data.loc[data['Proporção'].idxmax(), 'Proporção']:.2f}%",
        showarrow=True,
        arrowhead=1,
        ax=50,
        ay=-40,
        font=dict(size=12, color='#2a3f5f')
    )

    # Customize markers
    fig.update_traces(
        marker=dict(size=10, color='#ff7f0e', line=dict(width=2, color='white')),
        line=dict(width=3)
    )

    return fig

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def contextualized_question(input: dict):

    llm = Ollama(model="llama3")

    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt= ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input["question"]

def rag_chat(llm, user_query, chat_history):
    
    embedding = OllamaEmbeddings(
    model="nomic-embed-text",
    )
  
    db = Chroma(persist_directory="db", embedding_function=embedding)

    retriever = db.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k": 3}
    )

    template = """       
    You are a Low Birth Weight specialist. Always answer in portuguese.
    You can only answer question related to Low Birth Weight. Answer the question based only on the following context:

    {context}
    """

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        RunnablePassthrough.assign(
            context = contextualized_question | retriever | format_docs
        )
        | prompt_template 
        | llm
    )

    return rag_chain.stream(
        {
            "question": user_query,
            "chat_history": chat_history
        }
    )


def rag_questions(llm, question: str) -> str:
  
    embedding = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    db = Chroma(persist_directory="db", embedding_function=embedding)

    retriever = db.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k": 3}
    )
  
    template = PromptTemplate.from_template("""       
    You are a Low Birth Weight specialist. Always answer in portuguese. Don't show up your thinking.
    You can only answer question related to Low Birth Weight. Answer the question based only on the following context:

    {context}

    ---

    {question}
    """)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | template 
        | llm 
        | StrOutputParser()
    )

    return chain.stream({"question": question})