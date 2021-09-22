from Models import Site
import requests
import argparse
import re
import os
from bs4 import BeautifulSoup
from rich import print
from rich.table import Table
from rich.console import Console
from time import sleep

# Variables utilisées dans le programme
cfg_file = "liste.cfg"
result_from_search = {}
final_result = {}
film_input = ""
console = Console()


def get_argument():
    """
    Récupère les arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--film", help="Le film à rechercher")
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Sauvegarde le résultat dans un fichier",
    )
    return parser.parse_args()


def affichage_initial(need_save=None):
    """
    Demande à l'utilisateur de saisir le nom du film à rechercher,
    tant qu'il n'a pas saisi un nom valide (pas de chiffres, pas de caractères spéciaux, etc.)
    """
    while True:
        film_input = console.input(
            "[bold green]Saisissez le nom du film à rechercher : "
        )
        if film_input.isdigit() or len(film_input) < 3:
            console.print(
                "[bold red]Le nom du film doit être composé de 3 caractères minimum."
            )
            continue
        else:
            # Lecture du fichier de configuration
            config = read_cfg_file(cfg_file)
            get_movie_url(config=config, film_input=film_input)
            affichage_final()
            break
    if need_save is not None:
        save_result(file_name="results.txt", film=film_input)


def affichage_final():
    # Affichage des résultats finaux
    console.clear()
    # Si aucun film n'a été trouvé on demande à l'utilisateur s'il veut rechercher un autre film
    if len(final_result) == 0:
        console.print("[bold red]Aucun résultat n'a été trouvé...[/] :disappointed:")
        answer = console.input(
            "[bold green]Voulez-vous saisir un autre film ? (O/N) :relieved:"
        )
        while True:
            switch = {"o": True, "O": True, "n": False, "N": False}
            if answer in switch:
                if switch[answer]:
                    console.clear()
                    # Si l'argument save est présent, on l'utilise pour sauvegarder le résultat
                    if args.save is not None:
                        affichage_initial(need_save=True)
                    else:
                        affichage_initial()
                    break
                else:
                    console.print("[bold green]Au revoir ![/] :wave:")
                    sleep(0.5)
                    exit()
            else:
                # On demande à l'utilisateur de saisir une réponse valide
                console.print("[bold cyan]Veuillez saisir O ou N.")
                answer = console.input("[bold green]Nouvelle chance ! :smile:")
                continue
    else:
        table_results = Table(
            title="[not italic]:page_with_curl:[/] Résultats [not italic]:page_with_curl:[/]",
            show_lines=True,
        )
        table_results.add_column("Site", justify="right", style="cyan", no_wrap=True)
        table_results.add_column("Lien", justify="left", style="magenta")
        # Affichage des liens de tous les films trouvés
        for key in final_result:
            table_results.add_row(key.upper(), final_result[key], style=" magenta")
        console.print(table_results)
        exit()


def init_console_status():
    """
    Initialise la console avec le status recherche en cours ....
    """
    with console.status("[bold green]Recherche en cours...") as status:
        # Si aucun paramètre n'est passé, on lance l'application en mode interactif
        if args.film is None:
            if args.save is None:
                affichage_initial()
            else:
                affichage_initial(need_save=True)
        else:
            # On lance le script en fonction du paramètre passé
            config = read_cfg_file(cfg_file)
            get_movie_url(config=config, film_input=args.film)
            if args.save is not None:
                save_result(file_name="results.txt", film=args.film)
        # Une fois le script terminé, on change le status de la console
        status.update(
            status="[bold cyan] Récupération des liens",
            spinner="point",
            spinner_style="cyan",
        )
        sleep(1.5)
    affichage_final()
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
    # Trim des espaces en début et fin de chaîne
    film_input = film_input.strip()
    # Boucle sur chaque site présent dans le fichier liste.cfg
    for idx, key in enumerate(config, start=1):
        # Vide le dictionnaire de résultat
        result_from_search.clear()
        html_response_film_searched = ""
        # Création de l'objet Site
        site = Site(config[key])
        # Récupération de la méthode HTTP et de l'URL
        method, url = site.method_http_recherche, site.url_recherche
        # Récupération des résultats de recherche
        if method == "POST":
            payload = {site.param_recherche: film_input}
            html_response_film_searched = get_data(method, url, payload)
        else:
            params = {site.param_recherche: film_input}
            html_response_film_searched = get_data(method, url, params=params)
        # On récupère la div contenant les div des résultats
        params_find = site.element_dom_ensemble_resultat_recherche.split(":")
        list_films = html_response_film_searched.find(
            params_find[0], {params_find[1]: params_find[2]}
        )
        if site.element_dom_resultat_recherche.split(":")[1] == "id":
            list_films = list_films.find_all(
                site.element_dom_resultat_recherche.split(":")[0],
                id=site.element_dom_resultat_recherche.split(":")[2],
            )
        else:
            list_films = list_films.find_all(
                site.element_dom_resultat_recherche.split(":")[0],
                class_=site.element_dom_resultat_recherche.split(":")[2],
            )
        console.print(
            f"[bold magenta]-------- {idx} / {len(config)} {key.upper()} --------"
        )
        # Si plusieurs films sont trouvés, on demande à l'utilisateur de choisir
        if len(list_films) > 1:
            console.print("[bold cyan] Plusieurs films trouvés :grinning: :")
            # Boucle sur les films trouvés pour que l'utilisateur choisisse
            for index, div in enumerate(list_films, start=1):
                result_from_search[div.a.text.strip()] = div.a.get("href")
                console.print(f"[bold magenta]{index} - {div.a.text.strip()}")
            film_choice = ""
            while True:
                """
                Tant que l'utilisateur n'a pas saisi un nombre valide,
                on lui demande de le saisir à nouveau jusqu'à ce que l'utilisateur saisisse
                un nombre valide entre 1 et le nombre de films trouvés
                """
                try:
                    choice = int(
                        console.input("[bold green]Quel fim choisis-tu ? :eyes: : ")
                    )
                    if choice > len(list_films) or choice < 1:
                        console.print("[bold red]Ce film n'existe pas")
                        continue
                    else:
                        console.print(":ok_hand:")
                        film_choice = list_films[choice - 1].a.get("href")
                        break
                except ValueError:
                    console.print("[bold red]Ce film n'existe pas")
                    continue
        else:
            # Test si au moins un film est trouvé
            if len(list_films) == 0:
                break
            else:
                console.print("[bold cyan]Film trouvé :ok_hand:")
                console.print(list_films[0].a.text.strip(), style="italic cyan")
                film_choice = list_films[0].a.get("href")
        # Si le lien ne possède pas l'url de base, on l'ajoute
        if site.url_base != "":
            html_response_film_selected = get_data("GET", site.url_base + film_choice)
        else:
            html_response_film_selected = get_data("GET", film_choice)
        html_response_iframe = ""
        # S'il y a une utilisation d'iframe, on doit récupérer le contenu de l'iframe
        if html_response_film_selected.find("iframe"):
            html_response_iframe = get_data(
                "GET",
                html_response_film_selected.find_all("iframe")[site.nb_iframe - 1].get(
                    "src"
                ),
            )
        # S'il faut réaliser un click pour afficher le film, on le fait
        if site.necessite_click:
            on_click = html_response_iframe.find("body").get("onclick")
            final_result[key] = re.findall(r"\'.*\'", on_click)[0].replace("'", "")
        else:
            final_result[key] = html_response_film_selected.find_all("iframe")[
                site.nb_iframe - 1
            ].get("src")


def save_result(file_name: str, film: str):
    """
    Sauvegarde le résultat dans un fichier
    """
    with open(file_name, "a") as f:
        f.write("----------- " + film + " -----------\n")
        for key in final_result:
            f.write(key.upper() + " > ")
            f.write(final_result[key] + "\n")
        f.close()


# Début du script principal --------------------------------------------------- #
args = get_argument()
console.clear()
init_console_status()