import streamlit as st
from utilidades import *
from datetime import datetime, timedelta

hoje = datetime.now()
# Pegar o último dia do mês
proximo_mes = hoje.replace(day=28) + timedelta(
    days=4
)  # Este será o primeiro dia do próximo mês
ultimo_dia_do_mes = proximo_mes - timedelta(days=proximo_mes.day)

colunas = [
    "Em execução",
    "Migração Concluída",
    "Cotar Terceiros",
    "Aguardando Abertura OS",
    "Migração Suspensa",
    "Em análise",
    "Impedimento Clarify",
    "Aprovar Contratação OEMP",
    "Histórico/ Em retirada",
]


def colaborador():
    df = st.session_state["dados_excel"]
    df_metas = st.session_state["dados_metas"]
    st.markdown("##### :green[Colaborador]")

    with st.expander("Filtro", expanded=True):
        col_colaborador, col_data = st.columns(2)
        colaborador, df_colaborador = _filtro_colaborador(df, col_colaborador)
        data_conclusao = col_data.selectbox(
            "Migração concluída Mês", ["01/2024", "02/2024", "03/2024", "04/2024"]
        )
    valor_previsao = 0
    if colaborador == "Selecione":
        df_atual = df
    else:
        df_atual = df_colaborador

    total_filtro_status = len(df_atual["STATUS DETALHADO"])

    uf_metas = st.empty()
    total_metas = _filtro_metas_total(df_metas, colaborador)
    status_em_execução = _filtro_status(df_atual, colunas[0].upper())
    status_migracao_concluida = _filtro_status(df_atual, colunas[1].upper())
    df_status = df_atual[(df_atual["STATUS DETALHADO"] == "AGUARDANDO ABERTURA OS")]

    if data_conclusao == "Selecione":
        valor_migracao_mes = 0
    else:
        valor = status_migracao_concluida[
            status_migracao_concluida["MÊS CONCLUSÃO"] == data_conclusao
        ]
        if valor.empty:
            valor_migracao_mes = 0
        else:
            valor_migracao_mes = int(valor["MÊS CONCLUSÃO"].value_counts().iloc[0])
    if data_conclusao[:2] == hoje.strftime("%m"):
        valor_previsao = int((valor_migracao_mes / hoje.day) * ultimo_dia_do_mes.day)

    meta_mes = {
        "01/2024": 1000,
        "02/2024": 1000,
        "03/2024": 1000,
        "04/2024": 1000,
    }
    if uf_metas.empty:
        if colaborador == "Selecione":

            valor_meta = meta_mes[data_conclusao]
        else:
            valor_meta = total_metas
    else:
        valor_meta = int(uf_metas.iloc[0])

    container_principal(
        [
            "Total",
            "Em execução",
            "Meta Acumulada",
            "Migração concluída Acumulada",
            "Meta Mês",
            "Migração concluída Mês",
            "Previsão Mês",
        ],
        [
            total_filtro_status,
            len(status_em_execução),
            sum(meta_mes.values()),
            len(status_migracao_concluida),
            valor_meta,
            valor_migracao_mes,
            valor_previsao,
        ],
        ["orange", "red", "blue", "green", "blue", "green", "blue"],
    )

    detalhes, controle_de_reparo, tabela_filtrada = st.tabs(
        ["Detalhes", "Controle De Reparo", "Tabela"]
    )
    with detalhes:
        contagem_un, contagem_operacao = _contagem_os(df_status)
        col1, col2 = st.columns([0.8, 0.4])
        _container_status_detalhado(
            df_atual,
            col1,
            colunas,
        )
        try:
            if contagem_operacao.empty:
                valor = 0
            else:
                valor = str(contagem_operacao.iloc[0])
            container_aguard_os_detalhado(
                col2,
                ["UN", "OPERAÇÃO"],
                [
                    str(contagem_un.iloc[0]),
                    valor,
                ],
            )
        except:
            pass

    with controle_de_reparo:
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
            col1, col2, col3 = st.columns(3)

            if colaborador == "Selecione":
                contem = df_reparos[df_reparos["Migração_2024"] == "S"][
                    "Migração_2024"
                ].value_counts()
                nao_contem = df_reparos[df_reparos["Migração_2024"] == "N"][
                    "Migração_2024"
                ].value_counts()
                _controle_de_reparo(col1, col2, col3, nao_contem, contem)
            else:
                df_atual_reparos = df_reparos[df_reparos["COLABORADOR"] == colaborador]

                contem = df_atual_reparos[df_atual_reparos["Migração_2024"] == "S"][
                    "Migração_2024"
                ].value_counts()
                nao_contem = df_atual_reparos[df_atual_reparos["Migração_2024"] == "N"][
                    "Migração_2024"
                ].value_counts()

                # Criando um dataframe
                filial = df_reparos[df_reparos["COLABORADOR"] == colaborador][
                    "UF"
                ].unique()

                df = pd.DataFrame(
                    {
                        "Filial": sorted(filial),
                    }
                )
                df["Não Contém"] = df["Filial"].apply(
                    lambda x: count_contem(x, df_atual_reparos, "N")
                )

                df["Contém"] = df["Filial"].apply(
                    lambda x: count_contem(x, df_atual_reparos, "S")
                )

                df["Total"] = df["Contém"] + df["Não Contém"]
                df["Não Contém"] = df["Não Contém"].astype(int)
                df["Contém"] = df["Contém"].astype(int)
                df["Total"] = df["Total"].astype(int)

                # Adiciona uma nova linha ao dataframe com os valores totais
                df.loc["Total:"] = [
                    "Total",
                    df["Não Contém"].sum(),
                    df["Contém"].sum(),
                    df["Total"].sum(),
                ]

                # Função para colorir a última linha
                def color_last_row(val):
                    color = "blue" if val.name == df.index[-1] else "black"
                    return ["color: %s" % color] * len(val)

                styled_df = df.style.apply(color_last_row, axis=1)
                # Exibe o dataframe no Streamlit
                st.dataframe(styled_df, hide_index=True)

                df_tabela2_faixa = pd.DataFrame(
                    {
                        "UF": sorted(
                            df_reparos[df_reparos["COLABORADOR"] == colaborador][
                                "UF"
                            ].unique()
                        )
                    }
                )

                df_tabela2_faixa["Até 7 dias"] = df_tabela2_faixa["UF"].apply(
                    lambda x: count_faixa(x, df_atual_reparos, "Até 7 dias")
                )

                df_tabela2_faixa["De 8 a 15 dias"] = df_tabela2_faixa["UF"].apply(
                    lambda x: count_faixa(x, df_atual_reparos, "De 8 a 15 dias")
                )

                df_tabela2_faixa["De 16 a 30 dias"] = df_tabela2_faixa["UF"].apply(
                    lambda x: count_faixa(x, df_atual_reparos, "De 16 a 30 dias")
                )

                df_tabela2_faixa["De 31 a 60 dias"] = df_tabela2_faixa["UF"].apply(
                    lambda x: count_faixa(x, df_atual_reparos, "De 31 a 60 dias")
                )

                df_tabela2_faixa["Acima de 60 dias"] = df_tabela2_faixa["UF"].apply(
                    lambda x: count_faixa(x, df_atual_reparos, "Acima de 60 dias")
                )

                df_tabela2_faixa["Total"] = (
                    df_tabela2_faixa["Até 7 dias"]
                    + df_tabela2_faixa["De 8 a 15 dias"]
                    + df_tabela2_faixa["De 16 a 30 dias"]
                    + df_tabela2_faixa["De 31 a 60 dias"]
                    + df_tabela2_faixa["Acima de 60 dias"]
                )
                df_tabela2_faixa.loc["Total:"] = [
                    "Total",
                    df_tabela2_faixa["Até 7 dias"].sum(),
                    df_tabela2_faixa["De 8 a 15 dias"].sum(),
                    df_tabela2_faixa["De 16 a 30 dias"].sum(),
                    df_tabela2_faixa["De 31 a 60 dias"].sum(),
                    df_tabela2_faixa["Acima de 60 dias"].sum(),
                    df_tabela2_faixa["Total"].sum(),
                ]
                styled_df_faixa = df_tabela2_faixa.style.apply(color_last_row, axis=1)

                # Função para colorir a última linha
                def color_last_row(val):
                    color = "blue" if val.name == df.index[-1] else "black"
                    return ["color: %s" % color] * len(val)

                styled_df = df.style.apply(color_last_row, axis=1)

                # faixas = list(
                #     df_reparos[df_reparos["COLABORADOR"] == colaborador][
                #         "FAIXA_POSTO"
                #     ].unique()
                # )
                # faixas.append("Selecione")
                # faixa = st.selectbox("FAIXA", faixas, index=(len(faixas) - 1))

                # if faixa == "Selecione":
                #     df_atual_tabela2 = df_tabela2_faixa
                # else:
                #     df_atual_tabela2 = df_tabela2_faixa[
                #         df_tabela2_faixa["FAIXA_POSTO"] == faixa
                #     ]
                st.dataframe(styled_df_faixa, hide_index=True)

    with tabela_filtrada:

        base_mes_meta = _base_mes_meta(df_atual, valor_meta)

        if colaborador != "Selecione":
            col1, col_filtro, col3, col4 = st.columns([0.2, 0.2, 0.4, 0.4])
            mes = col1.selectbox(
                "Mês", ["Selecione", "01/2024", "02/2024", "03/2024", "04/2024"]
            )

            df_mes = df_colaborador[df_colaborador["MÊS CONCLUSÃO"] == mes]
            col1, col2 = st.columns(2)
            col1.dataframe(
                base_mes_meta,
                hide_index=True,
            )
            df_metas_filtro_colaborador = df_metas[
                df_metas["Colaborador"] == colaborador.title()
            ]
            if mes != "Selecione":
                farol = col_filtro.selectbox("Farol", ["Selecione", "✅", "❌"])
                tabela_metas_colaborador(
                    df_mes, df_metas_filtro_colaborador, col2, farol
                )
        else:
            st.info("Selecione um colaborador")


