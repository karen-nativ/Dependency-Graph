"""Dependency Graph Configuration

These variables are consts that are used in the Dependency Graph tool.
These variables may be edited, and they will affect the graph appearance and file
This file is required to be in the same folder as:
    create_graph.py
    graph_aux.py
"""

TEXT_FILE_FOLDER = r"dependency-graph-text/" # The file path to save the graph info, can be absolute or relative (to_file option)
TEXT_FILE_EXTENSION = r".txt" # The extension for the file that saves the graph info (to_file option)

HTML_FILE_FOLDER = r"dependency-graph-HTML/" # The file path to save the visual graph, can be absolute or relative

ARROW_COLOR = "rgb(169, 169, 169)"
ARROW_SIZE = 3
ARROW_WIDTH = 1

ERROR_ARROW_COLOR = "red"
ERROR_ARROW_SIZE = 2
ERROR_ARROW_WIDTH = 3

ARROW_HOVER_DIAMETER = 25

DEPENDENCY_INFO_LINE_AMOUNT = 9
BASE_NODE_SIZE = 11

ADDITIONAL_INFO_X = 0.5 # A decimal number relative to the graph plot, 0 is the left of the plot, 1 is the right
ADDITIONAL_INFO_Y = 1.01 # A decimal number relative to the graph plot, 0 is the bottom of the plot, 1 is the top
TEXT_SIZE = 17

TOGGLE_OPTION_X = 0 # A decimal number relative to the graph plot, 0 is the left of the plot, 1 is the right
TOGGLE_OPTION_Y = 1.1 # A decimal number relative to the graph plot, 0 is the bottom of the plot, 1 is the top

FALLBACK_BROWSER = "firefox" # The browser that will open the HTMl file if the default is not defined or cannot open the file