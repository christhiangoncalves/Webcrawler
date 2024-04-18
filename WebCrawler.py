from selenium import webdriver  # Biblioteca para interagir com navegadores web
from selenium.webdriver.common.by import By  # Utilizada para localizar elementos em páginas web
from selenium.webdriver.firefox.options import Options  # Opções para o navegador Firefox
from bs4 import BeautifulSoup  # Biblioteca para fazer parsing de HTML e XML
import json  # Biblioteca para manipulação de JSON
from collections import defaultdict  # Dicionário com valores padrão
import nltk  # Biblioteca para processamento de linguagem natural
from nltk.corpus import stopwords  # Palavras irrelevantes em textos

class HTMLParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

class InvertedIndexer:
    def __init__(self):
        self.inverted_index = defaultdict(lambda: defaultdict(int))  # Dicionário aninhado
        self.stopwords = set(stopwords.words('portuguese'))  # Palavras irrelevantes em português

    def index(self, url, text):
        # Tokenização e limpeza do texto
        tokens = text.split()
        tokens = [token.lower() for token in tokens if token.lower() not in self.stopwords]

        # Indexando palavras
        for token in tokens:
            self.inverted_index[token][url] += 1

    # Salvando o índice invertido em um arquivo JSON
    def save(self, output_file):
        inverted_index_json = {key: dict(value) for key, value in self.inverted_index.items()}
        with open(output_file, 'w') as f:
            json.dump(inverted_index_json, f, indent=2)


class WebCrawler:
    def __init__(self, base_urls, max_depth):
        self.base_urls = base_urls  # URLs base para iniciar o crawling
        self.max_depth = max_depth  # Profundidade máxima de navegação
        self.visited_urls = set()  # URLs já visitadas
        self.driver = self._get_web_driver()  # Inicializando o driver do navegador
        self.parser = HTMLParser('')  # Inicializando o parser HTML
        self.indexer = InvertedIndexer()  # Inicializando o indexador

    # Configurando o driver do navegador
    def _get_web_driver(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        return driver

    # Função para  coletar informaçõe
    def crawl(self, url, depth=0):
        # Condição de parada
        if depth > self.max_depth:
            return

        # Verificando se a URL já foi visitada
        if url in self.visited_urls:
            return

        try:
            # Acessando a página e obtendo o HTML
            self.driver.get(url)
            html = self.driver.page_source
            self.parser = HTMLParser(html)
            text = self.parser.soup.get_text()

            # Indexando o texto da página
            self.indexer.index(url, text)
            self.visited_urls.add(url)

            # Encontrando links na página e continuando o crawling
            for link in self.driver.find_elements(By.TAG_NAME, 'a'):
                next_url = link.get_attribute('href')
                if next_url and any(next_url.startswith(base_url) for base_url in self.base_urls):
                    self.crawl(next_url, depth + 1)
                    
        except Exception as e:
            print(f"Erro ao rastrear {url}: {e}")

    # Salvando o índice invertido
    def save_index(self, output_file):
        self.indexer.save(output_file)

#
class Buscador:
    def __init__(self, index_file):
        with open(index_file, "r") as file:
            self.inverted_index = json.load(file)
        self.stopwords = set(stopwords.words('portuguese'))

    # Função para realizar a busca
    def search(self, query):
        query_tokens = nltk.word_tokenize(query.lower())  # Tokenização da consulta
        relevant_links = []

        # Buscando palavras-chave no índice invertido
        for token in query_tokens:
            if token not in self.stopwords:
                for chave in self.inverted_index.keys():
                    if token in chave:
                        for url, count in self.inverted_index[chave].items():
                            relevant_links.append({'url': url, 'value': count})
                        break

        # Ordenando os resultados por frequência
        sorted_links = sorted(relevant_links, key=lambda x: x['value'], reverse=True)
        return sorted_links


if __name__ == "__main__":
    base_urls = ('https://www.infomoney.com.br/',)
    crawler = WebCrawler(base_urls, max_depth=5)  # Inicializando o crawler
    crawler.crawl(base_urls[0])  # Iniciando o crawling
    crawler.save_index('index.json')  # Salvando o índice invertido
    crawler.driver.quit()  # Fechando o driver do navegador

    # Loop para realizar buscas
    while True:
        query = input("\nO que você deseja pesquisar (digite 'exit' para sair)? ")
        if query.lower() == 'exit':
            break

        buscador = Buscador("index.json")  # Inicializando o buscador
        results = buscador.search(query)  # Realizando a busca

        # Exibindo os resultados
        for result in results:
            print(f"Link: {result['url']}, \nFrequência: {result['value']} \n")
