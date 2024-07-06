import json
import requests
from pathlib import Path

BASEDIR = Path(__file__).parents[1]

# URL of the webpage providing JSON data
url_ijcai = 'https://dblp.org/search/publ/api?q=toc:db/conf/ijcai/ijcai2023.bht:&h=1000&format=json'
url_neurips = 'https://dblp.org/search/publ/api?q=toc:db/conf/nips/neurips2023.bht:&h=1000&format=json'
url_acl = 'https://dblp.org/search/publ/api?q=toc:db/conf/acl/acl2023-1.bht:&h=1000&format=json'
url_cvpr = 'https://dblp.org/search/publ/api?q=toc:db/conf/cvpr/cvpr2023.bht:&h=1000&format=json'

# Fetch the content
response = requests.get(url_cvpr)

# Parse JSON data
data = response.json()

# Write to json file
with open(BASEDIR / 'data/cvpr_2023.json', 'w') as f:
    json.dump(data, f)