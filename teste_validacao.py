from modulo3_caminhos import carregar_caminhos
import os

def validar_caminhos():
    print("🔍 Iniciando validação dos caminhos...")

    caminhos = carregar_caminhos()
    erros = []

    # Valida se as pastas existem
    for nome, pasta in caminhos.items():
        if not os.path.exists(pasta):
            erros.append(f"❌ Pasta '{nome}' não existe: {pasta}")
        else:
            print(f"✅ Pasta '{nome}' localizada: {pasta}")

    # Valida se há arquivos PDF na pasta de origem
    origem = caminhos.get('origem_pdf', '')
    pdfs = [arq for arq in os.listdir(origem) if arq.lower().endswith('.pdf')]

    if not pdfs:
        erros.append(f"⚠️ Nenhum arquivo PDF encontrado em: {origem}")
    else:
        print(f"📄 {len(pdfs)} arquivos PDF encontrados na pasta de origem.")

    # Resultado final
    if erros:
        print("\n🧯 Problemas encontrados:")
        for erro in erros:
            print(erro)
    else:
        print("\n✅ Tudo certo! Caminhos e arquivos estão prontos para uso.")

if __name__ == "__main__":
    validar_caminhos()