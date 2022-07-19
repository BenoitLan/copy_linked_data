# won't work in notebook file, so written here
import os
import sys
import yaml

directories = os.system("""sudo docker run --rm --name yarrrmlmapper -v "/home/benoit/Documents/Linked_data/code/":/home/rmluser/data yarrrmlmapper yarrrml2.yaml --serialization turtle > 123.txt""")


