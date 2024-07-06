import json
import csv
from pathlib import Path

def add_authors(authors: dict):
    if not authors:
        return []
    # Check if 'author' is a list of authors
    if isinstance(authors['author'], list):
        return [author['text'] for author in authors['author']]
    # If 'author' is a single author represented as a string
    elif isinstance(authors['author'], dict):
        return [authors['author']['text']]
    else:
        raise ValueError("Unexpected format for authors")

BASEDIR = Path(__file__).parents[1]

# Path to the JSON files
json_files = [BASEDIR / 'data/acl_2023.json', BASEDIR / 'data/cvpr_2023.json', BASEDIR / 'data/ijcai_2023.json', BASEDIR / 'data/neurips_2023.json']

# Path to the existing CSV file
csv_file = BASEDIR / 'data/venue_paper.csv'

# Load JSON data
data = []
for json_file in json_files:
  with open(json_file, 'r') as f:
    json_data = json.load(f)
    data.append(json_data)

# Map JSON data to CSV
with open(csv_file, 'a', newline='') as f:
  writer = csv.writer(f)
  for item in data:
    print('Processing item: ', item['result']['query'])
    for venue_item in item['result']['hits']['hit']:
      item_id = venue_item['@id']
      print('Processing item: ', item_id)
      venue_item = venue_item['info']
    
      venue = venue_item['venue']
      title = venue_item['title']
      year = venue_item['year']
      try:
        authors = add_authors(venue_item['authors'])
      except KeyError:
        authors = []
      # Write to CSV
      writer.writerow([item_id, authors, title, venue, year])
print('CSV file updated successfully')