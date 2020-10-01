"""Dependency Graph Auxiliary Functions

These functions are not public, they are for inner use of the Dependency Graph tool.
This file is required to be in the same folder as:
    create_graph.py
    config.py
"""

from config import *
import networkx as nx
import random
import plotly.graph_objects as go
import shutil
import os

def parse_edges(edges):
    parsed_lists = {"edge_list":[], "line_list":[]}
    for current_edge in edges:
        parsed_lists["edge_list"].append(current_edge.to_tuple())
        lines_unique = list(set(current_edge.lines))
        if len(lines_unique) > DEPENDENCY_INFO_LINE_AMOUNT:
            lines_unique = lines_unique[:DEPENDENCY_INFO_LINE_AMOUNT]
            lines_unique.append("...")
        parsed_lists["line_list"].append("<br>".join(lines_unique))
    return parsed_lists

def create_pos(vertex_list, edge_list):
    G=nx.DiGraph()
    G.add_nodes_from(vertex_list)
    G.add_edges_from(edge_list)
    return nx.spring_layout(G, k=0.6, iterations=50)

def create_node_traces(vertices, positions, node_sizes):
    trace_dict={}
    for v in vertices:
        if v.name in positions: # In case positions was filtered
            if v.pkg not in trace_dict:
                trace_dict[v.pkg] = {"Xv":[], "Yv":[], "name":[], "size":[]}
            trace_dict[v.pkg]["Xv"].append(positions[v.name][0])
            trace_dict[v.pkg]["Yv"].append(positions[v.name][1])
            trace_dict[v.pkg]["name"].append(v.name)
            trace_dict[v.pkg]["size"].append(BASE_NODE_SIZE + node_sizes[v.name])
    return trace_dict


def create_middle_and_arrow_pos(edge_list, line_list, node_pos):
    Xmid=[]
    Ymid=[]
    Xarrow = []
    Yarrow = []
    lines = []
    for i in range(len(edge_list)):
        current_edge = edge_list[i]
        if current_edge[0] in node_pos and current_edge[1] in node_pos: # In case node_pos was filtered
            src_node = node_pos[current_edge[0]]
            dst_node = node_pos[current_edge[1]]
            x0 = src_node[0]
            y0 = src_node[1]
            x1 = dst_node[0]
            y1 = dst_node[1]
            Xmid.append(((x0 + x1) /2.0) + (random.random() * 0.01))
            Ymid.append((y0 + y1) /2.0)
            Xarrow.append([x0, x1])
            Yarrow.append([y0, y1])
            lines.append(line_list[i])
    return {"Xmid":Xmid, "Ymid":Ymid, "Xarrow":Xarrow, "Yarrow":Yarrow, "lines": lines}

def create_middle_node_trace(middle_and_arrow_pos, arrow_color):
    return go.Scatter(
        x=middle_and_arrow_pos["Xmid"], y=middle_and_arrow_pos["Ymid"],
        mode='markers',
        marker=dict(symbol='circle', size=ARROW_HOVER_DIAMETER, opacity=0, color=arrow_color),
        text=middle_and_arrow_pos["lines"],
        hoverinfo='text',
        showlegend=False
        )

def create_node_module_trace(Xv, Yv, node_names, node_sizes, pkg_name, is_visible=True):
    return go.Scatter(
            x=Xv, y=Yv,
            mode='markers',
            marker=dict(symbol='circle', size=node_sizes, opacity=0.8),
            name=pkg_name,
            hoverinfo='text',
            text=node_names,
            showlegend=is_visible,
            visible=is_visible
            )

def create_node_label_trace(Xv, Yv, node_names, is_visible=True):
    return go.Scatter(
            x=Xv, y=Yv,
            mode='markers+text',
            marker=dict(symbol='circle', size=BASE_NODE_SIZE, opacity=0),
            hoverinfo='skip',
            text=node_names,
            textposition="bottom center",
            showlegend=False,
            name='',
            visible=is_visible
            )
   

def create_axis():
    return dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
    )

