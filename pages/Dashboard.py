# Importação das bibliotecas

import pandas as pd
import re
import folium
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

# Importação do dataset
#O r antes das aspas vem de raw, ou seja, a string será interpretada como uma string literal.

df_original = pd.read_csv('train.csv')

#Criar uma cópia do dataframe para preservar a versão original

df = df_original.copy()


# =======================
# LIMPEZA DOS DADOS
# =======================

#Remover linhas com valores vazios

for i in list(df.columns):
  filtro = df[i] != 'NaN '
  df = df.loc[filtro,:] 

df = df.reset_index( drop=True )
    
#Remover espaços em branco

df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Delivery_person_ID'] = df.loc[:,'Delivery_person_ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
df.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()
df.loc[:,'City'] = df.loc[:,'City'].str.strip()
df.loc[:,'Time_taken(min)'] = df.loc[:,'Time_taken(min)'].str.strip()


#Remover texto indesejado em colunas:

df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )

df['Weatherconditions'] = df['Weatherconditions'].apply( lambda x: x.split( 'conditions ')[1] )
    
#Corrigir máscara das colunas com data

df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

#Corrigir os tipos das colunas

df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

#Listas úteis

weather = df['Weatherconditions'].unique()
traffic = df['Road_traffic_density'].unique()
cidades = df['City'].unique()


# =======================
# Barra Lateral
# =======================

#Inserir imagem (logotipo)
st.sidebar.image(Image.open('logotipo.png'), width = 120)

#Colocar título
st.sidebar.title('Cury Company')

#criar filtro de DATA:

st.sidebar.markdown( """---""" )

st.sidebar.markdown('## Selecione a data limite:')

date_slider = st.sidebar.slider(
    'Arraste o marcador até a data desejada.',
    value = pd.to_datetime(2022, 4, 6),
    min_value = pd.to_datetime(2022, 2, 11),
    max_value = pd.to_datetime(2022, 4, 6),
    format = 'DD-MM-YYYY',
    label_visibility = 'collapsed')
   
df = df.loc[df['Order_Date'] <= date_slider, :]

st.sidebar.markdown( """---""" )

#criar filtro de condição de TRÁFEGO:

st.sidebar.markdown('## Selecione as condições de tráfego:')

traffic_select = st.sidebar.multiselect(
    'label',
    traffic,
    default = traffic,
    label_visibility = 'collapsed') 

df = df.loc[df['Road_traffic_density'].isin(traffic_select), :]
    
st.sidebar.markdown( """---""" )
    
#criar filtro de condição do TEMPO:
    
st.sidebar.markdown('## Selecione as condições do tempo:')

weather_select = st.sidebar.multiselect(
    'label',
    weather,
    default = weather,
    label_visibility = 'collapsed')

df = df.loc[df['Weatherconditions'].isin(weather_select), :]
    
st.sidebar.markdown( """---""" )

#criar filtro de CIDADE:
    
st.sidebar.markdown('## Selecione a cidade:')

cidade_select = st.sidebar.multiselect(
    'label',
    cidades,
    default = cidades,
    label_visibility = 'collapsed')

df = df.loc[df['City'].isin(cidade_select), :]
    
st.sidebar.markdown( """---""" )


# ===========================================
# Layout Dashboard
# ===========================================

st.header('Dashboard de Acompanhamento')

# Criar uma aba para cada visão

tab1, tab2, tab3 = st.tabs(['**Visão Empresa**', '**Visão Entregadores**', '**Visão Restaurantes**'])


# ===========================================
# Layout Dashboard - Aba VISÃO EMPRESA
# ===========================================

with tab1:
    
    tab01, tab02, tab03 = st.tabs(['Gerencial', 'Tática', 'Geográfica'])
    
    
# ===================================================
# Layout Dashboard - Aba VISÃO EMPRESA - Gerencial
# ===================================================

    with tab01:

# PRIMEIRO CONTAINER

        with st.container():
            st.markdown('## Pedidos por dia:')

            pedidos_dia = df.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()

            fig = px.bar(pedidos_dia, x='Order_Date', y='ID')

            st.plotly_chart(fig, use_container_width=True)

