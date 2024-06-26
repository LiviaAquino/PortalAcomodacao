import streamlit as st
import pandas as pd
from utilidades import *


def painel_redea():
    st.markdown("##### Painel :green[REDEA]")
    with st.expander("Base Controle De Reparo"):
        controle_de_reparo = st.file_uploader(
            "Anexar Base Controle De Reparo",
            type=["xlsx"],
            key="unique_key_2",
        )

    if controle_de_reparo is not None:
        df_reparos = pd.read_excel(
            controle_de_reparo, engine="openpyxl", sheet_name="Resultado"
        )

        df_redea = pd.DataFrame(
            {
                "PROTOCOLO": df_reparos["PROTOCOLO"].astype(str),
                "PSR": df_reparos["PSR"],
                "REGIONAL": df_reparos["REGIONAL"],
                "UF": df_reparos["UF"],
                "CIRCUITO": df_reparos["CIRCUITO_BD"],
                "CLIENTE": df_reparos["CLIENTE"],
                "POSTO": df_reparos["POSTO"],
                "FAIXA": df_reparos["FAIXA_POSTO"],
            }
        )

        tab1, tab2 = st.tabs(["Base", "Base Tratada"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            
            psr, df_psr = filtro(df_redea, 'PSR',col1,"PSR")
            regional, df_regional = filtro(df_redea, 'REGIONAL',col2,"REGIONAL")
            faixa, df_faixa = filtro(df_redea, 'FAIXA',col3,"Faixa")
            df_atual = df_redea
            if psr != "Selecione":
                df_atual = df_psr
            if regional != "Selecione":
                df_atual = df_regional
            if faixa != "Selecione":
                df_atual = df_faixa
            
            
            st.dataframe(df_atual, hide_index=True)

        with tab2:
            
            contagem = df_redea.groupby(['PSR', 'REGIONAL', 'UF']).size()

            df_tratada = contagem.reset_index(name='TOTAL')
            
            psrs = list(df_tratada['PSR'].unique())
            psrs.append("Selecione")
            psr = st.selectbox('PSR', psrs, index=(len(psrs) - 1), key="base_tratada")
            df_filtrado = df_tratada[df_tratada['PSR'] == psr]
            
            df_atual = df_tratada
            if psr != "Selecione":
                df_atual = df_filtrado
            
            col1, col2 = st.columns(2)
            col1.dataframe(df_atual,width=600, hide_index=True)
            col2.warning('Total corresponde a quantidade de registro que a UF tem na tabela.', icon="⚠️")


def filtro(df, coluna_df, col_pag, nome_filtro):
    valores = list(df[coluna_df].unique())
    valores.append("Selecione")
    valor = col_pag.selectbox(nome_filtro, valores, index=(len(valores) - 1))
    df_filtrado = df[df[coluna_df] == valor]
    return valor, df_filtrado