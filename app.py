import requests
import argparse
import re
import os
from bs4 import BeautifulSoup

# Variables utilisées dans le programme
cfg_file = "liste.cfg"
result_from_search = {}
final_result = {}
film_input = ""

# Lambda pour nettoie la console
clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")


def affichage_initial():
    """
    Demande à l'utilisateur de saisir le nom du film à rechercher,
    tant qu'il n'a pas saisi un nom valide (pas de chiffres, pas de caractères spéciaux, etc.)
    """
    while True:
        film_input = input("Saisissez le nom du film à rechercher : ")
        if film_input.isdigit() or len(film_input) < 3:
            print("Le nom du film doit être composé de 3 caractères minimum.")
        else:
            # Lecture du fichier de configuration
            config = read_cfg_file(cfg_file)
            get_movie_url(config=config, film_input=film_input)
            break
    affichage_final()


def affichage_final():
    # Affichage des résultats finaux
    clearConsole()
    print("---------- RESULTATS ----------")
    # Si aucun film n'a été trouvé on demande à l'utilisateur s'il veut rechercher un autre film
    if len(final_result) == 0:
        print("Aucun résultat n'a été trouvé.")
        print("Voulez-vous saisir un autre film ? (O/N)")
        answer = input()
        switch = {"o": True, "O": True, "n": False, "N": False}
        if answer in switch:
            if switch[answer]:
                affichage_initial()
            else:
                exit()
        else:
            print("Veuillez saisir O ou N.")
    else:
        # Affichage des liens de tous les films trouvés
        for key in final_result:
            print(key.upper(), ">", final_result[key])
            print("-------------------------------")
        exit()


def read_cfg_file(file):
    """
    Lit le fichier de configuration et retourne un dictionnaire
    """
    config = {}
    with open(file, "r") as cfg_file:
        for line in cfg_file:
            if line.startswith("#") or line.startswith("\n"):
                continue
            else:
                key, value = line.split("=")
                config[key] = value.rstrip("\n")
    return config


def get_data(method, url, payload=None, params=None):
    """
    Execute une requete HTTP et récupère le DOM HTML
    """
    response = ""
    if method == "GET":
        if params is not None:
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
    elif method == "POST":
        response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def get_movie_url(config: dict, film_input: str):
    # Boucle sur chaque site présent dans le fichier liste.cfg
    for idx, key in enumerate(config, start=1):
        # Vide le dictionnaire de résultat
        result_from_search.clear()
        html_response_film_searched = ""
        config_array = config[key].split(",")
        # Récupération de la méthode HTTP et de l'URL
        method, url = config_array[0], config_array[1]
        # Récupération des résultats de recherche
        if method == "POST":
            payload = {config_array[2]: film_input}
            html_response_film_searched = get_data(method, url, payload)
        else:
            params = {config_array[2]: film_input}
            html_response_film_searched = get_data(method, url, params=params)
        # On récupère la div contenant les div des résultats
        params_find = config_array[3].split(":")
        list_films = html_response_film_searched.find(
            params_find[0], {params_find[1]: params_find[2]}
        )
        if config_array[4].split(":")[1] == "id":
            list_films = list_films.find_all(
                config_array[4].split(":")[0], id=config_array[4].split(":")[2]
            )
        else:
            list_films = list_films.find_all(
                config_array[4].split(":")[0], class_=config_array[4].split(":")[2]
            )
        print("--------", idx, "/", len(config), key.upper(), "--------")
        # Si plusieurs films sont trouvés, on demande à l'utilisateur de choisir
        if len(list_films) > 1:
            print("Plusieurs films trouvés")
            # Boucle sur les films trouvés pour que l'utilisateur choisisse
            for index, div in enumerate(list_films, start=1):
                result_from_search[div.a.text.strip()] = div.a.get("href")
                print(index, " - ", div.a.text.strip())
            film_choice = ""
            while True:
                """
                Tant que l'utilisateur n'a pas saisi un nombre valide,
                on lui demande de le saisir à nouveau jusqu'à ce que l'utilisateur saisisse
                un nombre valide entre 1 et le nombre de films trouvés
                """
                try:
                    choice = int(input("Quel fim choisis-tu ? : "))
                    if choice > len(list_films) or choice < 1:
                        print("Ce film n'existe pas")
                        continue
                    else:
                        film_choice = list_films[choice - 1].a.get("href")
                        break
                except ValueError:
                    print("Ce film n'existe pas")
                    continue
        else:
            # Test si au moins un film est trouvé
            if len(list_films) == 0:
                print("Aucun film trouvé")
                break
            else:
                print("Un seul film trouvé")
                print(list_films[0].a.text.strip())
                film_choice = list_films[0].a.get("href")
        # Si le lien ne possède pas l'url de base, on l'ajoute
        if config_array[5] != "":
            html_response_film_selected = get_data("GET", config_array[5] + film_choice)
        else:
            html_response_film_selected = get_data("GET", film_choice)
        html_response_iframe = ""
        # S'il y a une utilisation d'iframe, on doit récupérer le contenu de l'iframe
        if html_response_film_selected.find("iframe"):
            html_response_iframe = get_data(
                "GET",
                html_response_film_selected.find_all("iframe")[
                    int(config_array[6]) - 1
                ].get("src"),
            )
        # S'il faut réaliser un click pour afficher le film, on le fait
        if config_array[7] == "true":
            on_click = html_response_iframe.find("body").get("onclick")
            final_result[key] = re.findall(r"\'.*\'", on_click)[0]
        else:
            final_result[key] = html_response_film_selected.find_all("iframe")[
                int(config_array[6]) - 1
            ].get("src")


# Récupération des paramètres
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--film", help="Le film à rechercher")
args = parser.parse_args()
if args.film is None:
    affichage_initial()
else:
    config = read_cfg_file(cfg_file)
    get_movie_url(config=config, film_input=args.film)
    affichage_final()
    exit()