# SEGUNDO CONTAINER

        with st.container():

            col1, col2 = st.columns(2)

            with col1:

                st.markdown('### Pedidos por Tráfego')

                pedidos_trafego = df.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

                pedidos_trafego['%_entregas'] = pedidos_trafego['ID'] / pedidos_trafego['ID'].sum()

                fig = px.pie(pedidos_trafego, values = '%_entregas', names = 'Road_traffic_density')

                st.plotly_chart(fig, use_container_width = True)


            with col2:

                st.markdown('### Pedidos por Cidade e Tráfego')

                pedidos_cidade_trafego = df.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()

                fig = px.scatter(pedidos_cidade_trafego, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City', symbol = 'Road_traffic_density') 

                st.plotly_chart(fig, use_container_width = True)

                
# ===================================================
# Layout Dashboard - Aba VISÃO EMPRESA - Tática
# ===================================================

    with tab02:
        
#PRIMEIRO CONTAINER:
        
        with st.container():
            
            st.markdown('### Pedidos por semana:')
            
            df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
            
            pedidos_semana = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
            
            fig = px.line(pedidos_semana, x = 'week_of_year', y = 'ID')
            
            st.plotly_chart(fig, use_container_width = True)
    

#SEGUNDO CONTAINER:
        
        with st.container():
            
            st.markdown('### Pedidos por entregador por semana:')
            
            entregadores_semana = df.loc[:,['week_of_year','Delivery_person_ID']].groupby('week_of_year').nunique().reset_index()
            resposta = pd.merge(entregadores_semana, pedidos_semana, how = 'inner')
            resposta['pedidos_por_entregador'] = resposta['ID'] / resposta['Delivery_person_ID']
            
            fig = px.line(resposta, x = 'week_of_year', y = 'pedidos_por_entregador')
            
            st.plotly_chart(fig, use_container_width = True)
            
            
# ===================================================
# Layout Dashboard - Aba VISÃO EMPRESA - Geográfica
# ===================================================
    
    with tab03:

        with st.container():

            st.markdown('### Localização de cada cidade por tipo de tráfego')

            localizacao_central = df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()

            mapa = folium.Map()

            for i in range(len(localizacao_central)):

                folium.Marker([localizacao_central.loc[i,'Delivery_location_latitude'], localizacao_central.loc[i,'Delivery_location_longitude']]).add_to(mapa)

            folium_static(mapa, width = 1024, height = 600)

# ===========================================
# Layout Dashboard  - Visão ENTREGADORES
# ===========================================

with tab2:

# PRIMEIRO CONTAINER

    with st.container():

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            st.metric('A maior idade é:', maior_idade)

        with col2:

            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            st.metric('A menor idade é:', menor_idade)

        with col3:

            melhor_condicao = df.loc[:,'Vehicle_condition'].max()
            st.metric('A melhor condição de veículo é:', melhor_condicao)

        with col4:

            pior_condicao = df.loc[:,'Vehicle_condition'].min()
            st.metric('A pior condição de veículo é:', pior_condicao)

# SEGUNDO CONTAINER

    with st.container():

        st.markdown('### Média de avaliação das entregas:')

        col1, col2 = st.columns(2)

        with col1:

            nota_entregador = np.round(df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index(), 2)

            nota_entregador.columns = ['ID Entregador', 'Avaliação média']

            st.dataframe(nota_entregador)

        with col2:

            with st.container():

                nota_transito = np.round(df.loc[:,['Road_traffic_density','Delivery_person_Ratings']].groupby('Road_traffic_density').mean().reset_index(), 2)

                nota_transito.columns = ['Densidade do trânsito', 'Avaliação média']

                st.dataframe(nota_transito)


            with st.container():

                nota_clima = np.round(df.loc[:,['Weatherconditions','Delivery_person_Ratings']].groupby('Weatherconditions').mean().reset_index(), 2)

                nota_clima.columns = ['Condição do tempo', 'Avaliação média']

                st.dataframe(nota_clima)

# TERCEIRO CONTAINER

    with st.container():

        col1, col2 = st.columns(2)

        with col1:

            st.markdown('### Top 10 entregadores mais rápidos:')

            mais_rapidos = (df.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
                              .groupby('Delivery_person_ID')
                              .mean()
                              .sort_values('Time_taken(min)', ascending = True)
                              .reset_index() )

            mais_rapidos.columns = ['Entregador', 'Tempo de entrega']

            st.dataframe(mais_rapidos)


        with col2:

            st.markdown('### Top 10 entregadores mais lentos:')

            mais_lentos = (df.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
                              .groupby('Delivery_person_ID')
                              .mean()
                              .sort_values('Time_taken(min)', ascending = False)
                              .reset_index() )

            mais_lentos.columns = ['Entregador', 'Tempo de entrega']

            st.dataframe(mais_lentos)

# ===========================================
# Layout Dashboard  - Visão RESTAURANTES
# ===========================================

with tab3:

# PRIMEIRO CONTAINER

    with st.container():
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        
        with col1:
            
            entregadores_unicos = len(df['Delivery_person_ID'].unique())
            
            st.metric('Entregadores:', entregadores_unicos)
            
        with col2:
            
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

            df['distance'] = df.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1)
            
            distancia_media = np.round(df.loc[:, 'distance'].mean(),2)
            
            st.metric('Distância média:', distancia_media)
            
        
        with col3:
                     
            tempo_com_festival = np.round(df.loc[df['Festival'] == 'Yes', 'Time_taken(min)'].mean(),2)
            
            st.metric('Tempo com Festival', tempo_com_festival)
            
        
        with col4:
            
            desvio_com_festival = np.round(df.loc[df['Festival'] == 'Yes', 'Time_taken(min)'].std(),2)
            
            st.metric('DP com Festival', desvio_com_festival)
            
        
        with col5:
            
            tempo_sem_festival = np.round(df.loc[df['Festival'] == 'No', 'Time_taken(min)'].mean(),2)
            
            st.metric('Tempo sem Festival', tempo_sem_festival)
            
        
        with col6:
          
            desvio_sem_festival = np.round(df.loc[df['Festival'] == 'No', 'Time_taken(min)'].std(),2)
            
            st.metric('DP sem Festival', desvio_sem_festival)    
    
