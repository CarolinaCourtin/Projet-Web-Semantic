## Projet Web Sémantique (Réalisé par Hèlène Moore et Carolina Courtin dans le cadre du cours Web Semantic Technologies au semestre d'automne 2024)

Ce projet est une application en Python qui utilise un graphe RDF pour interroger et analyser des données liées à des publications académiques, des auteurs, et leurs domaines d'intérêt.

## Prérequis
Avant de commencer, vous devez avoir installé Python (version 3.8 minimum) et pip, le gestionnaire de paquets Python.

## Étapes d'installation et d'exécution
Téléchargez les fichiers du projet sur votre machine.

Créez un environnement virtuel pour installer les dépendances du projet. Cela vous permettra de gérer les bibliothèques nécessaires sans affecter votre installation Python globale. Pour ce faire, ouvrez une fenêtre de terminal ou PowerShell et naviguez jusqu'au dossier contenant les fichiers du projet.
Exécutez la commande suivante pour créer un environnement virtuel :

     python -m venv env

Cela créera un dossier env/ dans votre répertoire contenant l'environnement virtuel.
Activez l'environnement virtuel :

Sur Windows : 

     \env\Scripts\activate

Sur Mac/Linux :

     source env/bin/activate

Après l'activation, vous devriez voir quelque chose comme (env) avant votre invite de commande, ce qui signifie que l'environnement virtuel est actif.

Installez les dépendances à partir du fichier requirements.txt :

     pip install -r requirements.txt

Cela installera toutes les bibliothèques nécessaires pour exécuter le projet.

Exécutez le code : Une fois les dépendances installées, vous pouvez exécuter le code Python. Pour cela, lancez la commande : 

     python requetes.py

Si vous avez fini de travailler dans l'environnement virtuel, vous pouvez le désactiver avec la commande :

     deactivate

## Informations sur le code
Le code principal se trouve dans le fichier python "requetes.py". Chaque requete en SPARQL se trouve dans une fonction python particulière que vous pouvez lancer depuis le terminal. 
Vous trouverez également le code qui a permis de créer le début de la base de données à partir des données JSON dans le code "database_code.py". 
Remarque : ce code ne fournit pas la base de données finale, nous avons du l'améliorer sur protege pour vérifier les types, les liens et ajouter les règles SWRL.
