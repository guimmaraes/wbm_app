# setup_inicial.py
import subprocess
import sys

def instalar_pacotes():
    pacotes = [
        "tabula-py",
        "pandas",
        "openpyxl",
        "jpype1",
        "pdfplumber",
        "workdays",
        "xlrd"
    ]

    print("🔧 Instalando dependências...")
    for pacote in pacotes:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pacote], check=True)
            print(f"✅ {pacote} instalado com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {pacote}: {e}")

if __name__ == "__main__":
    instalar_pacotes()