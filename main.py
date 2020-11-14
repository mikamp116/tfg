from nlp import triples_extraction as te
from scrap import web_scrap as ws

def main(url):
    sources = ['theguardian.com', 'bbc.com', 'news.sky.com', 'independent.co.uk']
    article = ws.get_news_data(url)

    triplas, entidades = te.extraction(article.text)
    # print(triplas)

    noticia = ws.get_wikipedia_results(entidades[2])

    # for site in sources:
    #     ws.get_google_results()


if __name__ == '__main__':
    url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    main(url)