__author__ = 'BlubBlub'

import yaml

stream = open("test.yaml", "r")
doc = yaml.load(stream)
for k,v in doc.items():
    print(k, "->", v)
print("\n")
