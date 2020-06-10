import spacy


def show_linguistic_features(docs):
    """
    Muestra por pantalla los atributos linguisticos de cada token.

    :param docs: lista de spacy.tokens.doc.Doc conteniendo las oraciones
    :return:
    """
    sep = ' '
    for d in docs:
        print('text', (20 - 4) * sep, 'lemma_', (20 - 6) * sep, 'pos_', (20 - 4) * sep, 'tag_', (20 - 4) * sep, 'dep_',
              (20 - 4) * sep, 'shape_', (20 - 6) * sep, 'is_alpha', 5 * sep, 'is_stop', 5 * sep, 'ent_type_')
        for token in d:
            print(token.text, (20 - len(token.text)) * sep, token.lemma_, (20 - len(token.lemma_)) * sep,
                  token.pos_,
                  (20 - len(token.pos_)) * sep, token.tag_, (20 - len(token.tag_)) * sep, token.dep_,
                  (20 - len(token.dep_)) * sep,
                  token.shape_, (20 - len(token.shape_)) * sep, token.is_alpha, 5 * sep, token.is_stop, 5 * sep,
                  token.ent_type_)
        print('----------------------')


def are_ancestors(a, b):
    """
    Si las entidades son ancestros una de otra, devuelve 3.
    Si a es ancestro de b, devuelve 1.
    Si b es ancestro de a, devuelve 2.
    Si ninguna entidad es ancestro de otra, devuelve 0.

    :param a: entidad de tipo spacy.tokens.span.Span
    :param b: entidad de tipo spacy.tokens.span.Span
    :return: entero que representa si una entidad es ancestra de otra y, en caso de que asi sea, cual
    """
    if a.root.is_ancestor(b.root) and b.root.is_ancestor(a.root):
        return 3
    elif a.root.is_ancestor(b.root):
        return 1
    elif b.root.is_ancestor(a.root):
        return 2
    return 0


def is_relation(a, b):
    """
    Recorre los ancestros de las entidades hacia arriba hasta llegar al origen o encontrar una entidad.
    Realiza la intersección de los ancestros de ambas entidades y devuelve True si tienen alguno en comun,
    False en caso contrario.

    :param a: entidad de tipo spacy.tokens.span.Span
    :param b: entidad de tipo spacy.tokens.span.Span
    :return: bool indicando si las entidades a y b tienen alguna relacion
    """
    ancestors_a = []
    for anc in a.root.ancestors:
        # Recorre los ancestros y para si encuentra una entidad
        # Los spacy.tokens.token.Token guardan el tipo de entidad hasheado
        # en la variable spacy.tokens.token.Token.ent_type
        # Aquellos que no son entidades guardan el valor 0 en este atributo
        if anc.ent_type != 0:
            break
        ancestors_a.append(anc.i)

    ancestors_b = []
    for anc in b.root.ancestors:
        if anc.ent_type != 0:
            break
        ancestors_b.append(anc.i)

    return len(set.intersection(set(ancestors_a), set(ancestors_b))) > 0


def get_relation(ent):
    """
    Recorre los ancestros de la raiz de la entidad ent concatenando en relation los token que conforman la relacion
    asociada a ent.

    :param ent: spacy.tokens.span.Span con la entidad de la cual queremos obtener la relacion
    :return: str con la relacion que precede a la entidad
    """
    relation = ''
    for anc in ent.root.ancestors:
        # Para si encuentra un verbo auxiliar o una entidad
        if anc.pos == 87 or anc.ent_type != 0:
            break
        relation = anc.lemma_ + ' ' + relation
    return relation.strip()


def get_triples(ents):
    """
    Busca todas las relaciones posibles entre las entidades de ents.
    Si una entidad es ancestra de otra, busca la relacion entre ancestro y entidad.
    Si no son ancestros pero si hay relacion, busca la relacion entre a y b y tambien entre b y a,
    ya que no sabe en que direccion se produce la relacion.
    Las relaciones obtenidas se almacenan en la variable triples.

    :param ents: list of spacy.tokens.span.Span de entidades
    :return: tuple (entity, relation, entity) con las relaciones encontradas entre las entidades
    """
    triples = []
    for i in range(len(ents)):
        for j in range(i + 1, len(ents)):
            a, b = ents[i], ents[j]
            are_anc = are_ancestors(a, b)
            if are_anc == 1:  # a -> b
                rel = (a, get_relation(b), b)
                triples.append(rel)
            elif are_anc == 2:  # b -> a
                rel = (b, get_relation(a), a)
                triples.append(rel)
            elif are_anc == 3:
                print('Sale por 3. No implementado aun')
            else:
                if is_relation(a, b):
                    if a.root.dep_.startswith('nsubj'):
                        rel = (a, get_relation(b), b)
                        triples.append(rel)
                    elif b.root.dep_.startswith('nsubj'):
                        rel = (b, get_relation(a), a)
                        triples.append(rel)
    return triples


def main(doc):
    """
    Separa el texto en las distintas oraciones.
    Para cada oración extrae las entidades presentes y a continuación busca la relacion entre estas

    :param doc: spacy.tokens.doc.Doc del texto completo a analizar
    :return: triplas extraidas del texto (entidad, relacion, entidad)
    """
    # sentences = text.split('.')  # No vale porque rompe las oraciones con 'Mr.'
    sentences = [sent.text for sent in doc.sents]
    # sentences = [sent.text.translate(str.maketrans('', '', string.punctuation)) for sent in doc.sents]

    # Lista con los spacy.tokens.doc.Doc de cada oracion encontrada en el texto original
    doc_sents = [nlp(sent) for sent in sentences]

    # Lista de listas, una por cada oracion, cada una contiene un spacy.tokens.span.Span por cada entidad encontrada
    ent_sentences = [[ent for ent in doc.ents] for doc in doc_sents]

    # Lista de listas, una por cada oracion, cada una contiene las triplas (entidad, relacion, entidad) encontradas
    triples = [get_triples(sent) for sent in ent_sentences]

    return triples


if __name__ == '__main__':
    # nlp = spacy.load("en_core_web_sm")
    # nlp = spacy.load("en_core_web_md")
    # Los modelos que aparecen arriba no reconocen todas las entidades
    nlp = spacy.load("en_core_web_lg")

    text = "Michael Jordan is the president of the United States of America. Barack Obama played for the Chicago " \
           "Bulls. New York, which is in the east of America, is the most populated city in the United States of " \
           "America. The Rolling Stones played in Coachella."

    doc = nlp(text)
    triples = main(doc)
