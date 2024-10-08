import os
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import json
from typing import Dict, Any

# Connect to Neo4j
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
# driver = GraphDatabase.driver(uri, auth=(username, password))

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initializes the Neo4j connection.

        Args:
            uri (str): The URI for the Neo4j instance.
            user (str): Username for authentication.
            password (str): Password for authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        self.driver.close()
    
    def fetch_graph_data(self, cypher: str = "MATCH (s)-[r:!MENTIONS]->(t) RETURN s,r,t LIMIT 200") -> Dict[str, Any]:
        """
        Fetches nodes and relationships from the Neo4j graph database based on the provided Cypher query.

        Args:
            cypher (str): The Cypher query to execute.

        Returns:
            dict: A dictionary containing 'nodes' and 'links' for graph visualization.
        """
        with self.driver.session() as session:
            result = session.run(cypher)
            nodes = {}
            edges = []
            for record in result:
                source_node = record['s']
                relationship = record['r']
                target_node = record['t']
                
                # Process Source Node
                if source_node.id not in nodes:
                    nodes[source_node.id] = {
                        'id': source_node['id'],
                        'label': source_node['id'],
                        # 'group': list(source_node.labels)[0] if source_node.labels else 'Default',
                        'description': source_node['labels'],
                        # 'properties': dict(source_node)
                    }
                
                # Process Target Node
                if target_node.id not in nodes:
                    nodes[target_node.id] = {
                        'id': target_node['id'],
                        'label': target_node['id'],
                        # 'group': list(target_node.labels)[0] if target_node.labels else 'Default',
                        'description': target_node['labels'],
                        # 'properties': dict(target_node)
                    }
                
                # Process Relationship
                edges.append({
                    'source': source_node['id'],
                    'target': target_node['id'],
                    'type': relationship.type,
                    # 'properties': dict(relationship)  # Include relationship properties if needed
                })
            
            return {'nodes': list(nodes.values()), 'links': edges}
        
    def fetchGraphData(self, uri: str, username: str, password: str, cypher: str = "MATCH (s)-[r:!MENTIONS]->(t) RETURN s,r,t LIMIT 50"):
        with self.driver.session() as session:
            result = session.run(cypher)

            # Convert results to a format suitable for JSON
            graph_data = []
            for record in result:
                source = record['s']
                relationship = record['r']
                target = record['t']
                
                graph_data.append({
                    'source': dict(source),  # Convert Node to dict
                    'relationship': {
                        'type': relationship.type,  # Extract relationship type
                        'properties': dict(relationship)  # Convert Relationship properties to dict
                    },
                    'target': dict(target)  # Convert Node to dict
                })
        
        session.close()
        return graph_data
        # return {'nodes': [node for node in graph_data if 'source' not in node], 'links': [link for link in graph_data if 'source' in link]}
    
def prepare_data_for_d3(graph_data):
    # graph_data is a dictionary with 'nodes' and 'links'
    return json.dumps(graph_data)

conn = Neo4jConnection(neo4j_uri, neo4j_username, neo4j_password)

def main():
    st.set_page_config(layout="wide")
    st.title("AI Research Knowledge Graph Visualization with D3.js")

    # Fetch data from Neo4j
    graph_data = conn.fetch_graph_data()  # Adjust limit as needed
    # graph_data = conn.fetchGraphData(uri, username, password)
    # print(graph_data)
    # Prepare data for D3.js
    graph_json = prepare_data_for_d3(graph_data)

    # Checking
    # with open("sample.json", "w") as outfile:  
    #     outfile.write(graph_json)

    # Read the HTML template
    with open("knowledge_graph.html", "r") as f:
        html_template = f.read()

    # Inject the JSON data into the HTML
    html_content = html_template.replace("{{ data }}", graph_json)

    # Embed the visualization in Streamlit
    components.html(html_content, height=800, width=1200)

    # Optional: Add controls or interactivity in Streamlit
    st.sidebar.header("Controls")
    search_term = st.sidebar.text_input("Search Node")

    if search_term:
        # Implement search/filter logic if needed
        st.write(f"Search functionality can be implemented here for: {search_term}")

    conn.close()

if __name__ == "__main__":
    main()

# Function to get main concepts and their links
# @st.cache_data(show_spinner=False)  # Cache the graph data to avoid reloading
# def get_main_concepts():
#     def query_neo4j(tx):
#         query = """
#         MATCH (n)-[r]-() 
#         WITH n, COUNT(r) AS degree
#         WHERE degree > 25  // Only get nodes with more than 25 connections
#         MATCH (n)-[r]->(m)
#         RETURN n.id AS source, m.id AS target, r.type AS relationship
#         """
#         result = tx.run(query)
#         return [(record["source"], record["target"], record["relationship"]) for record in result]
    
#     with driver.session() as session:
#         main_concepts = session.read_transaction(query_neo4j)
#     return main_concepts

# # Get graph data (cached to avoid reloading on tab switch)
# main_concepts = get_main_concepts()

# # Create a PyVis network graph for main concepts
# @st.cache_data(show_spinner=False)  # Cache the PyVis graph generation
# def create_network_graph(main_concepts):
#     net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='black')

#     # Add nodes and edges for main concepts
#     for source, target, relationship in main_concepts:
#         net.add_node(source, label=source, size=20)  # Larger nodes for main concepts
#         net.add_node(target, label=target, size=20)
#         net.add_edge(source, target, title=relationship, width=2)  # Thicker edges for relationships

