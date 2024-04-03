from T_Coletor import *

if __name__ == "__main__":
    base_urls = ('https://www.iter.org/')
    crawler = WebCrawler(base_urls, max_depth=2)
    crawler.crawl(base_urls)
    crawler.save_inverted_index('index.json')
    crawler.driver.quit()


