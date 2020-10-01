<'
import dependency_util.e;

struct vertex {
    %name : string;
    %pkg : string;
};

struct edge {
    %src_vertex : vertex;
    %dst_vertex : vertex;
    %lines : list of string;
};


extend sys {
	@import_python(module_name="create_graph", python_name="draw_graph")
    draw_graph(vertices : list of vertex, edges : list of edge, imported : list of edge, item_name : string, item_type : string, blacklist : list of string={}) is imported;
    
    @import_python(module_name="create_graph", python_name="graph_to_file")
    graph_to_file(vertices : list of vertex, edges : list of edge, imported : list of edge, item_name: string, item_type : string) is imported;
};

extend dependencies_query {
    
    //Draws a graph of recursive dependencies of the given file/module
    // OPTIONS:
    //		to_file - When TRUE, writes the graph info to file. Otherwise, visual graph is displayed.
    
    static module_graph(filename: string, to_file : bool = FALSE) is {
        var dep_from: list(key: the_module) of module_dependencies = dependencies_query::find_module_dependencies_recursively(filename);       
        var dep_to: list (key: the_module) of module_dependencies = get_all_dependencies_to(filename); 
        var all_modules: list of rf_module = dependencies_query::get_interesting_modules();
        var vertices : list (key: name) of vertex;
        for each (module) in all_modules {
        	if module.get_name() != "dependency_graph" and module.get_name() != "dependency_util" {
	        	var current_vertex : vertex = new with {
	        		.name = module.get_name();
	        		.pkg = module.get_package().get_name();
	            };
	        	vertices.push(current_vertex);
        	};
        };
        var edges : list of edge;
        var imports : list of edge;
        if not dep_from.is_empty() or not dep_to.is_empty() then {
            for each (dep) in dep_from {
            	var module_name: string = dep.the_module.get_name();
            	if module_name != "dependency_graph" and module_name != "dependency_util" {
	            	//Add import edges
	        		var all_imported : list of rf_module = dep.the_module.get_direct_imports();
	        		if not all_imported.is_empty() and module_name !~ "*_top" then {
	            	//There are imports in the current module
	        			var current_src_vertex : vertex = vertices.key(module_name);
	        			if(current_src_vertex != NULL) {
	        				for each (imported_module) in all_imported {
	        					var imported_module_name : string = imported_module.get_name();
	        					var current_dst_vertex : vertex = vertices.key(imported_module_name);
	        					if(current_dst_vertex != NULL) {
		        					var current_import : edge = new with {
		        						.src_vertex = current_src_vertex;
		        						.dst_vertex = current_dst_vertex; 
		        						//.lines = {appendf("%s imports %s", dep.the_module.get_name(), imported_module.get_name())};
		        					};
		        					imports.push(current_import);
	        					}
	        					else {
	        						out("The module ", imported_module_name, " hasn't been created as a vertex");
	        					};	
	        				};
	        			}
	        			else {
	        				out("The module ", module_name, " hasn't been created as a vertex");
	        			};
	            	};
	            	
	            	//Dependencies from the given file, recursively
	            	var dependent_module_name : string = dep.the_module.get_name();
	            	var current_src_vertex : vertex = vertices.key(dependent_module_name);
	            	if(current_src_vertex != NULL) {
		                for each (dependee) in dep.all_deps {
		                    var dependee_module_name : string = dependee.get_name();
		                    var current_dst_vertex : vertex = vertices.key(dependee_module_name);
		                    if(current_dst_vertex != NULL) {
			                    var current_edge : edge = new with {
				                    .src_vertex = current_src_vertex; //source vertex
				                    .dst_vertex = current_dst_vertex; //destination vertex
				                    .lines = get_dependency_names(dependent_module_name, dependee_module_name);
			                    };
			                    edges.push(current_edge);
		                    }
		                    else {
		                    	out("The module ", dependee_module_name, " hasn't been created as a vertex");
		                    };
		                };
	            	}
	            	else {
	            		out("The module ", dependent_module_name, " hasn't been created as a vertex");
	            	};
            	};
            };

            //Dependencies to the given file, recursively
            for each (dep) in dep_to {
                var dependee_module_name : string = dep.the_module.get_name(); // Will be destination vertex
                if dependee_module_name != "dependency_graph" and dependee_module_name != "dependency_util" then {
	                var current_dst_vertex : vertex = vertices.key(dependee_module_name);
	                if(current_dst_vertex != NULL) {
		                for each (dependent) in dep.all_deps {
			            	var dependent_module_name : string = dependent.get_name(); // Will be source vertex
			            	var current_src_vertex : vertex = vertices.key(dependent_module_name);
			            	if(current_src_vertex != NULL) {
			            		if not edges.has(it.src_vertex == current_src_vertex and it.dst_vertex == current_dst_vertex) {
					                var current_edge : edge = new with {
					                	.src_vertex = current_src_vertex;
					                	.dst_vertex = current_dst_vertex;
					                	.lines = get_dependency_names(dependent_module_name, dependee_module_name);
					                };
					                edges.push(current_edge);
			            		};
			            	}
			            	else {
			            		out("The module ", dependent_module_name, " hasn't been created as a vertex");
			            	};
		                };
	                }
	                else {
	                	out("The module ", dependee_module_name, " hasn't been created as a vertex");
	                };
                }
            };
            if to_file {
            	sys.graph_to_file(vertices.as_a(list of vertex), edges, imports, filename, "modules");
            }
            else {
            	sys.draw_graph(vertices.as_a(list of vertex), edges, imports, filename, "modules");
            };
        }
        else {
        	out("The module may not be loaded.");
        }
        
    };
    
    //Returns a list of module dependencies for all modules that depend on the given files, recursively
    static get_all_dependencies_to(filename : string) : list (key: the_module) of module_dependencies is {
    	var all_modules: list of rf_module = dependencies_query::get_interesting_modules();
        var all_modules_as_elements: list of dependency_element = all_modules.as_a(list of dependency_element);
        var module: rf_module = rf_manager.get_module_by_name(filename);
        if module != NULL then {
            result.add(new with { it.the_module = module;});
        } else if filename ~ "/\*/" then {
            for each (module) in all_modules do {
            	var module_name : string = module.get_name();
                if (module_name ~ filename) or
                  (append(module_name, ".e") ~ filename) then {
                    result.add(new with {it.the_module = module;});
                };
            };
        };
        var all_deps : list of dependency_info ;
        for each (rec_dep) in result {
        	var tmp_list: list of dependency_element;
            tmp_list.add(rec_dep.the_module);
            all_deps = dependencies_query::find_all_dependencies(all_modules_as_elements, tmp_list);
            for each (dep) in all_deps do {
                var other_module: rf_module = dep.main_dependent.as_a(rf_module);
                assert other_module != NULL;
                rec_dep.all_deps.add(other_module);
                if not result.key_exists(other_module) then {
                    result.add(new with {it.the_module = other_module;});
                };
            };
        };
    };
    
    //Draws a graph of recursive dependencies of the given package, without blacklist
    // OPTIONS:
    //		to_file - When TRUE, writes the graph info to file. Otherwise, visual graph is displayed.
    //		blacklist - Enables hiding/displaying given list of packages in the graph. Only relevant if to_file is FALSE.
    static package_graph(my_package : string, blacklist : list of string = {}, to_file : bool = FALSE) is {   
        var the_package : rf_package = rf_manager.get_package_by_name(my_package);
        if the_package != NULL then {
	        var package_modules : list of rf_module = the_package.get_modules(); //All modules to be checked
	        var vertices : list (key: name) of vertex;
	        var edges : list of edge;
	        for each (module) in package_modules {
	        	var module_name : string = module.get_name();
	        	var dep_from: list(key: the_module) of module_dependencies = dependencies_query::find_module_dependencies_recursively(module_name);
	    		for each (dep) in dep_from {
	    			var dependent_name : string = dep.the_module.get_name();
	    			var dependent_pkg_name : string = dep.the_module.get_package().get_name();
	    			if not vertices.key_exists(dependent_pkg_name) {
	    				var current_vertex : vertex = new with {
		    				.name = dependent_pkg_name;
		    				.pkg = dependent_pkg_name;
		    			};
		    			vertices.push(current_vertex);
	    			};
	    			for each (dependee) in dep.all_deps {
	    				var dependee_name : string = dependee.get_name();
	    				var dependee_pkg_name : string = dependee.get_package().get_name();
						if not vertices.key_exists(dependee_pkg_name){
							var current_vertex : vertex = new with {
								.name = dependee_pkg_name;
								.pkg = dependee_pkg_name;
							};
	    					vertices.push(current_vertex);
						};
						var dependent_vertex : vertex = vertices.key(dependent_pkg_name);
						var dependee_vertex : vertex = vertices.key(dependee_pkg_name);
						if dependent_vertex != NULL and dependee_vertex != NULL then {
							if dependent_vertex != dependee_vertex {
		    					var existing_edge : edge = edges.first(.src_vertex == dependent_vertex and .dst_vertex == dependee_vertex);
		    					if existing_edge == NULL {
		        					var current_edge : edge = new with {
			        					.src_vertex = dependent_vertex;
			        					.dst_vertex = dependee_vertex;
			        					.lines = get_dependency_names(dependent_name, dependee_name);
		        					};
		        					edges.push(current_edge);
		        				}
		        				else {
		        					existing_edge.lines.add(get_dependency_names(dependent_name, dependee_name));
		        				};
							};
						}
						else {
							out("One of the following vertices was not added: ", dependent_pkg_name, " ", dependee_pkg_name);
						};
	    			};
	        	};
	        };
	        if to_file {
                    sys.graph_to_file(vertices.as_a(list of vertex), edges, {}, my_package, "packages");
                }
              else {
                    sys.draw_graph(vertices.as_a(list of vertex), edges, {}, my_package, "packages", blacklist);
                };
        }
        else {
        	out("The package ", my_package, " was not found");
        };

    };
    
    
    
    
    static get_dependency_names(dependent_module : string, dependee_module : string) : list of string is {
        var all_dep: list of dependency_info = dependencies_query::find_all_dependencies_by_pattern(module, dependent_module, module, dependee_module);
        if all_dep is not empty then {
            for each (dep) in all_dep[0].direct_dependencies {
                var dep_string : string = appendf("%s depends on %s from %s", all_dep[0].main_dependent.get_element_name(), dep.dependee.get_element_name(), all_dep[0].main_dependee.get_element_name());
                result.add(dep_string);
            };

        };
    };
};

'>

