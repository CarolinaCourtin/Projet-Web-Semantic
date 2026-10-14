import json
import rdflib
from rdflib import URIRef, Literal, XSD, Namespace
import os
import uuid
import requests
import random

# Fonction pour créer les entités d'auteurs et leurs liens dans la base de données

def code_auteurs():

    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    namespace = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")

    auteurs_h_json = []

    fichiers_auteurs = ["auteurs.json", "auteurs2.json", "auteurs3.json", "auteurs4.json"]

    for fichier in fichiers_auteurs:

        json_file_path = os.path.join(os.path.dirname(__file__), "Raw_data", fichier)

        with open(json_file_path, 'r', encoding='utf-8') as json_file:

            data = json.load(json_file)

            for personne in data["profiles"]:

                # ---------------- AUTEURS ------------------------------------------

                print(personne["author_id"])
                auteur_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{personne['author_id']}")

                g.add((auteur_uri, rdflib.RDF.type, namespace.Auteur))

                print(personne["name"])
                g.add((auteur_uri, foaf.name, Literal(personne['name'], datatype=XSD.string)))

                print(f"Auteur ID : {personne['author_id']}")

                g.add((auteur_uri, namespace.auteurId, rdflib.Literal(personne["author_id"])))
            
        
                try:
                    if "email" in personne:
                        print(personne["email"])
                        g.add((auteur_uri, foaf.mbox, Literal(personne['email'], datatype=XSD.string)))
                    else:
                        print("Email manquant pour cet auteur, ajout de 'mail non renseigné'.")
                        g.add((auteur_uri, foaf.mbox, Literal("mail non renseigné", datatype=XSD.string)))
                except KeyError as e:
                    print(f"Erreur lors de l'ajout de l'email pour {personne['author_id']}: {e}")
                    g.add((auteur_uri, foaf.mbox, Literal("mail non renseigné", datatype=XSD.string)))

                auteur_id = personne["author_id"]

                # -------------- h_index ------------------------------  

                url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={auteur_id}"
                
                key = "9b68b4e23ddaf32f4fac35cb36ae62a1f6641f010a8625cb5890f82f18334d29"

                url_with_key = f"{url}&api_key={key}"

                requete = requests.get(url_with_key)

                if requete.status_code == 200:
                    res = requete.json()
                    print(res)
                else:

                    print(f"Erreur : {requete.status_code}, {requete.text}")

                data = requete.json()

                indice_h = data["cited_by"]["table"][1]["h_index"]["all"]
                g.add((auteur_uri, namespace.auteurHIndex, Literal(indice_h, datatype=XSD.int)))

                

                new_h = {
                    "author_id": auteur_id,
                    "h_index": indice_h
                }

                auteurs_h_json.append(new_h)

                with open("h_index.json", "w") as f:
                    json.dump(auteurs_h_json, f, indent=4)


    # ---------------- AFFILIATIONS ------------------------------------------

           
                existing_affiliation = None
                for aff_uri in g.subjects(namespace.affiliationNom, Literal(personne["affiliations"], datatype=XSD.string)):
                    existing_affiliation = aff_uri
                    break

                if existing_affiliation:
                    
                    print(f"Affiliation existante trouvée : {existing_affiliation}")
                else:
                    
                    unique_aff_id = "AFFILIATION" + str(uuid.uuid4())
                    affiliation_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{unique_aff_id}")
                    print(f"Nouvelle affiliation ajoutée avec l'ID {unique_aff_id}")
                    

                    g.add((affiliation_uri, rdflib.RDF.type, namespace.Affiliation))
                    g.add((affiliation_uri, namespace.affiliationNom, Literal(personne["affiliations"], datatype=XSD.string)))
                    g.add((affiliation_uri, namespace.affiliationId, Literal(unique_aff_id, datatype=XSD.string)))
                    
                    existing_affiliation = affiliation_uri

                auteur_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{personne['author_id']}")
                g.add((auteur_uri, namespace.affilieA, existing_affiliation))


        # ---------------- INTERETS ------------------------------------------


                print("Interests : ")

                try:
                    if "interests" in personne:
                        for inte in personne["interests"]:
                            print(inte["title"])

                            existing_interest = None
                            for interet_uri in g.subjects(namespace.interetNom, Literal(inte["title"], datatype=XSD.string)):
                                existing_interest = interet_uri
                                break  

                            if existing_interest:
                                print(f"L'intérêt '{inte['title']}' existe déjà.")
                                g.add((auteur_uri, namespace.aPourInteret, existing_interest))
                            else:

                                unique_id = "INTERET" + str(uuid.uuid4())
                                interet_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{unique_id}")
                                g.add((interet_uri, rdflib.RDF.type, namespace.Interet))
                                g.add((interet_uri, namespace.interetNom, Literal(inte["title"], datatype=XSD.string)))
                                g.add((interet_uri, namespace.interetId, Literal(unique_id, datatype=XSD.string)))
                                g.add((auteur_uri, namespace.aPourInteret, interet_uri))

                    else:
                        print("Pas d'intérêts pour cet auteur.")
                except Exception as e:
                    print(f"Erreur lors du traitement des intérêts pour {personne['author_id']}: {e}")
                continue   

            g.serialize(ontho_file_path, format="turtle")

            print("Ontologie avec auteurs et affiliations ajoutées a été sauvegardée dans 'research_onthology.ttl'")

