from webbrowser import get
from subprocess import call
import requests
import re

def get_minute_state():
    URL = "https://planet.osm.org/replication/minute/state.txt"
    page = requests.get(URL)
    print(page.text, "\n")

# this method gives back the newest URL for the changeset .osm files and the latest .osm number
def get_latest_replication_URL():
    URL1 = "https://planet.osm.org/replication/changesets/"
    page1 = requests.get(URL1)
    regex1 = """(?<=href)(=")(\d+)"""
    match1 =  re.search(regex1, page1.text)
    # print("first: ", match1.group(2))
    URL_new = URL1 + match1.group(2) + "/"

    page2 = requests.get(URL_new)
    regex2 = """(?<=href)(=")(\d+)"""
    match2 =  re.search(regex2, page2.text)
    # print("second", match2.group(2))
    URL_new_new = URL_new + match2.group(2)
    print("latest replication URL: ", URL_new_new)

    page3 = requests.get(URL_new_new)
    regex3 = """(?<=href)(=")(\d+\.osm\S.+)(")"""
    match3 = re.search(regex3, page3.text)
    print("latest .osm file: ", match3.group(2))

    return URL_new_new, match3.group(2)

# this method downloads the latest .osm file of the changesets and extracts it
def download_latest_OSM_file():
    url, osm_file = get_latest_replication_URL()
    full_link = url+"/"+osm_file
    call(["wget", full_link]) # download latest .osm file
    call(["gunzip", osm_file]) # extract latest .osm file
    print(osm_file)
    return osm_file

osm_file_name = download_latest_OSM_file()





