from newspaper import Article
from summa.summarizer import summarize
import selenium.webdriver as wd


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


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    news = get_news_data(url)

    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
