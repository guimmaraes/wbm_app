# ======================================================================================
# MÓDULO 6 – ANÁLISES E RELATÓRIOS
# ======================================================================================

import os
import pandas as pd

def gerar_relatorios_comerciais(caminhos):
    pasta_entrada = caminhos['destino_excel_etl']
    pasta_saida = caminhos['destino_analises']

    # Cria pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    for nome_arquivo in os.listdir(pasta_entrada):
        if nome_arquivo.lower().endswith('.xlsx'):
            caminho_entrada = os.path.join(pasta_entrada, nome_arquivo)
            caminho_saida = os.path.join(pasta_saida, f"RELATORIO_{nome_arquivo}")

            try:
                df = pd.read_excel(caminho_entrada)

                # --- Agrupamento por PRODUTO ---
                agrupado = df.groupby("PRODUTO").agg({
                    "QTD.": "sum",
                    "TOTAL LÍQ.": "sum",
                    "VALOR IPI": "sum",
                    "TOTAL C/ IPI": "sum"
                }).reset_index()

                # --- Classifica produtos por venda total ---
                agrupado = agrupado.sort_values(by="TOTAL C/ IPI", ascending=False)

                # --- Salva relatório ---
                agrupado.to_excel(caminho_saida, index=False)
                print(f"[OK] Relatório gerado: {caminho_saida}")

            except Exception as e:
                print(f"[ERRO] ao gerar relatório de {nome_arquivo}: {e}")