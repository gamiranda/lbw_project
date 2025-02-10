import folium
import plotly.express as px
import requests

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

def brazil_map(data):
    
    #brazil_geojson = json.load("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/brazil_geo.json")

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


def promptTemp(llm, user_query, chat_history):
  

  #Você é um especialista em Baixo Peso ao Nascer. Responda a seguinte pergunta somente se ela for sobre Baixo Peso ao Nascer:
  #Se a pergunta não for sobre Baixo Peso ao Nascer responda: "Eu só respondo perguntas sobre Baixo Peso ao Nascer".
  
  system_prompt = """
  You are a Low Birth Weight specialist. Answer the following question only if it is about Low Birth Weight. 
  Always answer in Brazilian Portuguese.
  If the question is not about Low Birth Weight answer: "Eu só respondo perguntas sobre Baixo Peso ao Nascer.".
                                                                      
  """

  user_prompt = "{input}"

  prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", user_prompt)
    ])

  chain = prompt_template | llm | StrOutputParser()

  return chain.stream({
        "chat_history": chat_history,
        "input": user_query,
    })