def create_layout(axis, Xarrow, Yarrow, Ximport, Yimport, Xsecondary, Ysecondary, Xsecondary_import, Ysecondary_import, vertex_amount, edge_amount, max_dependee, dependee_amount, max_dependent, dependent_amount, full_graph_data_length, secondary_data_length, item_type):
    base_annotation = dict(text=str(vertex_amount) + ' ' + item_type + ' in total<br>' + 
                                str(edge_amount) + ' dependencies in total<br>' +  max_dependent + ' depends on a maximum of ' + str(dependent_amount) + ' ' + item_type + 
                                '<br>Maximum of ' + str(dependee_amount) + ' ' + item_type + ' depend on ' + max_dependee,
                           align='left',
                           showarrow=False,
                           xref='paper', #in relation to the edge of the graph
                           yref='paper',
                           xanchor='center',
                           yanchor='bottom',
                           x=ADDITIONAL_INFO_X,
                           y=ADDITIONAL_INFO_Y,
                           font=dict(size=TEXT_SIZE),   
                           bordercolor='black',
                           borderwidth=1)
    
    full_annotations = [dict(showarrow=True, arrowhead=5, arrowsize=ARROW_SIZE, arrowcolor=ARROW_COLOR, arrowwidth=ARROW_WIDTH,
                              ax=Xarrow[i][0], ay=Yarrow[i][0], 
                              axref='x', ayref='y',
                              xref='x', yref='y',
                              x=Xarrow[i][1], y=Yarrow[i][1],
                              opacity=0.7) for i in range(0, len(Xarrow))
                        ]
    full_annotations += [dict(showarrow=True, arrowhead=5, arrowsize=ERROR_ARROW_SIZE, arrowcolor=ERROR_ARROW_COLOR, arrowwidth=ERROR_ARROW_WIDTH, 
                              ax=Ximport[i][0], ay=Yimport[i][0], 
                              axref='x', ayref='y',
                              xref='x', yref='y',
                              x=Ximport[i][1], y=Yimport[i][1],
                              opacity=0.7) for i in range(0, len(Ximport))
                         ]
    full_annotations.append(base_annotation)

    secondary_annotations = [dict(showarrow=True, arrowhead=5, arrowsize=ARROW_SIZE, arrowcolor=ARROW_COLOR, arrowwidth=ARROW_WIDTH,
                              ax=Xsecondary[i][0], ay=Ysecondary[i][0], 
                              axref='x', ayref='y',
                              xref='x', yref='y',
                              x=Xsecondary[i][1], y=Ysecondary[i][1],
                              opacity=0.7) for i in range(0, len(Xsecondary))
                        ]
    secondary_annotations += [dict(showarrow=True, arrowhead=5, arrowsize=ERROR_ARROW_SIZE, arrowcolor=ERROR_ARROW_COLOR, arrowwidth=ERROR_ARROW_WIDTH, 
                              ax=Xsecondary_import[i][0], ay=Ysecondary_import[i][0], 
                              axref='x', ayref='y',
                              xref='x', yref='y',
                              x=Xsecondary_import[i][1], y=Ysecondary_import[i][1],
                              opacity=0.7) for i in range(0, len(Xsecondary_import))
                         ]
    secondary_annotations.append(base_annotation)

    my_updatemenus=[]
    if item_type == "modules":
        my_updatemenus = [dict(buttons=[                                                                                                        #middle nodes & label
                                       dict(args=[{"visible": [True] * full_graph_data_length + [False] * secondary_data_length, "showlegend": [False, False, False] + [True] * (full_graph_data_length - 3) + [False] * secondary_data_length, "annotations" : full_annotations}],
                                            label="Display Standalones",
                                            method="update"
                                            ),
                                                                                                                                                                                 #middle nodes & label
                                       dict(args=[{"visible":[False] * full_graph_data_length + [True] * secondary_data_length, "showlegend": [False] * full_graph_data_length + [False, False, False] + [True] * (secondary_data_length - 3), "annotations" : secondary_annotations}],
                                            label="Hide Standalones",
                                            method="update"
                                            )
                                       ],
                                    direction="down",
                                    pad={"r": 5, "t": 5},
                                    showactive=True,
                                    x=TOGGLE_OPTION_X,
                                    xanchor="left",
                                    y=TOGGLE_OPTION_Y,
                                    yanchor="bottom"
                              )
                          ]

    if item_type == "packages":
        my_updatemenus = [dict(buttons=[                                                                                                        #middle nodes & label
                                         dict(args=[{"visible": [True] * full_graph_data_length + [False] * secondary_data_length, "showlegend": [False, False, False] + [True] * (full_graph_data_length - 3) + [False] * secondary_data_length}, {"annotations" : full_annotations}],
                                            label="Display Blacklist",
                                            method="update"
                                            ),
                                                                                                                                                                                   #middle nodes & label
                                        dict(args=[{"visible":[False] * full_graph_data_length + [True] * secondary_data_length, "showlegend": [False] * full_graph_data_length + [False, False, False] + [True] * (secondary_data_length - 3)}, {"annotations" : secondary_annotations}],
                                            label="Hide Blacklist",
                                            method="update"
                                            ),],
                                    direction="down",
                                    pad={"r": 5, "t": 5},
                                    showactive=True,
                                    x=TOGGLE_OPTION_X,
                                    xanchor="left",
                                    y=TOGGLE_OPTION_Y,
                                    yanchor="bottom"
                              )]
    
    return go.Layout(
                  autosize=True,
                  xaxis=go.layout.XAxis(axis),
                  yaxis=go.layout.YAxis(axis),
                  hovermode='closest',
                  hoverlabel=dict(font_size=TEXT_SIZE),
                  font=dict(size=TEXT_SIZE),
                  legend=dict(itemclick=False, itemdoubleclick=False),
                  annotations=full_annotations,
                  updatemenus=my_updatemenus
                  )

def display_in_browser(file_path):
    import subprocess
    browsers = os.environ.get("BROWSER")
    if browsers is not None:
        browser_list = browsers.split(os.pathsep)
        for browser_path in browser_list:
            print("Opening with browser: ", browser_path)
            try:
                process = subprocess.Popen([browser_path, file_path], close_fds=True, stdin=None, stdout=None, stderr=None, start_new_session=True)
                return # Command ran successfully, no need to continue to other browsers
            except:
                print("Could not open file in browser: ", browser_path)
                
    # If a default browser was not found/ did not work, the fallback browser is used
    print("No defined default browser has succeeded. Opening with fallback browser: ", FALLBACK_BROWSER)
    try:
        process = subprocess.Popen([shutil.which(FALLBACK_BROWSER), file_path], close_fds=True, stdin=None, stdout=None, stderr=None, start_new_session=True)     
    except:
        print("Could not open file in fallback browser: ", FALLBACK_BROWSER)