# Ajout des identifiants pour les auteurs 

def retrieve_ids():

    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    NS1 = Namespace("http://example.org/ontology/semantic_scholar/")

    auteur_ids = []
    for s, p, o in g.triples((None, NS1.auteurId, None)):
        auteur_ids.append(str(o))

    print(len(auteur_ids))

    print("Liste des auteurId :")
    for id in auteur_ids:
        print(id)

# Fonction pour ajouter les articles dans la base de données

def retrieve_articles():

    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    NS1 = Namespace("http://example.org/ontology/semantic_scholar/")  
    foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")

    auteur_ids = []
    for s, p, o in g.triples((None, NS1.auteurId, None)):
        auteur_ids.append(str(o))

    for id in auteur_ids:

        url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={id}"
        key = "9b68b4e23ddaf32f4fac35cb36ae62a1f6641f010a8625cb5890f82f18334d29"


        json_file = "articles.json"
        url_with_key = f"{url}&api_key={key}"

        requete = requests.get(url_with_key)

        requete_json = requete.json()

        """

        with open(json_file, "w") as json_fileee:
            
            json.dump(requete_json, json_fileee, indent=4)

        """

        for article in requete_json["articles"]:
            titlee = article['title']
            year = article['year']
            publication = article.get('publication', None)
            authors = article['authors']
            link = article['link']
            citations = article['cited_by']['value']
            

            article_exists = False
            article_uri = None

            for s, p, o in g.triples((None, dc.title, Literal(titlee, datatype=XSD.string))):
                article_exists = True
                article_uri = s  
                break

            if article_exists:
                print(f"L'article '{titlee}' existe déjà dans le graphe.")
            else:

                unique_art_id = "ARTICLE" + str(uuid.uuid4())
                article_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{unique_art_id}")


                g.add((article_uri, rdflib.RDF.type, NS1.Article))
                g.add((article_uri, dc.identifier, Literal(unique_art_id, datatype=XSD.string)))
                g.add((article_uri, dc.title, Literal(titlee, datatype=XSD.string)))
                g.add((article_uri, dc.date, Literal(year, datatype=XSD.integer)))
                g.add((article_uri, NS1.allAuthors, Literal(authors, datatype=XSD.string)))
                g.add((article_uri, NS1.articleLien, Literal(link, datatype=XSD.string)))
                g.add((article_uri, NS1.articleNbCitation, Literal(citations, datatype=XSD.string)))
                print(f"Nouvel article ajouté : {titlee}")

                # --------------------- PUBLICATION ---------------------------------------

                if publication:

                    publication_exists = False
                    publication_uri = None
                    for s, p, o in g.triples((None, NS1.publicationNom, Literal(publication, datatype=XSD.string))):
                        publication_exists = True
                        publication_uri = s
                        break

                    if publication_exists:
                        print(f"La publication '{publication}' existe déjà dans le graphe.")
                    else:

                        unique_pub_id = "PUBLICATION" + str(uuid.uuid4())
                        publication_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{unique_pub_id}")

                        g.add((publication_uri, rdflib.RDF.type, NS1.Publication))
                        g.add((publication_uri, NS1.publicationNom, Literal(publication, datatype=XSD.string)))
                        print(f"Nouvelle publication ajoutée : {publication}")

                    if publication_uri:
                        g.add((article_uri, NS1.publieDans, publication_uri))

            # ------------- AUTEUR ------------------------------------------

            auteur_uri = None
            for s, p, o in g.triples((None, NS1.auteurId, Literal(id))):
                auteur_uri = s  
                break

            if auteur_uri:
                print(f"Auteur identifié : {auteur_uri}")

                g.add((article_uri, dc.creator, auteur_uri))
            else:
                print(f"L'auteur avec l'id '{id}' n'existe pas encore dans le graphe.")

    g.serialize(ontho_file_path, format="turtle")

            
    '''unique_auth_id = "AUTHOR" + str(uuid.uuid4())
    auteur_uri = URIRef(f"http://example.org/ontology/semantic_scholar/{unique_auth_id}")

    g.add((auteur_uri, rdflib.RDF.type, NS1.Auteur))
    g.add((auteur_uri, NS1.auteurId, Literal(id, datatype=XSD.string)))
    g.add((auteur_uri, foaf.name, Literal(article['authors'], datatype=XSD.string)))  # Optionnel : nom de l'auteur
    print(f"Nouvel auteur ajouté avec l'id : {id}")

    g.add((article_uri, dc.creator, auteur_uri))'''


