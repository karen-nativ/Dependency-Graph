"""Dependency Graph

This tool allows the user to create a visual display of dependencies in their environment

It is assumed that this tool is called from the matching E file dependency_graph.e

This tool requires Python version >= 3.2 and the following libraries be installed:
    * packaging.version
    * plotly.graph_objects
    * plotly.offline
    * subprocess
    * platform
    * networkx
    * datetime
    * os

This tool requires the following files in the same folder:
    * graph_aux.py
    * config.py - The variables in this file may be modified and will affect the graph appearance and file

This file contains the following functions:
    * graph_to_file - Creates a text file that contains the graph information in text format
    * draw_graph - Creates an html file that displays the graph visually
"""

import graph_aux as aux
from config import *

from datetime import datetime as datetime
from packaging import version
import plotly.graph_objects as go
import plotly.offline as po
import platform
import os


class vertex:
    """ The class that corresponds with the vertex struct in the e file
    Class attributes:
    name - The displayed name of the item
    pkg - The package the item belongs to
    """
    def get_name(self):
        """ Returns the name attribute of the vertex """
        return self.name

class edge:
    """ The class that corresponds with the edge struct in the e file
    Class attributes:
    src_vertex - An object of type vertex from which the edge starts
    dst_vertex - An object of type vertex to which the edge ends
    lines - The additional information displayed while hovering over the edge
    """
    def to_tuple(self):
        """ Returns a tuple of the vertex names of the start and end of the edge """
        return (self.src_vertex.get_name(), self.dst_vertex.get_name())


###### CONSTANTS ######

SUPPORTED_TYPES = ["modules", "packages"]
PYTHON_VERSION = "3.2.0"

#######################


def graph_to_file(vertices, edges, imported, item_name, item_type):
    """Writes graph info to file in text format
    Note - This function is called from E code.
    
    Parameters
    ----------
    vertices : list of vertex
        Represents the entities from which the dependencies are being checked
    edges : list of edge
        Represents the dependencies between two entities
    imported : list of edge
        Represents the import dependencies between two entities. 
        If the graph entities are packages,this list will be empty
    item_name : string
        The name of the base entity from which the graph was created
        This will be the end of the created text file name
    item_type : string
        The entity type of the graph
        Must be one of the const SUPPORTED_TYPES
    """
    vertex_names =  [v.get_name() for v in vertices]

    parsed_imported = aux.parse_edges(imported)
    import_list = parsed_imported["edge_list"]

    parsed_edges = aux.parse_edges(edges) # A dictionary that contains the edge names and dependency additional info
    edge_list = parsed_edges["edge_list"]
    line_list = parsed_edges["line_list"] # The dependency info lines to be displayed on each edge

    folder_path = os.getcwd() + "/" + TEXT_FILE_FOLDER
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    full_path = folder_path + item_type + "-" + item_name + "-" + datetime.now().strftime("%Y_%m_%d_%H_%M") + TEXT_FILE_EXTENSION
    with open(full_path, 'w') as f:
        f.write("Vertices:\n")
        f.write(str(vertex_names) + "\n\n")
        f.write("Imports:\n")
        f.write(str(import_list) + "\n\n")
        f.write("Edges:\n")
        f.write(str(edge_list) + "\n\n")
        f.write("Dependency info:\n")
        f.write(str(line_list) + "\n\n")
    print("Graph info has been written to a text file at the following path:")
    print(full_path)
        