def _controle_de_reparo(col1, col2, col3, nao_contem, contem):

    if contem.empty:
        contem_tratado = 0
    else:
        contem_tratado = int(contem.iloc[0])

    if nao_contem.empty:
        nao_contem_tratado = 0
    else:
        nao_contem_tratado = int(nao_contem.iloc[0])

    with col1.container(border=True):
        st.markdown("Não Contem na base de migração")
        st.markdown(f"## :red[{nao_contem_tratado}]")

    with col2.container(border=True):
        st.markdown("Contem na base de migração")
        st.markdown(f"## :green[{contem_tratado}]")

    with col3.container(border=True):
        st.markdown("Total")
        st.markdown(f"## :blue[{contem_tratado + nao_contem_tratado}]")


def _contagem_os(df_status):
    contagem_area_responsavel_un = df_status["ÁREA RESPONSÁVEL"][
        df_status["ÁREA RESPONSÁVEL"] == "UN"
    ].value_counts()

    contagem_area_responsavel_operacao = df_status["ÁREA RESPONSÁVEL"][
        df_status["ÁREA RESPONSÁVEL"] == "OPERAÇÃO"
    ].value_counts()
    return contagem_area_responsavel_un, contagem_area_responsavel_operacao


def container_principal(titulos, valores, cores):
    col1, col2, col3, col4, col5, col6, col7 = st.columns(
        [0.35, 0.35, 0.4, 0.5, 0.3, 0.38, 0.35]
    )

    # Loop através das colunass, títulos e valores
    for col, titulo, valor, cor in zip(
        [col1, col2, col3, col4, col5, col6, col7], titulos, valores, cores
    ):
        with col.container(border=True):
            st.markdown(f"{titulo.title()}")
            st.write(f"### :{cor}[{str(valor)}]")


