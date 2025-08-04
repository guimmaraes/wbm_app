import os
import yaml
from tkinter import Tk, filedialog

CONFIG_PATH = 'paths.yaml'

def selecionar_pasta(mensagem='Selecione a pasta desejada'):
    root = Tk()
    root.withdraw()  # esconde a janela principal
    caminho = filedialog.askdirectory(title=mensagem)
    root.destroy()
    return caminho

def configurar_caminhos():
    print("🔧 Configuração de caminhos iniciada...")
    caminhos = {
        'origem_pdf': selecionar_pasta('Selecione a pasta de PDFs de origem'),
        'destino_excel': selecionar_pasta('Selecione a pasta para os arquivos Excel'),
    }

    # Define o caminho do histórico dentro da pasta de origem
    caminhos['destino_pdf_historico'] = os.path.join(caminhos['origem_pdf'], 'historico')

    # Cria a pasta de histórico se não existir
    if not os.path.exists(caminhos['destino_pdf_historico']):
        os.makedirs(caminhos['destino_pdf_historico'])
        print(f"📁 Pasta criada: {caminhos['destino_pdf_historico']}")

    # Salva os caminhos no arquivo YAML
    with open(CONFIG_PATH, 'w') as arquivo:
        yaml.dump({'caminhos': caminhos}, arquivo, default_flow_style=False)
    print("✅ Caminhos salvos em paths.yaml")

def carregar_caminhos():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as arquivo:
            config = yaml.safe_load(arquivo)
        return config['paths']
    else:
        configurar_caminhos()
        return carregar_caminhos()

# Execução direta para testes
if __name__ == '__main__':
    caminhos = carregar_caminhos()
    print("🚀 Caminhos carregados:")
    for chave, valor in caminhos.items():
        print(f"  {chave}: {valor}")