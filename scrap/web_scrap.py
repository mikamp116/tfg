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

    content = Bs(html.text, features="lxml").find(class_='mw-parser-output')  # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.
    text = ''

    if hops > 0:
        links = []
        for child in content.children:
            if child.name == 'p':
                text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"
                a_s = child.find_all('a')
                for link in a_s:
                    if link.has_attr("href"):
                        if link["href"].startswith("/wiki/"):
                            links.append(link)

        text += get_wikipedia_results_recursive(hops - 1, links)
    else:
        for child in content.children:
            if child.name == 'p':
                text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"

    return text


#     Hay que hacer una plantilla para Wikipedia en la que se cojan el texto únicamente y se excluyan elementos como
# las notas al pie de foto o las referencias. La extracción de triplas también debe devolver las entidades

def get_wikipedia_results_recursive(hops, wiki_pages):

    text = ''

    if hops > 0:
        links = []
        for wiki in wiki_pages:
            url = 'https://en.wikipedia.org/' + wiki['href']
            html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                            'Gecko/20100101 Firefox/74.0'})

            content = Bs(html.text, features="lxml").find(class_='mw-parser-output')  # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

            for child in content.children:
                if child.name == 'p':
                    text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"
                    for link in child.find_all('a'):
                        if link.has_attr("href"):
                            if link["href"].startswith("/wiki/"):
                                links.append(link)

        text += get_wikipedia_results_recursive(hops - 1, links)
    else:
        for wiki in wiki_pages:
            url = 'https://en.wikipedia.org/' + wiki['href']
            html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                            'Gecko/20100101 Firefox/74.0'})

            content = Bs(html.text, features="lxml").find(class_='mw-parser-output')  # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

            for child in content.children:
                if child.name == 'p':
                    text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"

    return text


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    # news = get_news_data(url)

    text = get_wikipedia_results('Leyen', hops=1)

    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
