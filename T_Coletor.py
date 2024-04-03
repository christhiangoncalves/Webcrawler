from selenium import webdriver  # Importa o módulo webdriver do Selenium para automatizar a interação com navegadores web
from selenium.webdriver.common.by import By  # Importa a classe By do Selenium para encontrar elementos na página
from selenium.webdriver.firefox.options import Options  # Importa as opções do Firefox para configurar o driver
from bs4 import BeautifulSoup  # Importa BeautifulSoup para analisar HTML
import json  # Importa o módulo json para trabalhar com arquivos JSON
from collections import defaultdict  # Importa defaultdict para criar um dicionário com valores padrão

class HTMLParser:
    def __init__(self, html): # Inicializa o objeto HTMLParser com o HTML fornecido
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_text(self): # Retorna o texto extraído do HTML
        return self.soup.get_text()

class WebCrawler:
    def __init__(self, base_urls, max_depth): # Inicializa o WebCrawler com URLs de base e profundidade máxima de rastreamento
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.visited_urls = set()  # Conjunto para armazenar URLs visitadas
        self.inverted_index = defaultdict(list)  # Índice invertido para armazenar tokens e URLs
        self.driver = self._get_web_driver()  # Inicializa o driver do navegador

    def _get_web_driver(self): # Configura e retorna um driver do Firefox no modo headless
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        return driver

    def crawl(self, url, depth=0): # Método para rastrear a web a partir de uma URL inicial
        if depth > self.max_depth:  # Verifica se a profundidade máxima foi alcançada
            return

        if url in self.visited_urls:  # Verifica se a URL já foi visitada
            return

        try:
            self.driver.get(url)  # Visita a URL no navegador
            html = self.driver.page_source  # Obtém o HTML da página visitada
            parser = HTMLParser(html)  # Inicializa o parser HTML com o HTML obtido
            text = parser.get_text()  # Extrai o texto da página

            tokens = text.split()  # Divide o texto em tokens (palavras)

            # Atualiza o índice invertido com os tokens e a URL atual
            for token in tokens:
                self.inverted_index[token.lower()].append(url)

            self.visited_urls.add(url)  # Adiciona a URL à lista de URLs visitadas

            # Recupera todos os links na página e os visita recursivamente se forem URLs válidas
            for link in self.driver.find_elements(By.TAG_NAME, 'a'):
                next_url = link.get_attribute('href')  # Obtém o atributo href do link
                # Verifica se o próximo URL começa com uma das URLs de base
                if next_url and any(next_url.startswith(base_url) for base_url in self.base_urls):
                    self.crawl(next_url, depth + 1)  # Chama recursivamente o método crawl para o próximo URL
                    
        except Exception as e:
            # Em caso de erro, imprime a mensagem de erro
            print(f"Erro ao rastrear {url}: {e}")

    def save_inverted_index(self, output_file):
        # Salva o índice invertido em um arquivo JSON
        with open(output_file, 'w') as f:
            json.dump(self.inverted_index, f, indent=2)
