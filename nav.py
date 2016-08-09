import networkx

# A dictionary of location integers and strings to exact states.
places = {
		0 : (8, 1, 'E'),
		1 : (8, 2, 'E'),
		2 : (8, 3, 'E'),
		3 : (6, 1, 'W'),
		4 : (6, 2, 'W'),
		5 : (6, 3, 'W'),
		6 : (5, 1, 'E'),
		7 : (5, 2, 'E'),
		8 : (5, 3, 'E'),
		9 : (3, 1, 'W'),
		10 : (3, 2, 'W'),
		11 : (3, 3, 'W'),
		12 : (2, 1, 'E'),
		13 : (2, 2, 'E'),
		14 : (2, 3, 'E'),
		15 : (0, 1, 'W'),
		16 : (0, 2, 'W'),
		17 : (0, 3, 'W'),
		'start' : (0, 4, 'E'),
		'end' : (4, 4, 'W')
	}

def get_directions_with_replacement(G, s, t):
	""" Takes as arguments a statespace graph, starting state, and ending
		state. Returns a list of discrete commands to direct the device
		from the starting to the ending state.
	"""
	path = networkx.shortest_path(G, s, t)
	edges = zip(path[0:], path[1:])
	command = []
	for u, v in edges:
		command.append((G[u][v]['inst'], v))
	return command

def get_directions(G, s, t):
	""" Takes as arguments a statespace graph, starting state, and ending
		state. Returns a list of discrete commands to direct the device
		from the starting to the ending state.  Changes weights of outgoing
		edges from traversed nodes to ensure that car paths do not intersect.
	"""
	path = networkx.shortest_path(G, s, t, 'weight')
	path_weight = get_path_weight(G, path)
	if path_weight < 0xFFFF:
		all_outgoing_edges = networkx.edges(G, [(x, y, d) for x, y, z in path for d in ['N', 'S', 'E', 'W']])
		for u, v in all_outgoing_edges:
			G[u][v]['weight'] = 0xFFFF
		edges = zip(path[0:], path[1:])
		command = []
		for u, v in edges:
			command.append((G[u][v]['inst'], v))
		return command
	else:
		return None

def get_path_weight(G, path):
	""" Returns the total weight of a path """
	edges = zip(path[0:], path[1:])
	total = 0
	for u, v in edges:
		edge_weight = G[u][v]['weight']
		total += edge_weight
	return total

def reactivate_node(G, n):
	""" Resets to 1 the weights of all outgoing edges of a given coordinate. """
	x, y, inst = n
	all_outgoing_edges = networkx.edges(G, [(x, y, d) for d in ['N', 'S', 'E', 'W']])
	for u, v in all_outgoing_edges:
		G[u][v]['weight'] = 1

def translate_to_loc(v):
	""" Returns the state denoted by a location integer or string. """
	return places[v]
