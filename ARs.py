import pandas as pd
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Função para carregar o arquivo TXT existente ou criar um novo
def carregar_txt(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo, delimiter='\t')
    else:
        return pd.DataFrame(columns=['Pesquisa', 'Resultado'])

# Instala e inicia o serviço do ChromeDriver
servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

# Acessa a página desejada
navegador.get("https://listaars.iti.gov.br/list/sp")

# Lê os dados de entrada do arquivo TXT
dados_entrada = pd.read_csv('C:/Users/everton.souza/OneDrive - Certisign Certificadora Digital SA/Área de Trabalho/codigos/AutomacaoSelenium/Viagem.txt', sep='\t')
coluna_pesquisa = 'Pesquisa'  # Nome da coluna no TXT onde estão os dados a serem pesquisados

# Cria ou carrega o arquivo TXT para armazenar os resultados
arquivo_resultado = 'resultados_pesquisa.txt'
df_resultados = carregar_txt(arquivo_resultado)

# Loop pelos dados para fazer a pesquisa
for index, linha in dados_entrada.iterrows():
    dado_pesquisado = linha[coluna_pesquisa]  # Dado a ser pesquisado (CNPJ, nome, etc.)
    
    #print(f"Iniciando pesquisa para: {dado_pesquisado}")  # Mensagem de início de pesquisa

    try:
        # Espera o botão de busca estar clicável e clica
        botao_busca = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main-content"]/div[3]/div/div[1]/div[2]/button'))
        )
        botao_busca.click()
        
        # Espera um tempo extra para garantir que a página tenha carregado
        time.sleep(2)  # Espera 2 segundos

        # Espera o campo de pesquisa estar disponível e o localiza
        campo_pesquisa = WebDriverWait(navegador, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/div[3]/div/div[2]/form/div[1]/input'))
        )
        
        campo_pesquisa.clear()  # Limpa o campo antes de inserir o novo dado
        campo_pesquisa.send_keys(dado_pesquisado)

        # Espera um tempo para carregar a página (ajuste conforme necessário)
        time.sleep(5)  # Espera 2 segundos

        # Extrai os resultados da tabela
        resultados = []
        for i in range(2, 8):  # Colunas de 2 a 7
            xpath = f'//*[@id="main-content"]/div[3]/table/thead/tr/td[{i}]'
            try:
                resultado_element = WebDriverWait(navegador, 20).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                ).text
                resultados.append(resultado_element)
            except Exception as e:
                print(f"Erro ao obter o resultado da coluna {i}: {e}")
                resultados.append("Erro")

        resultado = ', '.join(resultados)  # Junta os resultados em uma string

    except Exception as e:
        print(f"Erro durante a pesquisa para '{dado_pesquisado}': {e}")
        resultado = "Erro ao obter resultado"  # Caso não consiga extrair o resultado
    
    print(f"Pesquisa: {dado_pesquisado}, Resultado: {resultado}")  # Resultado da pesquisa
    
    # Adiciona o resultado ao DataFrame
    df_resultado = pd.DataFrame({'Pesquisa': [dado_pesquisado], 'Resultado': [resultado]})
    df_resultados = pd.concat([df_resultados, df_resultado], ignore_index=True)

# Salva os resultados no arquivo TXT
df_resultados.to_csv(arquivo_resultado, index=False, sep='\t')

print("Resultados salvos no arquivo TXT com sucesso!")