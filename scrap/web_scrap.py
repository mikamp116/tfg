from newspaper import Article
from summa.summarizer import summarize
import selenium.webdriver as wd
import re
from bs4 import BeautifulSoup as Bs
import requests


class News:
    """Class for each news article"""

    def __init__(self, title, authors, description, text, summary, summary_, is_valid, site, generator):
        self.title = title
        self.authors = authors
        self.description = description
        self.text = text
        self.summary = summary
        self.summary_ = summary_
        self.is_valid = is_valid
        self.site = site
        self.generator = generator


class Wiki:
    """Class for each wikipedia page"""

    def __init__(self, title, description, text):
        self.title = title
        self.description = description
        self.text = text


def get_news_data(url, num_words=None):
    """Retrieves information about the news article"""
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    metadata = article.meta_data
    if num_words is None:
        summary_ = summarize(article.text)
    else:
        summary_ = summarize(article.text, words=num_words)
    authors = [metadata['author']]
    for author in article.authors:
        if author not in authors:
            authors.append(author)

    return News(article.title, authors, metadata['description'], article.text, article.summary, summary_,
                article.is_valid_body() and article.is_valid_url(), metadata['og']['site_name'], metadata['generator'])


def get_google_results(keywords, site):
    """Retrieves a list with the 10 first results of Google searching the given keywords in the specified site"""
    browser = wd.Chrome('/home/mikamp116/Downloads/chromedriver')
    url = 'https://www.google.com'
    browser.get(url)

    search_box = browser.find_element_by_name('q')
    search = keywords + ' site:' + site
    search_box.send_keys(search)
    search_box.submit()

    results = browser.find_elements_by_xpath("//div[@class='g']//div[@class='r']//a[not(@class)]")
    links = [result.get_attribute('href') for result in results]
    browser.close()
    return links


def get_wikipedia_results(entity, num_words=None, hops=0):
    url = 'https://en.wikipedia.org/wiki/' + entity
    html = requests.get(url,
        headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'})

    content = Bs(html.text).find(class_='mw-parser-output')
    text = ''

    if hops > 0:
        links = []
        for child in content.children:
            if child.name == 'p':
                text += child.get_text()
                links.append(child.find_all('a'))

        text += get_wikipedia_results_recursive(hops - 1, links)
    else:
        for child in content.children:
            if child.name == 'p':
                text += child.get_text()

    # num_parragraphs = len(content.findAll('p'))
    #
    # actual_p = content.find('p')
    # text = actual_p.get_text()
    # if hops > 0:
    #     links = actual_p.find_all('a')
    #     for i in range(num_parragraphs-1):
    #         actual_p = actual_p.find_next_sibling("p")
    #         text += actual_p.get_text()
    #         links.append(actual_p.find_all('a'))
    #
    #     text += get_wikipedia_results_recursive(hops - 1, links)
    # else:
    #     for i in range(num_parragraphs-1):
    #         actual_p = actual_p.find_next_sibling("p")
    #         text += actual_p.get_text()

    # results = [News(article.title, None, metadata['description'], re.sub("[\[].*[\]]", "", article.text),
    #                 article.summary, summary_, None, None, None)]

    return text


#     Hay que hacer una plantilla para Wikipedia en la que se cojan el texto únicamente y se excluyan elementos como
# las notas al pie de foto o las referencias. La extracción de triplas también debe devolver las entidades
#

def get_wikipedia_results_recursive(hops, urls):

    text = ''

    if hops > 0:
        links = []
        for link_list in urls:
            for link in link_list:
                url = 'https://en.wikipedia.org/' + link['href']
                html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                                'Gecko/20100101 Firefox/74.0'})

                content = Bs(html.text).find(class_='mw-parser-output')

                for child in content.children:
                    if child.name == 'p':
                        text += child.get_text()
                        links.append(child.find_all('a'))

        text += get_wikipedia_results_recursive(hops - 1, links)
    else:
        for link_list in urls:
            for link in link_list:
                url = 'https://en.wikipedia.org/' + link['href']
                html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                                'Gecko/20100101 Firefox/74.0'})

                content = Bs(html.text).find(class_='mw-parser-output')

                for child in content.children:
                    if child.name == 'p':
                        text += child.get_text()

    # text = ''
    #
    # if hops > 0:
    #     links = []
    #
    #     for link in urls:
    #         url = 'https://en.wikipedia.org/' + link['href']
    #         html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
    #                                                         'Gecko/20100101 Firefox/74.0'})
    #
    #         content = Bs(html.text).find(class_='mw-parser-output')
    #         pes = content.findAll('p')
    #         num_parragraphs = len(pes)
    #
    #         actual_p = content.find('p')
    #         text += actual_p.get_text()
    #         links.append(actual_p.find_all('a'))
    #         for i in range(num_parragraphs - 1):
    #             actual_p = actual_p.find_next_sibling("p")
    #             text += actual_p.get_text()
    #             links.append(actual_p.find_all('a'))
    #
    #     text += get_wikipedia_results_recursive(hops - 1, links)
    #
    # else:
    #     for link in urls:
    #         url = 'https://en.wikipedia.org/' + link['href']
    #         html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
    #                                                         'Gecko/20100101 Firefox/74.0'})
    #
    #         content = Bs(html.text).find(class_='mw-parser-output')
    #         pes = content.findAll('p')
    #         num_parragraphs = len(pes)
    #
    #         actual_p = content.find('p')
    #         text += actual_p.get_text()
    #         for i in range(num_parragraphs - 1):
    #             actual_p = actual_p.find_next_sibling("p")
    #             text += actual_p.get_text()

    return text


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    # news = get_news_data(url)

    get_wikipedia_results('Leyen', hops=2)

    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
