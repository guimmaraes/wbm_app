# ======================================================================================
# MÓDULO 4 – PROCESSA CADA PDF PARA EXCEL
# ======================================================================================

# ------------------------------- Importações necessárias -------------------------------
# Essas bibliotecas manipulam arquivos, diretórios, PDFs e planilhas conforme o fluxo original.
# ------------------------------------------------------------------------------------------------------
import os
import shutil
import pdfplumber
import pandas as pd
import re

# ------------------------------- Colunas esperadas na tabela extraída -------------------------------
# Garantimos que somente tabelas corretas sejam processadas.
# ------------------------------------------------------------------------------------------------------
COLUNAS_DESEJADAS = [
    "SKU", "PRODUTO", "NCM", "IPI", "VOLUME", "QTD.",
    "V. UND LÍQ.", "V. UND DESC.", "DESC. UND", "TOTAL"
]

# ------------------------------- Função principal que converte PDF para Excel -------------------------------
# Para cada arquivo .pdf na pasta origem, extrai as tabelas com estrutura esperada e salva em Excel.
# Move os PDFs processados para o histórico.
# ------------------------------------------------------------------------------------------------------
def converter_pdf_para_excel(caminhos):
    caminho_origem = caminhos['origem_pdf']
    caminho_destino_excel = caminhos['destino_excel']
    caminho_destino_pdf = caminhos['destino_pdf_historico']

    # Cria os diretórios de saída caso não existam
    os.makedirs(caminho_destino_excel, exist_ok=True)
    os.makedirs(caminho_destino_pdf, exist_ok=True)

    # Percorre os arquivos na pasta de origem
    for nome_arquivo in os.listdir(caminho_origem):
        if nome_arquivo.lower().endswith('.pdf'):
            caminho_pdf = os.path.join(caminho_origem, nome_arquivo)
            nome_base = nome_arquivo.replace("-budget.pdf", "")
            caminho_excel = os.path.join(caminho_destino_excel, f"{nome_base}.xlsx")

            try:
                tabelas_validas = []

                with pdfplumber.open(caminho_pdf) as pdf:
                    for pagina in pdf.pages:
                        tabelas = pagina.extract_tables()
                        for tabela in tabelas:
                            if tabela and len(tabela[0]) == 10:
                                df = pd.DataFrame(tabela[1:], columns=tabela[0])
                                if list(df.columns) == COLUNAS_DESEJADAS:
                                    tabelas_validas.append(df)

                if tabelas_validas:
                    df_final = pd.concat(tabelas_validas, ignore_index=True)

                    # Remove linhas com "..." simples ou entre parênteses
                    padrao_lixo = r"\.{3,}|\(\.{3,}\)"
                    df_final = df_final[
                        ~df_final.apply(lambda row: row.astype(str).str.contains(padrao_lixo, regex=True), axis=1)
                        .any(axis=1)
        ]


                    # Salva Excel final
                    df_final.to_excel(caminho_excel, index=False)
                    print(f"[OK] {nome_base}.xlsx gerado com sucesso.")

                    # Move PDF original para histórico
                    shutil.move(caminho_pdf, os.path.join(caminho_destino_pdf, nome_arquivo))
                else:
                    print(f"[AVISO] Nenhuma tabela válida encontrada em: {nome_arquivo}")

            except Exception as e:
                print(f"[ERRO] ao processar {nome_arquivo}: {e}")
# ======================================================================================