def _container_status_detalhado(df, col, titulos):

    with col.container():
        # Cria três linhas de colunass
        for i in range(3):
            cols = st.columns(3)

            # Loop através das colunass, títulos e valores
            for j in range(3):
                index = i * 3 + j
                with cols[j].container(border=True):
                    st.markdown(f"{titulos[index].title()}")

                    df_filtro_status = df[
                        df["STATUS DETALHADO"] == colunas[index].upper()
                    ]
                    st.write(f"#### :black[{len(df_filtro_status)}]")


def container_aguard_os_detalhado(coluna, titulos, valores):
    with coluna.container():
        col1, col2 = st.columns(2)
        # Loop através das colunass, títulos e valores
        for col, titulo, valor in zip([col1, col2], titulos, valores):
            with col.container(border=True):
                st.markdown("Aguardando Abertura OS")
                st.markdown(f"{titulo}")
                st.write(f"### :black[{str(valor)}]")


def _filtro_colaborador(df, colunas):
    colaboradores = list(df["RESPONSÁVEL NOVA OI"].unique())
    colaboradores.append("Selecione")
    colaboradores.sort()

    colaborador = colunas.selectbox(
        "Colaborador", colaboradores, index=(len(colaboradores) - 1)
    )
    df_colaborador = df[df["RESPONSÁVEL NOVA OI"] == str(colaborador).upper()]

    return colaborador, df_colaborador


def _filtro_status(df, colunas):
    df_filtro_status = df[df["STATUS DETALHADO"] == colunas]
    return df_filtro_status


def _filtro_metas_total(df_metas, colaborador):
    df_filtro = df_metas[df_metas["Colaborador"] == colaborador.title()]["Meta"].sum()
    return df_filtro


def _base_mes_meta(df_atual, valor_meta):
    status = df_atual[df_atual["STATUS DETALHADO"] == "MIGRAÇÃO CONCLUÍDA"]

    base = status.groupby("MÊS CONCLUSÃO").size().reset_index(name="Migração Concluída")
    base["Meta Mensal"] = valor_meta
    base["Farol"] = base["Migração Concluída"].apply(
        lambda x: "✅" if x >= valor_meta else "❌"
    )
    base["Porcentagem"] = ((base["Migração Concluída"] / valor_meta) * 100).round(
        2
    ).astype(str) + " % "
    base = base.sort_values(["MÊS CONCLUSÃO", "Migração Concluída"])
    return base


def count_contem(filial, df_atual_reparos, letra):
    # Conta o número de "S" em "Migração_2024" para cada "Filial"
    return df_atual_reparos[
        (df_atual_reparos["UF"] == filial)
        & (df_atual_reparos["Migração_2024"] == letra)
    ]["Migração_2024"].count()


def count_faixa(filial, df, faixa):
    return df[(df["UF"] == filial) & (df["FAIXA_POSTO"] == faixa)][
        "FAIXA_POSTO"
    ].count()
