import random
from nlp import triples_extraction as te
from scrap import web_scrap as ws
from tqdm import tqdm
import csv
import time
from threading import Thread


def write_test_triples_to_csv(triple_list, filename):
    print(f'Writing triples to "{filename}"...')
    csv_write = open(filename, mode='w', newline='')
    csv_writer = csv.writer(csv_write, delimiter=',')
    for triple in triple_list:
        csv_writer.writerow([triple[0], triple[1], triple[2]])
    csv_write.close()
    csv_write = None
    csv_writer = None
    print(f'{filename} written!')


def get_triples_information(query_triple_list, n_source_results, date, true_news_limit, true_news_link_limit):

    # Limite para el Getting true news
    if true_news_limit is not None:
        query_triple_list = random.shuffle(query_triple_list)[:true_news_limit]
    true_news_link_list = ws.get_true_news(query_triple_list, n_source_results)

    # same: true_news_link_list = [ws.get_true_news(' '.join(query_triple), 2) for query_triple in query_triple_list]

    # Limit true_news_link_list
    if true_news_link_limit is not None:
        true_news_link_list = random.shuffle(true_news_link_list)[:true_news_link_limit]

    web_scrap_extraction = te.link_bulk_extraction(true_news_link_list)
    # true_news_link_list = None

    train_a_filename = f'/files/train_a_{date}.csv'
    print(f'Writing triples to "{train_a_filename}"...')
    csv_write = open(train_a_filename, mode='w', newline='')
    csv_writer = csv.writer(csv_write, delimiter=',')
    for triple_list in web_scrap_extraction:
        for triple in triple_list:
            csv_writer.writerow([triple[0], triple[1], triple[2]])
    csv_write.close()
    csv_write = None
    csv_writer = None
    # web_scrap_extraction = None
    print(f'{train_a_filename} written!')


def get_entity_information(entity_list, n_wikipedia_hops, n_wikipedia_links):
    for query_entity in tqdm(entity_list, desc="Scrapping Wikipedia for related text..."):
        wikipedia_results.append(ws.get_wikipedia_results(query_entity, n_wikipedia_hops, n_wikipedia_links))


def get_entities_information(query_entity_list, n_wikipedia_hops, n_wikipedia_links, date):
    global wikipedia_results
    wikipedia_results = []

    n_threads = 6
    aux_list = []
    last_index = 0
    # Limit query entity list
    for i in range(n_threads):
        aux_index = (len(query_entity_list) - last_index) // (n_threads - i)
        aux_list.append(query_entity_list[last_index: last_index + aux_index])
        last_index += aux_index

    lista_hilos = [Thread(target=get_entity_information, args=(aux_list[i], n_wikipedia_hops, n_wikipedia_links))
                   for i in range(n_threads)]
    aux_list = None

    for hilo in lista_hilos:
        hilo.daemon = True
        hilo.start()

    for hilo in lista_hilos:
        hilo.join()

    lista_hilos = None

    wikipedia_extraction = te.wikipedia_bulk_extraction(wikipedia_results)

    train_b_filename = f'/files/train_b_{date}.csv'
    print(f'Writing triples to "{train_b_filename}"...')
    csv_write = open(train_b_filename, mode='w', newline='')
    csv_writer = csv.writer(csv_write, delimiter=',')
    for triple_list in wikipedia_extraction:
        for triple in triple_list:
            csv_writer.writerow([triple[0], triple[1], triple[2]])
    csv_write.close()
    csv_write = None
    csv_writer = None
    wikipedia_extraction = None
    print(f'{train_b_filename} written!')


def main(query_url, summarization, n_source_results, date, n_words_article=None, n_wikipedia_hops=0,
         n_wikipedia_links=500, true_news_limit=None, true_news_link_limit=None, test_triples_file=None):
    # if test_triples_file is None:
    start = time.perf_counter()
    print(f'Getting content of {query_url}')
    query_article = ws.get_news_data(query_url, n_words_article)
    print(f'Extracting triples for "{query_article.title}"...')
    if summarization:
        text = query_article.summary
    else:
        text = query_article.text
    query_triple_list, query_entity_list = te.extraction(text)
    # query_article = None
    # text = None

    test_triples_csv = Thread(target=write_test_triples_to_csv, args=(query_triple_list, f'/files/test_{date}.csv'))
    test_triples_csv.start()
    # else:
    #     csv_read = open(test_triples_file, mode='r', newline='')
    #     csv_reader = csv.reader(csv_read, delimiter=',')
    #     query_triple_list = [row for row in csv_reader]

    triples_information = Thread(target=get_triples_information,
                                 args=(query_triple_list, n_source_results, date, true_news_limit, true_news_link_limit))
    entities_information = Thread(target=get_entities_information,
                                  args=(query_entity_list, n_wikipedia_hops, n_wikipedia_links, date))

    triples_information.start()
    entities_information.start()

    triples_information.join()
    entities_information.join()
    test_triples_csv.join()
    #
    # query_triple_list = None
    # query_entity_list = None
    #
    end = time.perf_counter()
    print(f'The execution took {end - start} seconds.')


def main_fake(text, n_source_results, date, n_wikipedia_hops=0, n_wikipedia_links=500, true_news_limit=None,
              true_news_link_limit=None):

    query_triple_list, query_entity_list = te.extraction(text)

    test_triples_csv = Thread(target=write_test_triples_to_csv, args=(query_triple_list, f'/files/test_{date}.csv'))
    test_triples_csv.start()

    triples_information = Thread(target=get_triples_information,
                                 args=(query_triple_list, n_source_results, date, true_news_limit, true_news_link_limit))
    entities_information = Thread(target=get_entities_information,
                                  args=(query_entity_list, n_wikipedia_hops, n_wikipedia_links, date))

    triples_information.start()
    entities_information.start()

    triples_information.join()
    entities_information.join()
    test_triples_csv.join()
    #
    # query_triple_list = None
    # query_entity_list = None


if __name__ == '__main__':

    query_news_url = 'https://www.theguardian.com/world/commentisfree/2020/jul/27/europe-coronavirus-planet-climate'

    date = 20210915_03

    main(query_news_url,
         summarization=True,
         n_source_results=2,
         date=date,
         n_words_article=None,
         n_wikipedia_hops=0,
         n_wikipedia_links=100,
         true_news_limit=50,
         true_news_link_limit=None,
         test_triples_file=None,
         # model = ComplEx,
         # batches_count=100,
         # seed=0,
         # epochs=200,
         # k=150,
         # eta=5,
         # optimizer='adam',
         # optimizer_params={'lr':1e-3},
         # loss='multiclass_nll',
         # regularizer='LP',
         # regularizer_params={'p':3, 'lambda':1e-5},
         )

    main_fake(query_news_url,
              n_source_results=2,
              date='fake ' + str(date),
              n_wikipedia_hops=0,
              n_wikipedia_links=100,
              true_news_limit=50,
              true_news_link_limit=None,
              # model = ComplEx,
              # batches_count=100,
              # seed=0,
              # epochs=200,
              # k=150,
              # eta=5,
              # optimizer='adam',
              # optimizer_params={'lr':1e-3},
              # loss='multiclass_nll',
              # regularizer='LP',
              #  regularizer_params={'p':3, 'lambda':1e-5},
              )
