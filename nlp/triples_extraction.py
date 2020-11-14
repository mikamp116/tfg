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


if __name__ == '__main__':
    text = "Michael Jordan is the president of the United States of America. Barack Obama played for the Chicago " \
           "Bulls. New York, which is in the east of America, is the most populated city in the United States of " \
           "America. The Rolling Stones played in Coachella."

    text = """Ubisoft: Sexual misconduct probe sees three senior heads resign.

            Three senior executives at game-maker Ubisoft have stepped down amid an investigation into sexual misconduct.
            
            The French company's chief creative officer, Canadian studios head, and global HR chief had all left their roles, Ubisoft said.
            
            Ubisoft is a major player in the games industry, best known for the Assassin's Creed franchise.
            
            The resignations came just before its annual showcase of new games, which made no mention of the allegations.
            
            In a tweet ahead of the event, Ubisoft said: "Because all the content has been pre-recorded, we wanted to recognise that the issues we're currently dealing with won't be addressed directly in the show."
            
            The company has already seen one of its most senior executives depart and another placed on administrative leave."""

    triples = extraction(text)
    print(triples)