# Ajout des affiliations dans la base de données

def affiliations():

    NS1 = Namespace("http://example.org/ontology/semantic_scholar/")
    ontho_file_path = os.path.join("RDF", "base1", "semantic_scholar1.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    for s, p, o in g.triples((None, NS1.affilieA, None)):
        print(f"Auteur URI: {s}")
        print(f"Affiliation: {o}")

# Problème de types : transformation des nombres de citations en integer

def citations_to_int():

    NS1 = Namespace("http://example.org/ontology/semantic_scholar/")
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    for s, p, o in g.triples((None, NS1.articleNbCitation, None)):
        print(f"{s} -> = {o}")
        
        if isinstance(o, rdflib.Literal):
            try:
                int_value = int(o)
                print(f"Valeur convertie : {int_value}")
                
                new_literal = Literal(int_value, datatype=XSD.integer)
                
                g.remove((s, p, o))

                g.add((s, p, new_literal))
                
                print(f"Le triplet a été mis à jour avec la nouvelle valeur {new_literal}")
                
            except ValueError:
                print(f"Impossible de convertir {o} en int")

    g.serialize(ontho_file_path, format="turtle")


# Ajout des identifiants de publication 

def add_publication_id():

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    xsd = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
    
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")
    
    for s, p, o in g.triples((None, NS1.publicationNom, None)):

        publication_id = str(s).split("/")[-1]
        
        g.add((s, NS1.publicationId, rdflib.Literal(publication_id, datatype=xsd.string)))
    
    g.serialize(ontho_file_path, format="turtle")
    print("Attribut 'publicationId' ajouté avec succès!")


# Problème de type : transformation de la date en xsd.year au lien d'un integer

def update_date():

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    xsd = rdflib.XSD
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")
    
    for s, p, o in g:
        if p in {NS1.publicationDate, dc.date}:
            try:
                newdate = None

                if isinstance(o.value, str) and o.value.isdigit():

                    year = int(o.value)
                elif isinstance(o.value, int):
                    year = o.value
                else:

                    if o.datatype == xsd.date:
                        year = o.toPython().year
                    elif o.datatype == xsd.gYear:
                        year = int(o)
                    else:
                        year = None


                if year is not None and 1850 <= year <= 2024:
                    newdate = rdflib.Literal(str(year), datatype=xsd.gYear)
                else:

                    random_year = random.randint(1990, 2024)
                    newdate = rdflib.Literal(str(random_year), datatype=xsd.gYear)
                    print(f"Date invalide ({o}). Nouvelle date assignée : {random_year}")

                g.remove((s, p, o))
                g.add((s, p, newdate))
                print(f"Le triplet a été mis à jour avec la nouvelle valeur {newdate}")

            except Exception as e:
                print(f"Impossible de convertir ou de mettre à jour la date {o}: {e}")
    

    output_file_path = os.path.join("semantic_scholar_updated.ttl")
    g.serialize(destination=output_file_path, format="turtle")
    print(f"Graph modifié sauvegardé dans : {output_file_path}")

# Autre fonction pour retourner et convertir les dates de publications en xsd.year

def retrieve_date_publications():

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    xsd = rdflib.XSD
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    new_date = None

    try:

        for s, p, o in g.triples((None, NS1.publicationDate, None)):

            print(o)
            print(f"Old type : {type(o)}")

            int_date = int(o)

            print(f"String conversion : {type(int_date)}")

            if int_date is not None and not 1850 <= int_date <= 2024:

                random_year = random.randint(1990, 2024)
                new_date = rdflib.Literal(int(random_year), datatype=xsd.gYear)
                print(f"Date invalide ({o}). Nouvelle date assignée : {random_year}")

            else:

                new_date = rdflib.Literal(int_date, datatype=xsd.gYear)

                # print(f"Nouvelle date ajoutée : {new_date}")

            g.remove((s, p, o))
            g.add((s, p, new_date))
            print(f"Le triplet a été mis à jour avec la nouvelle valeur {new_date}")


            '''
            # Remplacer l'ancien triplet
            g.remove((s, p, o))
            g.add((s, p, new))
            print(f"Le triplet a été mis à jour avec la nouvelle valeur {new}")'''

    except Exception as e:
                print(f"Impossible de convertir ou de mettre à jour la date {o}: {e}")

    g.serialize(destination=ontho_file_path, format="turtle")

# Problème de type : conversion de la date des articles en xsd.year au lieu d'un integer ou un string

def retrieve_date_article():

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    xsd = rdflib.XSD
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    
    # Charger le fichier RDF
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    new_date = None

    try:

        for s, p, o in g.triples((None, dc.date, None)):

            print(o)
            print(f"Old type : {type(o)}")

            int_date = int(o)

            print(f"String conversion : {type(int_date)}")

            if int_date is not None and not 1850 <= int_date <= 2024:

                random_year = random.randint(1990, 2024)
                new_date = rdflib.Literal(int(random_year), datatype=xsd.gYear)
                print(f"Date invalide ({o}). Nouvelle date assignée : {random_year}")

            else:

                new_date = rdflib.Literal(int_date, datatype=xsd.gYear)

                # print(f"Nouvelle date ajoutée : {new_date}")

            g.remove((s, p, o))
            g.add((s, p, new_date))
            print(f"Le triplet a été mis à jour avec la nouvelle valeur {new_date}")


            '''
            # Remplacer l'ancien triplet
            g.remove((s, p, o))
            g.add((s, p, new))
            print(f"Le triplet a été mis à jour avec la nouvelle valeur {new}")'''

    except Exception as e:
                print(f"Impossible de convertir ou de mettre à jour la date {o}: {e}")

    g.serialize(destination=ontho_file_path, format="turtle")

# Retourne les dates pour vérifier leur type

def test_type_dates():

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    xsd = rdflib.XSD
    dc = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")

    print("Datatypes for articles : ")

    for s, p, o in g.triples((None, dc.date, None)):

            print(o)
            print(f"Type : {type(o)}")

    '''print("Datatypes for publications : ")

    for s, p, o in g.triples((None, NS1.publicationDate, None)):

            print(o)
            print(f"Type : {type(o)}")'''
    
# Test qui retourne la liste d'interets (cleaning)

def retrieve_same_interests():

    inte = []

    NS1 = rdflib.Namespace("http://example.org/ontology/semantic_scholar/")
    # xsd = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
    
    ontho_file_path = os.path.join("semantic_scholar.ttl")
    g = rdflib.Graph()
    g.parse(ontho_file_path, format="turtle")
    
    for s, p, o in g.triples((None, NS1.interetNom, None)): 

        inte.append(o)

        print(f"{len(inte)} : {o}")



# retrieve_date_publications()
# retrieve_date_article()
# update_date()
# retrieve_same_interests()
# citations_to_int()
# code_auteurs()
# retrieve_articles()
# add_publication_id()