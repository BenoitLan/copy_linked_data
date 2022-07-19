import osmium as osm
import pandas as pd

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
osmhandler.apply_file("829-tmp.osc")

# transform the list into a pandas DataFrame
data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid', 'user', 'chgset',
                'lon', 'lat',
                'tagkey', 'tagvalue']

df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
print(df_osm)

import json
result = (df_osm).to_json(orient="records")
parsed = json.loads(result)

# get the json data from the pandas dataframe
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(parsed, f, ensure_ascii=False, indent=4)
