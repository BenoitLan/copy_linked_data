from webbrowser import get
from subprocess import call
import requests
import re
from inspect import Parameter
from numpy import empty, full, mat
import osmium as osm
import pandas as pd
from sqlalchemy import create_engine


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
    return file_name


## START MAIN ##
choice = input("""choose "area" to choose an .osc file chosen by a city or "latest changeset" to get the latest changeset \n""" )
osm_file_name = ""
osc_or_osm = ""
while osm_file_name == "":
    if(choice == "area"):
        osm_file_name = download_area_osm_file()
        print(osm_file_name)
        osc_or_osm = "osc"
    elif(choice == "latest changeset"):
        # download_area_osm_file()
        osm_file_name = download_latest_OSM_file()
        print(osm_file_name)
        osc_or_osm = "osm"
    else: 
        choice = input("invalid input \n")


if(osc_or_osm == "osc"):
    class OSMHandler(osm.SimpleHandler):
        def __init__(self):
            osm.SimpleHandler.__init__(self)
            self.osm_data = []

        def tag_inventory(self, elem, elem_type):
            if elem_type == "way":
                for tag in elem.tags:
                    self.osm_data.append([elem_type, 
                                        elem.id, 
                                        elem.version,
                                        elem.visible,
                                        pd.Timestamp(elem.timestamp),
                                        elem.uid,
                                        elem.user,
                                        elem.changeset,
                                        "None",
                                        "None",
                                        tag.k, 
                                        tag.v])

            if elem_type == "node":
                if "invalid" not in str(elem.location):
                    lctn = str(elem.location).split("/")
                else:
                    lctn = [None, None]
                self.osm_data.append([elem_type, 
                                        elem.id, 
                                        elem.version,
                                        "NaN",
                                        pd.Timestamp(elem.timestamp),
                                        elem.uid,
                                        elem.user,
                                        elem.changeset,
                                        lctn[0],
                                        lctn[1],                                    
                                        "None",
                                        "None"
                                    ])

        def way(self, w):
            self.tag_inventory(w, "way")

        def node(self, n):
            self.tag_inventory(n, "node")

    osmhandler = OSMHandler()
    # scan the input file and fills the handler list accordingly
    osmhandler.apply_file(osm_file_name[0:7])

    # transform the list into a pandas DataFrame
    data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid', 'user', 'chgset',
                    'lon', 'lat',
                    'tagkey', 'tagvalue']

    df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)

    print(df_osm.tail(50))

elif(osc_or_osm == "osm") : 
    # https://askubuntu.com/questions/20414/find-and-replace-text-within-a-file-using-commands
    # sed -i 's/original/new/g' file.txt
    # Explanation:

    # sed = Stream EDitor
    # -i = in-place (i.e. save back to the original file)
    # The command string:

        # s = the substitute command
        # original = a regular expression describing the word to replace (or just the word itself)
        # new = the text to replace it with
        # g = global (i.e. replace all and not just the first occurrence)

    # file.txt = the file name

    # help code: 
    # https://stackoverflow.com/questions/45771809/how-to-extract-and-visualize-data-from-osm-file-in-python 

    # bounds is blijkbaar (min_lon, min_lat    max_lon, max_lat)!!!!
    # min lon = bottom left x
    # min lat = bottom left y
    # max lon = top right x
    # max lat = top right y

    class OSMHandler(osm.SimpleHandler):
        def __init__(self):
            osm.SimpleHandler.__init__(self)
            self.osm_data = []

        def tag_inventory(self, elem, elem_type):
            for tag in elem.tags:
                # seperating min lon, min lat, max long, max lat from bounds data!
                second = []
                if "invalid" not in str(elem.bounds):
                    first = re.sub('[()]','',str(elem.bounds))
                    first = first.split(" ")
                    for el in first:
                        second.append(el.split("/"))
                else:
                    second = [[None,None],[None,None]]
                
                # appending all the data!
                self.osm_data.append([ elem.id, 
                                    elem.created_at,
                                    elem.closed_at,
                                    elem.open,
                                    elem.num_changes,
                                    elem.user,
                                    elem.uid,
                                    second[0][0],
                                    second[0][1],
                                    second[1][0],
                                    second[1][1],
                                    tag.k, 
                                    tag.v])

        def changeset(self, r):
            self.tag_inventory(r, "changeset")


    osmhandler = OSMHandler()
    # scan the input file and fills the handler list accordingly
    osmhandler.apply_file(osm_file_name[0:7])

    # transform the list into a pandas DataFrame
    data_colnames = ['id', 'created_at', 'closed_at', 'open', 'num_changes','user', 'uid', 
                    'min_lon', 'min_lat', 'max_lon', 'max_lat', 'tagkey', 'tagvalue']

    df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
    print(df_osm)

else:
    print("mistakes were made")


# database is: called mydb
# username is: myuser
# password is: mypassword

# this commando works: psql -h localhost -U myuser mydatabase

table_name = osm_file_name[0:3]
print(table_name)

engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydb')
df_osm.to_sql(table_name, engine)