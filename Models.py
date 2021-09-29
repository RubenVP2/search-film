"""
    Classe qui représente un modèle de données. 
    Cette classe représente les paramètres du fichier de configuration liste.cfg
"""


class Site:
    method_http_recherche: str
    url_recherche: str
    param_recherche: str
    element_dom_ensemble_resultat_recherche: str
    element_dom_resultat_recherche: str
    url_base: str
    nb_iframe: int
    url_base_iframe: str
    necessite_click: bool

    # Constructor de la classe
    # @param Tableau qui contient les informations à récupérer
    # @return: None
    def __init__(self, vars_array):
        vars_array = vars_array.split(",")
        self.method_http_recherche = vars_array[0]
        self.url_recherche = vars_array[1]
        self.param_recherche = vars_array[2]
        self.element_dom_ensemble_resultat_recherche = vars_array[3]
        self.element_dom_resultat_recherche = vars_array[4]
        self.url_base = vars_array[5]
        self.nb_iframe = int(vars_array[6])
        self.url_base_iframe = vars_array[7]
        self.necessite_click = self.convert_to_bool(vars_array[8])

    def print_site(self):
        """
        Méthode qui print les informations du site
        @param: None
        @return: None
        """
        #
        print("\n\n")
        print("Method HTTP : " + self.method_http_recherche)
        print("URL : " + self.url_recherche)
        print("Paramètre : " + self.param_recherche)
        print("Element DOM : " + self.element_dom_ensemble_resultat_recherche)
        print("Element DOM resultat : " + self.element_dom_resultat_recherche)
        print("URL Base : " + self.url_base)
        print("Nombre d'iframe : " + str(self.nb_iframe))
        print("URL Base iframe : " + self.url_base_iframe)
        print("Necessite Click : " + str(self.necessite_click))
        print("\n\n")

    def convert_to_bool(self, value: str):
        """
        Méthode qui convertit le paramètre string en booléen
        @param: String qui représente le booléen
        @return: Booléen correspondant au string
        """
        if value == "True":
            return True
        else:
            return False