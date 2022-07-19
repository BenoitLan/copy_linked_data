from inspect import Parameter
from webbrowser import get
from subprocess import call
from numpy import empty, full, mat
import requests
import re

# this method gives back the newest URL for the changeset .osm files and the latest .osm number
def Choose_area():

    # search URL pieces until .osm files are found.
    URL = "http://download.openstreetmap.fr/replication"
    waarde = True
    while(waarde):
        page = requests.get(URL)
        regex = """href="([a-z]\S+|\d+)\/"."""
        match = re.findall(regex, page.text)

        if(len(match) == 0):
            print("choose .osm file")
            break

        print("Choose between: ", match)
        paramater = input("choose first parameter: ")

        while not paramater in match:
            print(len(match))
            print("parameter nog in list... try again")
            paramater = input("choose first parameter: ")
        
        URL_new = URL + "/" + paramater
        print(URL_new)
        URL = URL_new

    # select .osm file
    page = requests.get(URL)
    regex = """href="(\d{3}.osc.gz)"""
    match = re.findall(regex, page.text)
    print(match)

    print("Choose between: ", match)
    paramater = input("choose first parameter: ")

    while not paramater in match:
        print(len(match))
        print("parameter nog in list... try again")
        paramater = input("choose first parameter: ")

    full_url = URL + "/" + paramater
    print(full_url)
    file_name = paramater
    return full_url, file_name


def download_area_osm_file():
    url, file_name = Choose_area()
    print(url, file_name)
    call(["wget", url]) # download latest .osm file
    call(["gunzip", file_name]) # extract latest .osm file
    

download_area_osm_file()




