import requests
import json
from bs4 import BeautifulSoup

# Variables utilisées dans le programme
cfg_file = "liste.cfg"
result = {}
film_input = ""

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
    html_response = ""
    # Récupération de la méthode HTTP et de l'URL
    method, url = config[key].split(",")[0], config[key].split(",")[1]
    # Récupération du payload si besoin
    if method == "POST":
        payload = {config[key].split(",")[2]: film_input}
        html_response = get_data(method, url, payload)
    else:
        html_response = get_data(method, url)
    # On récupère les div contenant les informations du film
    list_films = html_response.find("div", {"class": "column1"}).find_all(
        "div", id="hann"
    )
    # Si plusieurs films sont trouvés, on demande à l'utilisateur de choisir
    if len(list_films) > 1:
        print("Plusieurs films trouvés")
        # Boucle sur les films trouvés pour que l'utilisateur choisisse
        for index, div in enumerate(list_films, start=1):
            result[div.a.text.strip()] = div.a.get("href")
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
            result[list_films[0].a.text.strip()] = list_films[0].a.get("href")
            print(list_films[0].a.text.strip())
