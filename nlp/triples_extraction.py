import networkx as nx
from matplotlib import pyplot as plt
from openie import StanfordOpenIE
import spacy
import neuralcoref
from summa import summarizer
from tqdm import tqdm, trange
from scrap import web_scrap as ws


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


def bulk_extraction(true_news_link_list):
    nlp = spacy.load('en_core_web_lg')
    neuralcoref.add_to_pipe(nlp)

    with StanfordOpenIE() as client:
        web_scrap_extraction = []
        for keyword_urls in tqdm(true_news_link_list, desc="Extracting triples from true news articles..."):
            for site_urls in keyword_urls:
                for url in site_urls:
                    article = ws.get_news_data(url)
                    text_resolved = nlp(article.text)._.coref_resolved
                    doc = nlp(text_resolved)
                    lemmatized_text = ' '.join(
                        [token.lemma_ if (token.pos == 100 or token.pos == 87) else token.text for token in doc])
                    triples_dict = client.annotate(lemmatized_text)
                    triple_list= [(d['subject'], d['relation'], d['object']) for d in triples_dict]

                    web_scrap_extraction.append(triple_list)
    return web_scrap_extraction


def print_graph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.spring_layout(G)


    # plt.figure()
    # nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
    #         node_size=50, node_color='seagreen', alpha=0.9,
    #         labels={node: node for node in G.nodes()})
    # plt.axis('off')

    plt.figure(figsize=(100, 60))
    d = dict(G.degree)
    nx.draw(G, pos=pos, node_color='orange',
            with_labels=False,
            node_size=[d[k] * 300 for k in d])
    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=d[node] * 3, ha='center', va='center')
    plt.savefig("filename6.png")


if __name__ == '__main__':
    text = '''
    Unable either to stay in France or to move to Germany, Marx decided to emigrate to Brussels in Belgium in February 1845. However, to stay in Belgium he had to pledge not to publish anything on the subject of contemporary politics. In Brussels, Marx associated with other exiled socialists from across Europe, including Moses Hess, Karl Heinzen and Joseph Weydemeyer. In April 1845, Engels moved from Barmen in Germany to Brussels to join Marx and the growing cadre of members of the League of the Just now seeking home in Brussels. Later, Mary Burns, Engels' long-time companion, left Manchester, England to join Engels in Brussels.

In mid-July 1845, Marx and Engels left Brussels for England to visit the leaders of the Chartists, a working-class movement in Britain. This was Marx's first trip to England and Engels was an ideal guide for the trip. Engels had already spent two years living in Manchester from November 1842 to August 1844. Not only did Engels already know the English language, he had also developed a close relationship with many Chartist leaders. Indeed, Engels was serving as a reporter for many Chartist and socialist English newspapers. Marx used the trip as an opportunity to examine the economic resources available for study in various libraries in London and Manchester.

In collaboration with Engels, Marx also set about writing a book which is often seen as his best treatment of the concept of historical materialism, The German Ideology. In this work, Marx broke with Ludwig Feuerbach, Bruno Bauer, Max Stirner and the rest of the Young Hegelians, while he also broke with Karl Grun and other "true socialists" whose philosophies were still based in part on "idealism". In German Ideology, Marx and Engels finally completed their philosophy, which was based solely on materialism as the sole motor force in history. German Ideology is written in a humorously satirical form, but even this satirical form did not save the work from censorship. Like so many other early writings of his, German Ideology would not be published in Marx's lifetime and would be published only in 1932.

After completing German Ideology, Marx turned to a work that was intended to clarify his own position regarding "the theory and tactics" of a truly "revolutionary proletarian movement" operating from the standpoint of a truly "scientific materialist" philosophy. This work was intended to draw a distinction between the utopian socialists and Marx's own scientific socialist philosophy. Whereas the utopians believed that people must be persuaded one person at a time to join the socialist movement, the way a person must be persuaded to adopt any different belief, Marx knew that people would tend on most occasions to act in accordance with their own economic interests, thus appealing to an entire class (the working class in this case) with a broad appeal to the class's best material interest would be the best way to mobilise the broad mass of that class to make a revolution and change society. This was the intent of the new book that Marx was planning, but to get the manuscript past the government censors he called the book The Poverty of Philosophy (1847) and offered it as a response to the "petty bourgeois philosophy" of the French anarchist socialist Pierre-Joseph Proudhon as expressed in his book The Philosophy of Poverty (1840).
Marx with his daughters and Engels

These books laid the foundation for Marx and Engels's most famous work, a political pamphlet that has since come to be commonly known as The Communist Manifesto. While residing in Brussels in 1846, Marx continued his association with the secret radical organisation League of the Just. As noted above, Marx thought the League to be just the sort of radical organisation that was needed to spur the working class of Europe toward the mass movement that would bring about a working class revolution. However, to organise the working class into a mass movement the League had to cease its "secret" or "underground" orientation and operate in the open as a political party. Members of the League eventually became persuaded in this regard. Accordingly, in June 1847 the League was reorganised by its membership into a new open "above ground" political society that appealed directly to the working classes. This new open political society was called the Communist League. Both Marx and Engels participated in drawing up the programme and organisational principles of the new Communist League.

In late 1847, Marx and Engels began writing what was to become their most famous work – a programme of action for the Communist League. Written jointly by Marx and Engels from December 1847 to January 1848, The Communist Manifesto was first published on 21 February 1848.The Communist Manifesto laid out the beliefs of the new Communist League. No longer a secret society, the Communist League wanted to make aims and intentions clear to the general public rather than hiding its beliefs as the League of the Just had been doing. The opening lines of the pamphlet set forth the principal basis of Marxism: "The history of all hitherto existing society is the history of class struggles". It goes on to examine the antagonisms that Marx claimed were arising in the clashes of interest between the bourgeoisie (the wealthy capitalist class) and the proletariat (the industrial working class). Proceeding on from this, the Manifesto presents the argument for why the Communist League, as opposed to other socialist and liberal political parties and groups at the time, was truly acting in the interests of the proletariat to overthrow capitalist society and to replace it with socialism.

Later that year, Europe experienced a series of protests, rebellions and often violent upheavals that became known as the Revolutions of 1848. In France, a revolution led to the overthrow of the monarchy and the establishment of the French Second Republic. Marx was supportive of such activity and having recently received a substantial inheritance from his father (withheld by his uncle Lionel Philips since his father's death in 1838) of either 6,000 or 5,000 francs he allegedly used a third of it to arm Belgian workers who were planning revolutionary action. Although the veracity of these allegations is disputed, the Belgian Ministry of Justice accused Marx of it, subsequently arresting him and he was forced to flee back to France, where with a new republican government in power he believed that he would be safe.
    '''
    triples, entities = extraction(text)

    print_graph(triples)

    pass
