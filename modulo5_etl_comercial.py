import os
import re
import pandas as pd
from datetime import datetime, timedelta
import yaml

def entrada_float(msg):
    while True:
        valor = input(msg).replace(',', '.')
        try:
            return float(valor)
        except ValueError:
            print("❌ Valor inválido. Tente novamente (ex: 1.35).")

def etl_dados_comerciais():
    # ------------------------------ Configurações e caminhos ------------------------------
    with open('paths.yaml', 'r') as f:
        config = yaml.safe_load(f)['paths']

    pasta_excel     = config['destino_excel_etl']
    data_cotacao    = datetime.today().strftime('%d/%m/%Y')
    data_arquivo    = datetime.today().strftime('%Y-%m-%d')
    padrao_remocao  = re.compile(r"\.{3,}|\(\.\.\.\)|…")

    url_clientes    = config['url_clientes']
    url_mc          = config['url_mc']
    url_condicoes   = config['url_condicoes']

    # ------------------------------ Seleção de arquivo XLSX ------------------------------
    arquivos_disponiveis = [f for f in os.listdir(pasta_excel) if f.lower().endswith('xlsx') and not f.startswith('ETL-')]

    print("\n📂 Arquivos disponíveis para processamento:")
    for i, nome in enumerate(arquivos_disponiveis):
        print(f"{i + 1}. {nome}")
    escolha = int(input("Digite o número do arquivo desejado: ")) - 1
    nome_arquivo = arquivos_disponiveis[escolha]
    caminho_arquivo = os.path.join(pasta_excel, nome_arquivo)

    # ------------------------------ Início do processamento ------------------------------
    try:
        df = pd.read_excel(caminho_arquivo)
        nome_base = os.path.splitext(nome_arquivo)[0]

        df = df[~df.apply(lambda row: row.astype(str).str.contains(padrao_remocao), axis=1).any(axis=1)]

        df["TOTAL"] = df["TOTAL"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["TOTAL"] = pd.to_numeric(df["TOTAL"], errors="coerce")

        df["NF 5,84%"] = (df["TOTAL"] * 5.84 / 100).round(2)
        df["TOT1"]     = (df["TOTAL"] + df["NF 5,84%"]).round(2)

        df.insert(0, "ARQUIVO", nome_base)
        df.insert(1, "DATA-COTACAO", data_cotacao)

        # ------------------------------ CLIENTE + CNPJ ------------------------------
        df_clientes = pd.read_csv(url_clientes)
        clientes = df_clientes['Nome'].dropna().tolist()

        print("\n📋 Selecione um cliente:")
        for i, nome in enumerate(clientes):
            print(f"{i + 1}. {nome}")
        escolha = int(input("Número do cliente: ")) - 1
        cliente_escolhido = clientes[escolha]
        print(f"✅ Cliente selecionado: {cliente_escolhido}")

        linha_cliente = df_clientes[df_clientes["Nome"].str.lower() == cliente_escolhido.lower()]
        cnpj = linha_cliente.iloc[0]["CNPJ"] if not linha_cliente.empty else input("⚠️ Informe o CNPJ: ").strip()

        df.insert(2, "CLIENTE", cliente_escolhido)
        df.insert(3, "CNPJ", cnpj)

        # ------------------------------ MARK UP ------------------------------
        aplicar_todos = input("Deseja aplicar MC único para todas as linhas? (S/N): ").strip().upper()
        if aplicar_todos == "S":
            mc_valor = entrada_float("➡️ MC único: ")
            df["MC"] = mc_valor
        else:
            mcs = []
            for idx, linha in df.iterrows():
                prod = str(linha.get("PRODUTO", f"Linha {idx}"))
                mc = entrada_float(f"➡️ MC para \"{prod}\": ")
                mcs.append(mc)
            df["MC"] = mcs

        df["TOT2"] = (df["TOT1"] * df["MC"]).round(2)

        # ------------------------------ DESCONTO / VALIDADE / OBSERVAÇÕES ------------------------------
        df["DESCONTO"]     = 0.00
        df["TOTAL-GERAL"]  = df["TOT2"]
        validade           = (datetime.strptime(data_cotacao, "%d/%m/%Y") + timedelta(days=14)).strftime("%d-%m-%Y")
        df["VALIDADE"]     = validade
        df["OBSERVAÇÕES"]  = ""

        aplicar_desconto = input("❓ Deseja aplicar desconto? (S/N): ").strip().upper()
        if aplicar_desconto == "S":
            desconto_pct = entrada_float("🔢 Informe % de desconto: ")
            df["DESCONTO"]     = desconto_pct
            df["TOTAL-GERAL"]  = (df["TOT2"] * (1 - desconto_pct / 100)).round(2)

        incluir_obs = input("📝 Inserir observações? (S/N): ").strip().upper()
        if incluir_obs == "S":
            obs = input("✏️ Digite as observações: ").strip()
            df["OBSERVAÇÕES"] = obs

        # ------------------------------ CONDIÇÕES DE PAGAMENTO ------------------------------
        try:
            df_condicoes  = pd.read_csv(url_condicoes)
            for col in ['MIN', 'MAX']:
                df_condicoes[col] = (
                    df_condicoes[col].astype(str)
                    .str.replace(r"[^\d,\.]", "", regex=True)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .astype(float)
                )

            total_geral_sum = df["TOTAL-GERAL"].sum()
            linha_cond = df_condicoes[
                (df_condicoes["MIN"] <= total_geral_sum) & (df_condicoes["MAX"] >= total_geral_sum)
            ]

            if not linha_cond.empty:
                cond_sintese = linha_cond.iloc[0]["SINTESE"]
                cond_cliente = linha_cond.iloc[0]["CLIENTE"]
                print(f"\n📌 Condição encontrada:")
                print(f"🔹 Síntese: {cond_sintese}")
                print(f"🔹 Cliente: {cond_cliente}")

                usar_padrao = input("Usar essa condição? (S/N): ").strip().upper()
                if usar_padrao != "S":
                    cond_sintese = input("✏️ Nova condição - Síntese: ").strip()
                    cond_cliente = input("✏️ Nova condição - Cliente: ").strip()
            else:
                print("⚠️ Nenhuma condição encontrada.")
                cond_sintese = input("✏️ Condição - Síntese: ").strip()
                cond_cliente = input("✏️ Condição - Cliente: ").strip()

            df["CONDIÇÃO-SINTESE"] = cond_sintese
            df["CONDIÇÃO-CLIENTE"] = cond_cliente

        except Exception as e:
            print(f"[ERRO] ao buscar condição: {e}")
            df["CONDIÇÃO-SINTESE"] = "ERRO"
            df["CONDIÇÃO-CLIENTE"] = "ERRO"

        # ------------------------------ Limpeza de PRODUTO + Salvamento ------------------------------
        df['PRODUTO'] = df['PRODUTO'].str.replace(r'1GR|1KG', '', regex=True).str.strip()

        nome_curto = ' '.join(cliente_escolhido.split()[:2])
        nome_curto_sanitizado = re.sub(r'[\\/*?:"<>|]', '', nome_curto)
        novo_nome = f"{nome_curto_sanitizado}-{nome_base}-{data_arquivo}.xlsx"
        caminho_saida = os.path.join(pasta_excel, novo_nome)
        df.to_excel(caminho_saida, index=False)
        # ------------------------------ Finalização ------------------------------

        print(f"\n✅ [ETL OK] {novo_nome} salvo com cliente {nome_curto}.")
    except Exception as e:
        print(f"[ERRO] ao processar {nome_arquivo}: {e}")