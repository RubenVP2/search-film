import requests
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


# Demander à l'utilisateur de saisir le nom du film à rechercher, tant qu'il n'a pas saisi un nom valide (pas de chiffres, pas de caractères spéciaux, etc.)
while True:
    film_input = input("Saisissez le nom du film à rechercher : ")
    if film_input.isdigit() or len(film_input) < 3:
        print("Le nom du film doit être composé de 3 caractères minimum.")
    else:
        break


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


# Lecture du fichier de configuration
config = read_cfg_file(cfg_file)


def get_data(method, url, payload=None):
    """
    Execute une requete HTTP et récupère le DOM HTML
    """
    response = ""
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        print(payload)
        response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


# Boucle sur chaque site présent dans le fichier liste.cfg
for key in config:
    # Vide le dictionnaire de résultat
    result_from_search.clear()
    html_response_film_searched = ""
    config_array = config[key].split(",")
    # Récupération de la méthode HTTP et de l'URL
    method, url = config_array[0], config_array[1]
    # Récupération du payload si besoin
    if method == "POST":
        payload = {config_array[2]: film_input}
        html_response_film_searched = get_data(method, url, payload)
    else:
        html_response_film_searched = get_data(method, url)
    # On récupère les div contenant les informations du film
    list_films = html_response_film_searched.find("div", {"class": "column1"}).find_all(
        "div", id="hann"
    )
    print("--------", key.upper(), "--------")
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
                if choice > len(list_films):
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
        else:
            print("Un seul film trouvé")
            print(list_films[0].a.text.strip())
            film_choice = list_films[0].a.get("href")
    # Si le lien ne possède pas l'url de base, on l'ajoute
    if config_array[3] != "":
        html_response_film_selected = get_data("GET", config_array[3] + film_choice)
    else:
        html_response_film_selected = get_data("GET", film_choice)
    html_response_iframe = ""
    # S'il y a une utilisation d'iframe, on doit récupérer le contenu de l'iframe
    if html_response_film_selected.find("iframe"):
        html_response_iframe = get_data(
            "GET", html_response_film_selected.find("iframe").get("src")
        )
    # S'il faut réaliser un click pour afficher le film, on le fait
    if config_array[4] != "":
        on_click = html_response_iframe.find("body").get("onclick")
        final_result[key] = re.findall(r"\'.*\'", on_click)[0]

clearConsole()
print("-------- RESULTATS --------")
# Affichage des liens de tous les films trouvés
for key in final_result:
    print(key.upper(), ":", final_result[key])