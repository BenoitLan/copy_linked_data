import osmium as osm
import pandas as pd
import re

# Changeset has to be changed to way in the .osm files to use osmium

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
osmhandler.apply_file("670.osm")

# transform the list into a pandas DataFrame
data_colnames = ['id', 'created_at', 'closed_at', 'open', 'num_changes','user', 'uid', 
                'min_lon', 'min_lat', 'max_lon', 'max_lat', 'tagkey', 'tagvalue']

df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
print(df_osm.columns)