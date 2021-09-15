from openie import StanfordOpenIE
import spacy
import neuralcoref
from tqdm import tqdm
import time
from scrap import web_scrap as ws


def show_linguistic_features(docs):
    """
    Muestra por pantalla los atributos linguisticos de cada token.
    :param docs: lista de spacy.tokens.doc.Doc conteniendo las oraciones
    :return:
    """
    sep = ' '
    for d in docs:
        for token in d:
            print(token.text, (20 - len(token.text)) * sep,
                  token.lemma_, (20 - len(token.lemma_)) * sep,
                  token.pos,  18 * sep,
                  token.tag_, (20 - len(token.tag_)) * sep,
                  token.dep_, (20 - len(token.dep_)) * sep,
                  token.sentiment, 18 * sep,
                  token.is_alpha, 5 * sep,
                  token.is_stop, 5 * sep,
                  token.ent_type_)
        print('----------------------')


def extraction(text, entity_extraction=True):
    """
    Extract relations between entities present in the news item and packs them in (head, relation, tail) triples.

    Test the method with the followwin operations:
     - lemmatization + information extraction
     - information extraction + lemmatization
     - information extraction

    :param text: str with input news content
    :return: list of (h, r, t) triples
    """
    nlp = spacy.load('en_core_web_lg')
    neuralcoref.add_to_pipe(nlp)

    coref_start = time.perf_counter()
    text_resolved = nlp(text)._.coref_resolved
    coref_end = time.perf_counter()
    print(f'The coref execution took {coref_end - coref_start} seconds.')

    doc = nlp(text_resolved)
    lemmatized_text = ''.join([token.lemma_ + token.whitespace_
                               if token.pos == 87 or
                                  (token.pos == 100 and (token.tag_ == 'VBD' or token.dep_ == 'ROOT'))
                               else token.text + token.whitespace_ for token in doc])

    ie_start = time.perf_counter()
    with StanfordOpenIE() as client:
        triples_dict = client.annotate(lemmatized_text)
    ie_end = time.perf_counter()
    print(f'The IE execution took {ie_end - ie_start} seconds.')

    if entity_extraction:
        valid_ents = ['PERSON', 'PER', 'NORP', 'FAC', 'FACILITY', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT',
                      'WORK_OF_ART', 'LAW', 'LANGUAGE', 'DATE', 'MONEY', 'MISC', 'EVT', 'PROD', 'GPE_LOC', 'GPE_ORG']
        entities = [ent.text for ent in doc.ents if ent.label_ in valid_ents]
        return [(d['subject'], d['relation'], d['object']) for d in triples_dict], list(set(entities))
    else:
        return [(d['subject'], d['relation'], d['object']) for d in triples_dict]


def link_bulk_extraction(true_news_link_list):
    nlp = spacy.load('en_core_web_lg')
    neuralcoref.add_to_pipe(nlp)

    with StanfordOpenIE() as client:
        web_scrap_extraction = []
        for keyword_urls in tqdm(true_news_link_list, desc="Extracting triples from true news articles..."):
            for url in keyword_urls:
                if url.startswith('http:///newtabredir') == False:
                    article = ws.get_news_data(url)
                    text_resolved = nlp(article.text)._.coref_resolved
                    doc = nlp(text_resolved)
                    lemmatized_text = ''.join([token.lemma_ + token.whitespace_
                                               if token.pos == 87 or
                                                  (token.pos == 100 and (token.tag_ == 'VBD' or token.dep_ == 'ROOT'))
                                               else token.text + token.whitespace_ for token in doc])
                    triples_dict = client.annotate(lemmatized_text)
                    triple_list = [(d['subject'], d['relation'], d['object']) for d in triples_dict]

                    web_scrap_extraction.append(triple_list)
    return web_scrap_extraction


def wikipedia_bulk_extraction(wikipedia_text):
    nlp = spacy.load('en_core_web_lg')
    neuralcoref.add_to_pipe(nlp)

    with StanfordOpenIE() as client:
        wikipedia_extraction = []
        for text in tqdm(wikipedia_text, desc="Extracting triples from Wikipedia text..."):
            text_resolved = nlp(text)._.coref_resolved
            doc = nlp(text_resolved)
            lemmatized_text = ''.join([token.lemma_ + token.whitespace_
                                       if token.pos == 87 or
                                          (token.pos == 100 and (token.tag_ == 'VBD' or token.dep_ == 'ROOT'))
                                       else token.text + token.whitespace_ for token in doc])
            triples_dict = client.annotate(lemmatized_text)
            triple_list = [(d['subject'], d['relation'], d['object']) for d in triples_dict]

            wikipedia_extraction.append(triple_list)
    return wikipedia_extraction


if __name__ == '__main__':
    text = ''
    triples, entities = extraction(text)
