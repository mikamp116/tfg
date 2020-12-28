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


def get_true_news(keywords):
    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
    links = [get_google_results(keywords, site) for site in sources]

    # related news

    return links


def get_google_results(keywords, site, num_results=10):
    """Retrieves a list with the 10 first results of Google searching the given keywords in the specified site"""
    browser = wd.Chrome('/home/mikamp116/Downloads/chromedriver86')
    url = 'https://www.google.com'
    browser.get(url)

    google_cookies = [{'domain': '.google.com',
  'expiry': 2146723199,
  'httpOnly': False,
  'name': 'CONSENT',
  'path': '/',
  'sameSite': 'None',
  'secure': True,
  'value': 'YES+ES.en+V9+BX'},
 {'domain': 'www.google.com',
  'expiry': 1609198685,
  'httpOnly': False,
  'name': 'UULE',
  'path': '/',
  'secure': True,
  'value': 'a+cm9sZTogMQpwcm9kdWNlcjogMTIKdGltZXN0YW1wOiAxNjA5MTc3MDg1Mjc4MDAwCmxhdGxuZyB7CiAgbGF0aXR1ZGVfZTc6IDQwMjk3MTg0MgogIGxvbmdpdHVkZV9lNzogLTM4MTQ2NjI1Cn0KcmFkaXVzOiAxMjIzODgwCnByb3ZlbmFuY2U6IDYK'},
 {'domain': '.google.com',
  'expiry': 1624988274,
  'httpOnly': True,
  'name': 'NID',
  'path': '/',
  'sameSite': 'None',
  'secure': True,
  'value': '205=gebCYZ_OR8rpQHkm_wQ73bUFGsvgtHCpHre2lrSHWJ1Du1TWdZHIW25rKIo7ZcdT-BXmkPHjqoz1MElxO6ntiO1O_WX6xLJX9TiAg2xyhfn_vcoCO1h66rUb8GK6qusoMEHzLjGVAtcNcXvTHM00BbhOA2v9Vryobqh4UwRCM48'},
 {'domain': 'www.google.com',
  'expiry': 1609177685,
  'httpOnly': False,
  'name': 'DV',
  'path': '/',
  'secure': False,
  'value': 'o_HnBf2pffsuYDWOpqAb4t3CJNumalfvuV7H4kDCogEAAAA'},
 {'domain': '.google.com',
  'expiry': 1624729084,
  'httpOnly': True,
  'name': 'CGIC',
  'path': '/search',
  'secure': False,
  'value': 'IocBdGV4dC9odG1sLGFwcGxpY2F0aW9uL3hodG1sK3htbCxhcHBsaWNhdGlvbi94bWw7cT0wLjksaW1hZ2UvYXZpZixpbWFnZS93ZWJwLGltYWdlL2FwbmcsKi8qO3E9MC44LGFwcGxpY2F0aW9uL3NpZ25lZC1leGNoYW5nZTt2PWIzO3E9MC45'}]
    for cookie in google_cookies:
        browser.add_cookie(cookie)

    search_box = browser.find_element_by_name('q')
    search = keywords + ' site:' + site + " -ext:xml"
    search_box.send_keys(search)
    search_box.submit()

    links = []
    for i in range(1, num_results + 1):
        try:
            links.append(browser.find_element_by_xpath(
        "/html/body/div[7]/div[2]/div[10]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[" + str(i) + "]/div/div[1]/a")
        .get_attribute('href'))
        except:
            pass
    browser.close()

    return links


def get_wikipedia_results(entity, hops=0, num_links=None):
    url = 'https://en.wikipedia.org/wiki/' + entity
    html = requests.get(url,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'})

    content = Bs(html.text, features="lxml").find(class_='mw-parser-output')
    # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.
    text = ''

    if hops > 0:
        links = []
        for child in content.children:
            if child.name == 'p':
                text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"
                for link in child.find_all('a'):
                    if link.has_attr("href") and num_links is not None:
                        if link["href"].startswith("/wiki/") and len(links) < num_links:
                            links.append(link)
        text += get_wikipedia_results_recursive(hops - 1, links, num_links)
    else:
        for child in content.children:
            if child.name == 'p':
                text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"

    return text


#     La extracción de triplas también debe devolver las entidades

def get_wikipedia_results_recursive(hops, wiki_pages, num_links=None):
    text = ''

    if hops > 0:
        links = []
        for wiki in wiki_pages:
            url = 'https://en.wikipedia.org/' + wiki['href']
            html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                            'Gecko/20100101 Firefox/74.0'})

            content = Bs(html.text, features="lxml").find(class_='mw-parser-output')
            # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

            for child in content.children:
                if child.name == 'p':
                    text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"
                    for link in child.find_all('a'):
                        if link.has_attr("href") and num_links is not None:
                            if link["href"].startswith("/wiki/") and len(links) < num_links:
                                links.append(link)

        text += get_wikipedia_results_recursive(hops - 1, links)
    else:
        for wiki in wiki_pages:
            url = 'https://en.wikipedia.org/' + wiki['href']
            html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                            'Gecko/20100101 Firefox/74.0'})

            content = Bs(html.text, features="lxml").find(class_='mw-parser-output')
            # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

            for child in content.children:
                if child.name == 'p':
                    text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"

    return text


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    # news = get_news_data(url)

    # text = get_wikipedia_results('Leyen', hops=2, num_links=100)

    links = get_true_news("wannacry attacks corporation")

    pass
