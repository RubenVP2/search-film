import requests
from bs4 import BeautifulSoup

cfg_file = "liste.cfg"

def read_cfg_file(file):
    """
    Reads the config file and returns a dictionary
    """
    config = {}
    with open(file, 'r') as cfg_file:
        for line in cfg_file:
            if line.startswith('#') or line.startswith('\n'):
                continue
            else:
                key, value = line.split('=')
                config[key] = value.rstrip('\n')
    return config

def get_data(method, url, payload=None):
    """
    Make http request and get data from the DOM element
    """
    response = ""
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        print(payload)
        response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

config = read_cfg_file(cfg_file)

for key in config:
    method, url = config[key].split(',')[0], config[key].split(',')[1]
    if method == 'POST':
        payload = { config[key].split(',')[2]: 'le+réveil+de+la+forc'}
        html_response = get_data(method, url, payload)
        html_response = get_data(method, url)
        list_films = html_response.find('div', {'class': 'column1'}).find_all('div', id='hann')
    for div in list_films:
        print(div.a.text)