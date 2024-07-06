import lxml.etree as ET

def filter_xml_by_year(file_path, output_path):
    print("Starting XML filtering process...")
    new_root = ET.Element("articles")  # Create a new root for the filtered XML
    article_count = 0  # Counter for articles that match the criteria

    try:
        # Use iterparse for streaming parsing to handle large files efficiently
        for event, elem in ET.iterparse(file_path, events=("end",), tag="article", load_dtd=True):
            year_elem = elem.find(".//year")  # Adjusted to use relative path
            if year_elem is not None and year_elem.text.isdigit():
                year = int(year_elem.text)
                if 2018 <= year <= 2024:
                    new_root.append(elem)  # Add matching articles to the new root
                    article_count += 1
                    print(f"Added article published in {year}. Total articles added: {article_count}")
            
            # It's important to clear elements to free memory
            elem.clear()
            # Also clear the parent to avoid memory leak in lxml
            while elem.getprevious() is not None:
                del elem.getparent()[0]

        # After processing all articles, write the new XML to the output file
        tree = ET.ElementTree(new_root)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Filtered XML document written to {output_path}. Total articles added: {article_count}")
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")

# Example usage
input_xml_file = "/Users/max/Desktop/dblp.xml"
output_xml_file = "/Users/max/Desktop/dblp_filtered.xml"
filter_xml_by_year(input_xml_file, output_xml_file)

# https://dblp.org/faq/How+can+I+download+the+whole+dblp+dataset.html