#     # Save the PyVis graph to HTML
#     net.save_graph('main_concepts_graph.html')

# # Generate and cache the graph
# create_network_graph(main_concepts)

# Display in Streamlit
# HtmlFile = open('main_concepts_graph.html', 'r', encoding='utf-8')
# components.html(HtmlFile.read(), height=750)

# Close the driver after querying is done
# driver.close()



# import streamlit as st
# import json
# import streamlit.components.v1 as components
# import os

# file_path = os.path.abspath('backend/llm_playground/graph_data.json')
# st.write(f"File Path: {file_path}")

# with open(file_path) as f:
#     graph_data = json.load(f)

# # Prepare sets for unique nodes and a list for edges
# nodes = set()  # Use a set to avoid duplicate nodes
# edges = []

# # Flatten the list if it's nested
# for sublist in graph_data:
#     for relationship in sublist:
#         # Extract source and target nodes
#         source_id = relationship['source']['id']
#         target_id = relationship['target']['id']
        
#         # Add nodes to the set
#         nodes.add(source_id)
#         nodes.add(target_id)
        
#         # Add edge to the list
#         edges.append({
#             'data': {
#                 'source': source_id,
#                 'target': target_id,
#                 'label': relationship['relationship']['type']
#             }
#         })

# # Convert the nodes to the format Cytoscape expects
# cytoscape_nodes = [{'data': {'id': node}} for node in nodes]

# # Combine nodes and edges
# cytoscape_elements = cytoscape_nodes + edges

# # Convert to JSON string for embedding in the HTML
# cytoscape_elements_json = json.dumps(cytoscape_elements)


# # HTML template for Cytoscape.js graph
# cytoscape_html = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Graph Visualization</title>
#     <script src="https://unpkg.com/cytoscape@latest/dist/cytoscape.min.js"></script>
#     <style>
#         #cy {{
#             width: 100%;
#             height: 800px;
#             display: block;
#             border: 1px solid #ccc;
#         }}
#     </style>
# </head>
# <body>
#     <div id="cy"></div>
#     <script>
#         document.addEventListener('DOMContentLoaded', function () {{
#             var cy = cytoscape({{
#                 container: document.getElementById('cy'),
#                 elements: {cytoscape_elements_json},
#                 layout: {{
#                     name: 'cose',
#                     idealEdgeLength: 100,
#                     nodeOverlap: 20,
#                     refresh: 20,
#                     fit: true,
#                     padding: 30,
#                     randomize: false,
#                     componentSpacing: 100,
#                     nodeRepulsion: 400000,
#                     edgeElasticity: 100,
#                     nestingFactor: 5,
#                     gravity: 80,
#                     numIter: 1000,
#                     initialTemp: 200,
#                     coolingFactor: 0.95,
#                     minTemp: 1.0
#                 }},
#                 style: [
#                     {{
#                         selector: 'node',
#                         style: {{
#                             'background-color': '#68b3c8',
#                             'label': 'data(id)',
#                             'text-valign': 'center',
#                             'text-halign': 'center',
#                             'color': '#000000',  // Make label color black for readability
#                             'font-size': '10px',  // Increase label font size
#                             'width': '40px',
#                             'height': '40px',
#                             'shape': 'ellipse',  // Node shape can be ellipse for clarity
#                             'overlay-padding': '6px',  // Add padding around nodes
#                             'z-index': '10'  // Bring nodes forward
#                         }}
#                     }},
#                     {{
#                         selector: 'edge',
#                         style: {{
#                             'width': 3,
#                             'line-color': '#888',  // Grey color for edges
#                             'target-arrow-color': '#888',
#                             'target-arrow-shape': 'triangle',
#                             'curve-style': 'bezier',
#                             'label': 'data(label)',  // Show the edge type as label
#                             'font-size': '8px',  // Set edge label font size
#                             'text-rotation': 'autorotate',
#                             'text-margin-x': '10px',  // Shift edge label away from the edge for readability
#                             'text-margin-y': '10px',  // Shift edge label down for readability
#                             'opacity': 0.7  // Reduce opacity for less clutter
#                         }}
#                     }},
#                     {{
#                         selector: 'edge[label]',
#                         style: {{
#                             'text-opacity': 1,  // Show edge labels clearly
#                             'font-size': '10px'
#                         }}
#                     }},
#                     {{
#                         selector: 'edge:hover',
#                         style: {{
#                             'width': 4,  // Increase edge width on hover
#                             'line-color': '#000',  // Highlight edge color on hover
#                             'label': 'data(label)',  // Show label when hovering
#                             'font-size': '14px'
#                         }}
#                     }},
#                     {{
#                         selector: ':selected',
#                         style: {{
#                             'background-color': '#ffd700',  // Highlight selected nodes in gold
#                             'line-color': '#ffd700',  // Highlight selected edges in gold
#                             'target-arrow-color': '#ffd700',
#                             'source-arrow-color': '#ffd700',
#                             'font-size': '18px',  // Increase font size of selected nodes
#                             'z-index': 9999
#                         }}
#                     }}
#                 ]
#             }});
#         }});
#     </script>
# </body>
# </html>
# """

# # Embed the Cytoscape.js graph into the Streamlit app
# components.html(cytoscape_html, height=800)