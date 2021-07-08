from nlp import triples_extraction as te
from scrap import web_scrap as ws
from tqdm import tqdm
import csv


def write_triples_to_csv(triple_list, filename):
    print(f'Writing triples to "{filename}"...')
    csv_write = open(filename, mode='w', newline='')
    csv_writer = csv.writer(csv_write, delimiter=',')
    for triples in triple_list:
        for t in triples:
            csv_writer.writerow([t[0], t[1], t[2]])
    csv_write.close()
    print(f'{filename} written!')


def main(query_url):
    print(f'Getting content of {query_url}')
    query_article = ws.get_news_data(query_url)
    print(f'Extracting triples for "{query_article.title}"...')
    query_triple_list, query_entity_list = te.extraction(query_article.summary)

    write_triples_to_csv([query_triple_list], 'test_20210707.csv')

    # TRIPLES PATH
    true_news_link_list = []
    for query_triple in tqdm(query_triple_list[:20], desc="Getting articles for true news..."):
        keywords = ' '.join(query_triple)
        true_news_link_list.append(ws.get_true_news(keywords, 2))  # Lista de listas de listas de urls
    # same: true_news_link_list = [ws.get_true_news(' '.join(query_triple), 2) for query_triple in query_triple_list]

    # web_scrap_extraction = []
    # for keyword_urls in tqdm(true_news_link_list, desc="Extracting triples from true news articles..."):
    #     for site_urls in keyword_urls:
    #         for url in site_urls:
    #             article = ws.get_news_data(url)
    #             triple_list, _ = te.extraction(article.text)
    #             web_scrap_extraction.append(triple_list)
    web_scrap_extraction = te.bulk_extraction(true_news_link_list)

    write_triples_to_csv(web_scrap_extraction, 'train_a_20210707.csv')

    # csv_write = open('train.csv', mode='w', newline='')
    # csv_writer = csv.writer(csv_write, delimiter=',')
    # for l1 in web_scrap_extraction:
    #     for t in l1:
    #         csv_writer.writerow([t[0], t[1], t[2]])
    # csv_write.close()

    #ENTITIES PATH
    wikipedia_text = []

    for query_entity in tqdm(query_entity_list, desc="Scrapping Wikipedia for related text..."):
        results = ws.get_wikipedia_results(query_entity)
        wikipedia_text.append(results)

    wikipedia_extraction = [te.extraction(text) for text in tqdm(wikipedia_text,
                                                                 desc='Extracting triples from Wikipedia text...')]

    write_triples_to_csv(wikipedia_extraction, 'train_b_20210707.csv')

    pass


if __name__ == '__main__':
    query_news_url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'
    main(query_news_url)