# SEGUNDO CONTAINER

    with st.container():
        
        col1, col2 = st.columns(2)

        with col1:            # Tempo médio por cidade
            
            st.markdown('### Tempo médio por cidade:')
            
            tempo_por_cidade = np.round(df.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index(), 2)
            tempo_por_cidade.columns = ['cidade','tempo_medio', 'desvio']            
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(name = 'Control', x = tempo_por_cidade['cidade'], y = tempo_por_cidade['tempo_medio'], error_y = dict(type = 'data', array = tempo_por_cidade['desvio'])))
            fig.update_layout(barmode = 'group')

            st.plotly_chart(fig)
     
        
        with col2:        # Tempo médio por cidade e tipo de pedido
        
            st.markdown('### Tempo médio por cidade e tipo de pedido:')
            
            tempo_por_cidade_pedido = np.round(df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                                                 .groupby(['City', 'Type_of_order'])
                                                 .agg({'Time_taken(min)': ['mean', 'std']})
                                                 .reset_index(), 2)
            
            tempo_por_cidade_pedido.columns = ['Cidade', 'Tipo de pedido', 'Tempo médio', 'Desvio padrão']
            
            st.dataframe(tempo_por_cidade_pedido)
            
# TERCEIRO CONTAINER

    with st.container():
        
        col1, col2 = st.columns(2)

        with col1:            #tempo médio por cidade e tipo de tráfego 
            
            st.markdown('### Tempo médio por cidade e tipo de tráfego:')
            
            tempo_cidade_trafego = np.round(df.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                              .groupby(['City', 'Road_traffic_density'])
                                              .agg({'Time_taken(min)': ['mean', 'std']})
                                              .reset_index(), 2)
            tempo_cidade_trafego.columns = ['cidade', 'trânsito','tempo_medio', 'desvio']
            
            fig = px.sunburst(tempo_cidade_trafego, path = ['cidade', 'trânsito'], values = 'tempo_medio',
                              color = 'desvio', color_continuous_scale = 'oranges',
                              color_continuous_midpoint = np.average(tempo_cidade_trafego['desvio']))
            
            st.plotly_chart(fig)            

        
        with col2:

            st.markdown('### Distância média por cidade:')

            distancia_media = np.round(df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index(),2)

            fig = go.Figure(data = [go.Pie(labels= distancia_media['City'], values = distancia_media['distance'])])

            st.plotly_chart(fig)
