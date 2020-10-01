# Dependency-Graph
Visual display of e environment dependencies.

[ More e code examples in https://github.com/efratcdn/spmn-e-utils ]

----------------------
Prerequisites
----------------------
This tool requires the following libraries be installed within the Python
environment you are running this script in:
* `networkx`
* `plotly.graph_objects`
* `plotly.offline`
* `datetime`
* `random`
* `shutil`
* `os`

This tool requires the following files in the same folder:
* `create_graph.py`
* `graph_aux.py`
* `config.py` - The variables in this file may be modified and will affect the graph appearance and file

This tool requires Specman to run in the environment, and the following environment variables to be configured:
* `PYTHONPATH` - the path to the python files written above
* `SPECMAN_PYTHON_INCLUDE_DIR`
* `SPECMAN_PYTHON_LIB_DIR`
* `SPECMAN_PATH`
(See Specman reference for details regarding these variables)


----------------------
Initialization
----------------------
In order to run the tool, the user must first run the following command:

   `specman -64 -p 'config misc -lint_mode; load dependency_graph.e'`
   
If the dependency_graph.e file is not in the current directory, load it from a relative/absolute path.

> NOTE - Make sure there aren't any modules in the environment named dependency_graph or dependency_util.
       They will not be displayed in the graph.

Afterward, the user must load the modules in the environment to Specman.
Example: `load my_top.e`


----------------------
Usage
----------------------

> NOTE - The usage of the utility on sealed and encrypted modules is limited.
The dependency graph tool creates a graph of direct and indirect dependencies, and has 2 primary uses:

1. A dependency graph between modules.
   The function dependencies_query::module_graph receives the base module for the graph.
   If the user input for the base module is *, the graph depicts all dependencies in the loaded environment.
   There are two output options:

   a)An HTML file containing a visual graph.
     
     Example: `dependencies_query::module_graph("my_module")`
              `dependencies_query::module_graph("*")`
   
   
   b)A text file containing graph information.
     
     Example: `dependencies_query::module_graph("my_module", TRUE)`


2. A dependency graph between packages.
   The function dependencies_query::package_graph receives the base package for the graph.
   In addition, the user can input a blacklist of packages that can be toggled in the display.
   This option is available only when the graph is in visual format.
   There are two output options:

   a)An HTML file containing a visual graph
     
     Example: `dependencies_query::package_graph("my_package", {"my_common_1";"my_common_2"})`
   
   b)A text file containing graph information in the following format -
     
     Example: `dependencies_query::package_graph("my_package", {}, TRUE)`



---------------------
Output
----------------------

There are two possible outputs of the tool, depending on the user input.
Both file types are saved in the current working directory.

1. An interactive html file containing a visual graph
   This file will be saved in the default folder "dependency-graph-HTML" in the directory from which this tool is run.
   The folder path is declared in the config file and is modifiable.

2. A text file containing graph information
   This file will be saved in the default folder "dependency-graph-text" in the directory from which this tool is run.
   The folder path is declared in the config file and is modifiable.   
   The format of this file is the following:
   
       Vertices:
       <list of module names(strings) in the graph>

       Imports:
       <list of tuples representing import dependencies between two modules>
       
       Edges:
       <list of tuples representing dependencies between two modules>

       Dependency info:
       <list of strings that correspond to the edges, and contain the specific dependency>
   


---------------------
Ownership
----------------------
This tool is written and owned by The Specman Team in Cadence Design Systems, Inc.
