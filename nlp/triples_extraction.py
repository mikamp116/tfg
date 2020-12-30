from openie import StanfordOpenIE
import spacy
import neuralcoref
from summa import summarizer


def resolve_coreferences(nlp, text):
    """
    Resolves text coreferences such as in 'The girl loves her dog. She (the girl) loves him (her dog).'

    :param nlp: spacy natural language processor
    :param text: str with input news content
    :return: str containing news content without coreferences
    """
    neuralcoref.add_to_pipe(nlp)
    return nlp(text)._.coref_resolved


def extraction(text):
    """
    Extract relations between entities present in the news item and packs them in (head, relation, tail) triples.

    :param text: str with input news content
    :return: list of (h, r, t) triples
    """
    nlp = spacy.load('en_core_web_lg')

    #sum_text = summarizer.summarize(text)

    text_resolved = resolve_coreferences(nlp, text)

    # print(text_resolved)

    doc = nlp(text_resolved)
    lemmatized_text = ' '.join([token.lemma_ if (token.pos == 100 or token.pos == 87) else token.text for token in doc])
    # print(lemmatized_text)

    with StanfordOpenIE() as client:
        triples_dict = client.annotate(lemmatized_text)

    valid_ents = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LANGUAGE', 'DATE',
                  'TIME']
    entities = [ent.text for ent in doc.ents if ent.label_ in valid_ents]

    return [(d['subject'], d['relation'], d['object']) for d in triples_dict], list(set(entities))
