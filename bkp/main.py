# ======================================================================================
# WBM App – Ponto de entrada principal
# ======================================================================================

# ------------------------------- Módulo 1 – Carregamento de bibliotecas -------------------------------
import os
import shutil
import pdfplumber
import pandas as pd
import re
import requests
import io
from datetime import datetime, timedelta
from workdays import workday  # cálculo de dias úteis

# ------------------------------- Módulo 2 – Caminhos -------------------------------
from modulo3_caminhos import carregar_caminhos
caminhos = carregar_caminhos()

print("📂 Caminhos configurados:")
for nome, pasta in caminhos.items():
    print(f"  {nome}: {pasta}")

# ------------------------------- Módulo 3 – Conversão PDF para Excel -------------------------------
from modulo4_conversao import converter_pdf_para_excel
converter_pdf_para_excel(caminhos)

# ------------------------------- Módulo 4 – ETL Comercial -------------------------------
from modulo5_etl_comercial import etl_dados_comerciais
etl_dados_comerciais()

# ------------------------------- Módulo 5 – Análises e Relatórios -------------------------------
from modulo6_analises import gerar_relatorios_comerciais
gerar_relatorios_comerciais(caminhos)