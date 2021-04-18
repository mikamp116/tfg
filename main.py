from nlp import triples_extraction as te
from scrap import web_scrap as ws
from tqdm import tqdm


def main(query_url):
    query_article = ws.get_news_data(query_url)
    query_triple_list, query_entity_list = te.extraction(query_article.summary)


    true_news_link_list = []
    for query_triple in tqdm(query_triple_list, desc="Getting articles for true news..."):
        keywords = ' '.join(query_triple)
        true_news_link_list.append(ws.get_true_news(keywords, 2))
    # same: true_news_link_list = [ws.get_true_news(' '.join(query_triple), 2) for query_triple in query_triple_list]

    web_scrap_extraction = []
    for keyword_urls in tqdm(true_news_link_list, desc="Extracting triples from true news articles..."):
        for site_urls in keyword_urls:
            for url in site_urls:
                article = ws.get_news_data(url)
                triple_list, _ = te.extraction(article.text)
                web_scrap_extraction.append(triple_list)



    wikipedia_text = []
    for query_entity in tqdm(query_entity_list, desc="Extracting triples from Wikipedia text..."):
        results = ws.get_wikipedia_results(query_entity)
        wikipedia_text.append(results)

    wikipedia_extraction = [te.extraction(text) for text in wikipedia_text]




if __name__ == '__main__':
    query_news_url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    main(query_news_url)
