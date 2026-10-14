import rdflib
import os

ontho_file_path = os.path.join(os.path.dirname(__file__), "semantic_scholar.ttl")
g = rdflib.Graph()
g.parse(ontho_file_path, format="turtle")

'''
Requete qui associe des publications à des domaines en fonction des articles publiés par les auteurs et leurs interets

'''

def publication_interet():

    requete = g.query(
        """SELECT ?publication_name (GROUP_CONCAT(DISTINCT ?interest_name; SEPARATOR=", ") AS ?interests)
WHERE {{
    ?article dc:creator ?author .
    ?author foaf:name ?author_name .
    ?author ns1:aPourInteret ?interet .
    ?interet ns1:interetNom ?interest_name .
    ?article ns1:publieDans ?publication .
    ?publication ns1:publicationNom ?publication_name .
    
    FILTER(BOUND(?interest_name) && ?interest_name != "")
}}
GROUP BY ?publication_name

        """
    )

    for i, a in requete:
        publication_name = i 
        interests = a 
        
        print(f"Publication: {publication_name}")
        print(f"Intérêts: {interests}")
        print("-" * 80)  

'''
Requete qui trouve des paires d'auteurs qui ont publié dans les memes publications

'''

def coauteur_publication():

    requete = g.query(
    """
        SELECT ?author1name ?author2name (GROUP_CONCAT(DISTINCT ?publication_name; SEPARATOR=", ") AS ?publications)
        WHERE {{
        ?article1 ns1:publieDans ?publication .
        ?article1 dc:creator ?author1 .
        ?article2 ns1:publieDans ?publication .
        ?article2 dc:creator ?author2 .
        
        ?author1 foaf:name ?author1name .
        ?author2 foaf:name ?author2name .
        ?publication ns1:publicationNom ?publication_name .

        FILTER(?author1 != ?author2)
        }}
        GROUP BY ?author1name ?author2name

    """
)

    for auteur1, auteur2, publication in requete:

        print(f"Co-auteurs : {auteur1.value, auteur2.value}")
        print(f"Publication commune : {publication}")
        print("-" * 80)  

'''
Requete pour trouver les affiliations liées aux auteurs les plus influents (en fonction du h-index)

'''

def affiliations_h_index_eleve():
    requete = g.query(
        """SELECT DISTINCT ?authorName ?affiliationName ?hIndex
    WHERE {{
    ?author <http://example.org/ontology/semantic_scholar/affilieA> ?affiliation .
    ?author <http://xmlns.com/foaf/0.1/name> ?authorName .
    ?affiliation <http://example.org/ontology/semantic_scholar/affiliationNom> ?affiliationName .
    ?author <http://example.org/ontology/semantic_scholar/auteurHIndex> ?hIndex .
    FILTER(?hIndex > 50) 
    }} ORDER BY DESC(?hIndex)

        """
    )

    print("Voici la liste des auteurs possédant un haut h-index et leur affiliations : ")
    for authorName, affiliationName, hIndex in requete:
        print(f"Auteur: {authorName.value}, Affiliation: {affiliationName.value}, H-index: {hIndex.value}")
        print("-" * 80)

'''
Requete qui renvoie la liste des affiliations qui sont plus ou moins influentes dans un domaine 
Retourne le nombre d'auteurs affiliés à chaque affiliation et ayant un intérêt lié au domaine spécifié

'''

def affiliation_influente_domaine():

    domaine = str(input("Entrer un domaine d'études : "))
    requete = g.query(
    """
        SELECT ?affiliationName ?localisation (COUNT(?author) AS ?authorCount)
        WHERE {
            ?author <http://example.org/ontology/semantic_scholar/aPourInteret> ?interet .
            ?interet <http://example.org/ontology/semantic_scholar/interetNom> ?interetName .
            ?author <http://example.org/ontology/semantic_scholar/affilieA> ?affiliation .
            ?affiliation <http://example.org/ontology/semantic_scholar/affiliationNom> ?affiliationName .
            ?affiliation <http://example.org/ontology/semantic_scholar/affiliationLocalisation> ?localisation .

            FILTER(CONTAINS(LCASE(?interetName), "%s"))
        }
        GROUP BY ?affiliationName ?localisation
        ORDER BY DESC(?authorCount)
    """ %domaine
)

    for affiliation, localisation, count in requete:

        print(f"Affiliation : {affiliation}")
        print(f"Localisation : {localisation}")
        print(f"Influence : {count}")
        print("-" * 80)  

choix_fonction = int(input("Quelle requete voulez-vous tester ? : \n 1 - Affichage des publications liées à leur domaine \n 2 - Affichage d'auteurs ayant publié dans les mêmes plublications \n 3 - Affichage des affiliations liées aux auteurs influents \n 4 - Affichage de l'influence d'une affiliation en fonction d'un domaine spécifique \n Votre choix :  "))

if choix_fonction == 1:

    publication_interet()

elif choix_fonction == 2:

    coauteur_publication()

elif choix_fonction == 3:

    affiliations_h_index_eleve()

elif choix_fonction == 4:

    affiliation_influente_domaine()