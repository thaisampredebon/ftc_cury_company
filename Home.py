import streamlit as st
from PIL import Image 

st.set_page_config(
    page_title="Home",
    page_icon="🚀",
    layout="wide"
    )

# =======================
# Barra Lateral

#Inserir imagem (logotipo)
st.sidebar.image(Image.open('logotipo.png'), width = 120)

#Colocar título
st.sidebar.title('Cury Company')

#criar filtro de DATA:

st.sidebar.markdown( """---""" )

# =======================

st.write("# Cury Company Growth Dashboard")
st.markdown(
    """
    ### Como utilizar esse dashboard?
     - Visão Empresa:
         - Visão Gerencial:
         - Visão Tática:
         - Visão Geográfica:
     - Visão Entregador:
         - Acompanhamento dos indicadores semanais de crescimento
     - Visão Restaurante:
         - Indicadores semanais de crescimento dos restaurantes
    
    ### Ask for help:
        thaisampredebon@gmail.com

    """)



