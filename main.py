import streamlit as st
from utilidades import *
from views.base import *
from views.colaborador import *
from views.painel import *
from views.historico import *
from views.redea import *


@st.cache_data()
def carregar_dados(arquivo):
    df_data = pd.read_excel(arquivo, engine="openpyxl", sheet_name="LISTA")
    return df_data


if __name__ == "__main__":
    st.set_page_config("Portal", layout="wide")
    with st.sidebar:
        with st.expander("Base De Migração"):
            base_de_migracao = st.file_uploader(
                "Anexar Base De Migração", type=["xlsx"], key="unique_key_1"
            )

    if base_de_migracao is not None:

        iniciar_dados(carregar_dados(base_de_migracao))
        st.sidebar.divider()
        st.sidebar.button(
                "Painel De Migração",
                use_container_width=True,
                on_click=mudar_pagina,
                args=("pag_home",),
                type="primary",
            )
        st.sidebar.button(
                "Base De Migração",
                use_container_width=True,
                on_click=mudar_pagina,
                args=("pag_base_migracao",),
                type="primary",
            )
        st.sidebar.button(
                "Colaborador",
                use_container_width=True,
                on_click=mudar_pagina,
                args=("pag_colaborador",),
                type="primary",
            )
        st.sidebar.button(
                "Histórico De Migração",
                use_container_width=True,
                on_click=mudar_pagina,
                args=("pag_historico",),
                type="primary",
            )
        st.sidebar.button(
                "Painel REDEA",
                use_container_width=True,
                on_click=mudar_pagina,
                args=("pag_readea",),
                type="primary",
            )

        if st.session_state["pagina_central"] == "pag_home":
            painel()

        elif st.session_state["pagina_central"] == "pag_base_migracao":
            base_migracao()

        elif st.session_state["pagina_central"] == "pag_colaborador":
            colaborador()

        elif st.session_state["pagina_central"] == "pag_historico":
            historico()

        elif st.session_state["pagina_central"] == "pag_readea":
            painel_redea()
