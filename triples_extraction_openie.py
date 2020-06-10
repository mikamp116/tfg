from openie import StanfordOpenIE
import spacy
import neuralcoref


def resolve_coreferences(nlp, text):
    """
    Resolves text coreferences such as in 'The girl loves her dog. She (the girl) loves him (her dog).'

    :param nlp: spacy natural language processor
    :param text: str with input news content
    :return: str containing news content without coreferences
    """
    neuralcoref.add_to_pipe(nlp)
    return nlp(text)._.coref_resolved


def entity_alignment(nlp, triples):  # not used
    """
    Removes the triples that represent the same relation.
    Removes entities that refer to the same entity but with different names.

    :param nlp: spacy natural language processor
    :param triples: list of (h, r, t) triples
    :return: list of unified (h, r, t) triples
    """
    for triple in triples:
        s, r, o = triple
        s_doc = nlp(s)
        r_doc = nlp(r)
        o_doc = nlp(o)

        s_ents = set([ent.text for ent in s_doc.ents])
        o_ents = set([ent.text for ent in o_doc.ents])

        # Si el sujeto no es una entidad
        # if (s_doc[:len(s_doc)].text not in s_ents):
        if (s_doc.text not in s_ents):
            triples.remove(triple)


def main(text):
    """
    Extract relations between entities present in the news item and packs them im (head, relation, tail) triples.

    :param text: str with input news content
    :return: list of (h, r, t) triples
    """
    nlp = spacy.load('en_core_web_lg')

    text_resolved = resolve_coreferences(nlp, text)

    with StanfordOpenIE() as client:
        triples_dict = client.annotate(text_resolved)

    return [(d['subject'], d['relation'], d['object']) for d in triples_dict]


if __name__ == '__main__':
    text = "Michael Jordan is the president of the United States of America. Barack Obama played for the Chicago " \
           "Bulls. New York, which is in the east of America, is the most populated city in the United States of " \
           "America. The Rolling Stones played in Coachella."

    triples = main(text)