def draw_graph(vertices, edges, imported, item_name, item_type, blacklist=[]):
    
    """Creates an HTML file that displays an interactive graph
    Note - This function is called from E code.
    
    Parameters
    ----------
    vertices : list of vertex
        Represents the entities from which the dependencies are being checked
    edges : list of edge
        Represents the dependencies between two entities
    imported : list of edge
        Represents the import dependencies between two entities. 
        If the graph entities are packages,this list will be empty
    item_name : string
        The name of the base entity from which the graph was created
        This will be the end of the created html file name
    item_type : string
        The entity type of the graph
        Must be one of the const SUPPORTED_TYPES
    blacklist : list, optional
        A list of entities that can be displayed or hidden (default is an empty list)
    """
    
    if version.parse(platform.python_version()) < version.parse(PYTHON_VERSION):
        print("\t*** Error: Python version", PYTHON_VERSION, "is required.")
        print("\tYour current version is " + platform.python_version())
        return

    if item_type not in SUPPORTED_TYPES:
        print("\t*** Error: The supported item_type parameter values are: ", SUPPORTED_TYPES)
        return
    if len(vertices) == 0:
        print("The module may not be loaded")
        return

    # Extract information from input objects
    vertex_names =  [v.get_name() for v in vertices]
    parsed_edges = aux.parse_edges(edges) # A dictionary that contains the edge names and dependency additional info
    edge_list = parsed_edges["edge_list"]
    line_list = parsed_edges["line_list"] # The dependency info lines to be displayed on each edge

    parsed_imported = aux.parse_edges(imported)
    import_list = [import_edge for import_edge in parsed_imported["edge_list"] if import_edge not in edge_list] 
    import_info_list =[]
    for import_edge in import_list:
        import_info_list.append(import_edge[0] + " imports " + import_edge[1] + " but does not use it")



    # Generate the positions of the graph components
    node_pos = aux.create_pos(vertex_names, edge_list+import_list)
    middle_and_arrow_pos = aux.create_middle_and_arrow_pos(edge_list, line_list, node_pos)
    import_middle_and_arrow_pos = aux.create_middle_and_arrow_pos(import_list, import_info_list, node_pos)



    # Build graph components in positions
    middle_node_trace = aux.create_middle_node_trace(middle_and_arrow_pos, ARROW_COLOR)
    middle_import_trace = aux.create_middle_node_trace(import_middle_and_arrow_pos, ERROR_ARROW_COLOR)
    label_module_trace = aux.create_node_label_trace([pos[0] for (node, pos) in node_pos.items()] , [pos[1] for (node, pos) in node_pos.items()], [node for node in node_pos.keys()])

    full_graph_data = [middle_node_trace, middle_import_trace, label_module_trace]

    dependees = [edge[1] for edge in edge_list+import_list]
    dependents = [edge[0] for edge in edge_list+import_list]
    node_dependee_amount = {v: dependees.count(v) for v in vertex_names}
    node_dependent_amount = {v: dependents.count(v) for v in vertex_names}
    trace_dict = aux.create_node_traces(vertices, node_pos, node_dependee_amount) # A dictionary of all of the node traces

    for pkg in trace_dict:
        node_module_trace = aux.create_node_module_trace(trace_dict[pkg]["Xv"], trace_dict[pkg]["Yv"],  trace_dict[pkg]["name"], trace_dict[pkg]["size"], pkg)
        full_graph_data.append(node_module_trace)


    # Create the secondary graph for toggle feature
    if item_type == "modules":
        connected_vertices = set([edge[0] for edge in (edge_list + import_list)] + [edge[1] for edge in (edge_list + import_list)])
        standalones = list(filter(lambda vertex : vertex not in connected_vertices, vertex_names)) # Vertices that are not related by dependency to any other
        blacklist += standalones
        
    
    secondary_node_pos = {node: pos for node, pos in node_pos.items() if node not in blacklist}
    secondary_middle_and_arrow_pos = aux.create_middle_and_arrow_pos(edge_list, line_list, secondary_node_pos)
    secondary_import_middle_and_arrow_pos = aux.create_middle_and_arrow_pos(import_list, import_info_list, secondary_node_pos)
    secondary_trace_dict = aux.create_node_traces(vertices, secondary_node_pos, node_dependee_amount) # A dictionary of all connected node traces
    secondary_label_module_trace = aux.create_node_label_trace([pos[0] for (node, pos) in secondary_node_pos.items()] , [pos[1] for (node, pos) in secondary_node_pos.items()], [node for node in secondary_node_pos.keys()])
    secondary_middle_node_trace = aux.create_middle_node_trace(secondary_middle_and_arrow_pos, ARROW_COLOR)
    secondary_middle_import_trace = aux.create_middle_node_trace(import_middle_and_arrow_pos, ERROR_ARROW_COLOR)
    secondary_graph_data = [secondary_middle_node_trace, secondary_middle_import_trace, secondary_label_module_trace]

    for pkg in secondary_trace_dict:
        secondary_node_module_trace = aux.create_node_module_trace(secondary_trace_dict[pkg]["Xv"], secondary_trace_dict[pkg]["Yv"],  secondary_trace_dict[pkg]["name"], secondary_trace_dict[pkg]["size"], pkg, is_visible=False)
        secondary_graph_data.append(secondary_node_module_trace)



    # Build arrows in graph
    axis = aux.create_axis()

    Xarrow = middle_and_arrow_pos["Xarrow"]
    Yarrow = middle_and_arrow_pos["Yarrow"]

    
    Ximport = import_middle_and_arrow_pos["Xarrow"]
    Yimport = import_middle_and_arrow_pos["Yarrow"]

    Xsecondary = secondary_middle_and_arrow_pos["Xarrow"]
    Ysecondary = secondary_middle_and_arrow_pos["Yarrow"]

    Xsecondary_import = secondary_import_middle_and_arrow_pos["Xarrow"]
    Ysecondary_import = secondary_import_middle_and_arrow_pos["Yarrow"]


    max_dependee = max(node_dependee_amount, key=lambda k: node_dependee_amount[k])
    max_dependent = max(node_dependent_amount, key=lambda k: node_dependent_amount[k])

    my_layout = aux.create_layout(axis, Xarrow, Yarrow, Ximport, Yimport, Xsecondary, Ysecondary, Xsecondary_import, Ysecondary_import, len(vertex_names), len(edge_list)+len(import_list),  
                                  max_dependee, node_dependee_amount[max_dependee], max_dependent, node_dependent_amount[max_dependent], len(full_graph_data), len(secondary_graph_data), str(item_type))
    
    
    
    #Render and display the graph
    fig1=go.Figure(data=full_graph_data+secondary_graph_data, layout=my_layout)
    
    folder_path = os.getcwd() + "/" + HTML_FILE_FOLDER
    os.makedirs(folder_path, exist_ok=True)
    
    graph_filename = po.plot(fig1, filename=folder_path + item_type + "-" + item_name + "-" + datetime.now().strftime("%Y_%m_%d_%H_%M") + '.html', auto_open=False, config={"displayModeBar":False}) # Creates the graph into an interactive HTML file
    aux.display_in_browser("file://" + graph_filename)
    


        
if __name__ == "__main__": 
    print("This file is intended to be imported from specman module")
