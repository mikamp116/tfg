from newspaper import Article
from summa.summarizer import summarize
import re
from bs4 import BeautifulSoup as Bs
from requests import get as api_get
from urllib import parse
from tqdm import tqdm, trange


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


def get_news_data(news_url, num_words=None):
    """Retrieves information about the news article"""
    article = Article(news_url)
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

    try:
        site_name = metadata['og']['site_name']
        generator = metadata['generator']
    except:
        site_name = 'site_name'
        generator = 'generator'

    return News(article.title, authors, 'description', article.text, article.summary, summary_,
                article.is_valid_body() and article.is_valid_url(), site_name, generator)


def get_true_news(keywords, num_results=10):

    def get_google_results(keywords, site, num_results):
        """Retrieves a list with the 10 first results of Google searching the given keywords in the specified site"""

        user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'}

        usr_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36'}

        def fetch_results(keywords, num_results):
            escaped_search_term = keywords.replace(' ', '+')

            # google_url = 'https://www.google.com/search?q=' + escaped_search_term + '+site%3A' + site + '&num=' \
            #              + str(num_results) + 'hl=en'

            google_url = 'https://duckduckgo.com/?q=' + escaped_search_term + '+site%3A' + site

            response = api_get(google_url)
            #response.raise_for_status()

            return response

        def parse_results(raw_html):
            soup = Bs(raw_html, 'html.parser')
            result_block = soup.find_all('div', attrs={'class': 'g'})
            for result in result_block:
                link = result.find('a', href=True)
                title = result.find('h3')
                if link and title:
                    yield link['href']

        response = fetch_results(keywords, num_results)
        return list(parse_results(response.text))
        # links = list(parse_results(response.text))
        # if len(links) < num_results:
        #     return links[:num_results]
        # return links



    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
    links = [get_searx_results(keywords, site, num_results) for site in tqdm(sources, desc="Getting Searx results")]

    # related news

    return links

def get_searx_results(keywords, site, num_results):
    # return get_standalone_searx(keywords + ' site:' + site)
    cummulative_links = []
    searx_text = parse.quote(keywords + ' site:' + site)
    # base_url = 'http://127.0.0.1:8888/search'
    # params = {
    #     'q': searx_text,
    #     'categories': 'general',
    #     'lang': 'en',
    #     'format': 'json'}
    # response = api_get(base_url, params=params).json()
    response = api_get('http://127.0.0.1:8888/search?q=eu%20bans%20uk%20flights&categories=general&lang=en&engines=google,duckduckgo,bing,qwant,wikidata,startpage,yahoo&format=json').json()

    for result in response['results']:
        cummulative_links.append(result)

    return cummulative_links


def get_wikipedia_results(entity, hops=0, num_links=None):
    def get_wikipedia_results_recursive(hops, wiki_pages, num_links=None):
        text = ''

        if hops > 0:
            links = []
            for wiki in wiki_pages:
                url = 'https://en.wikipedia.org/' + wiki['href']
                html = api_get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
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
                html = api_get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) '
                                                           'Gecko/20100101 Firefox/74.0'})

                content = Bs(html.text, features="lxml").find(class_='mw-parser-output')
                # To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

                for child in content.children:
                    if child.name == 'p':
                        text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"

        return text

    url = 'https://en.wikipedia.org/wiki/' + entity
    html = api_get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 '
                                               'Firefox/74.0'})

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
                # text += re.sub(' +', ' ', child.get_text().replace("\n", " ")) + "\n"
                text += re.sub(' +', ' ', re.sub('\[.*?\]', '', child.get_text().replace("\n", " "))) + "\n"

    return text


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    # news = get_news_data(url)

    # text = get_wikipedia_results('Leyen', hops=2, num_links=100)

    # links = get_true_news("wannacry attacks corporation")

    links = []

    for i in trange(500):
        res = get_searx_results('eu bans uk flights', 'bbc.com', 10)
        links.append(res)

    pass
