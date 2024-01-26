'''
This script modifies the graphml file to add the node id as a new attribute to the fuel nodes.
This enables to see the fuel-codes in the graph, too when using external software like yEd.
'''

import xml.etree.ElementTree as ET
import otoole
import subprocess
import sys
import os


def make_graphml(directory, filename):
    visualise = [
        'otoole',
        'viz',
        'res',
        'csv',
        directory,
        filename,
        'config\\otoole.yaml'
    ]
    try: #visualisation of res
        subprocess.run(visualise, check=True)
        print('Generation of res visualisation is done')
    except subprocess.CalledProcessError as e4: # Handle errors
        print(f"Error: {e4}")
        sys.exit()

def change_graphml(filename):
    # Load the .graphml file and remove the xmlns attribute from the root element
    
    with open(filename, 'r') as f:
        xml_data = f.read()
        xml_data = xml_data.replace('xmlns="http://graphml.graphdrawing.org/xmlns"', '')
        root = ET.fromstring(xml_data)
    # Iterate through the nodes and add a d4 key with the same value as the id for every fuel node
    for node in root.findall('.//node'):
        if node.find('data[@key="d0"]') is not None and \
                node.find('data[@key="d0"]').text \
                == 'fuel':
            d4_elem = ET.Element('data')
            d4_elem.set('key', 'd4')
            d4_elem.text = node.get('id')        
            node.remove(node.find('data[@key="d4"]'))
            node.append(d4_elem)
            node.tail = '\n'
    # Add the xml declaration and the xmlns attribute to the root element
    root.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')
    xml_data = ET.tostring(root, encoding='utf-8')
    xml_data = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n' + xml_data
    # Write the modified .graphml file
    with open(filename, 'wb') as f:
        f.write(xml_data)

if __name__ == "__main__":
    directory = snakemake.input[1]
    filename = snakemake.output[1]
    graphml_filename = snakemake.output[0]

    make_graphml(directory,filename)
    change_graphml(graphml_filename)

