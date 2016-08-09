from networkx import DiGraph
import cPickle

def make_warehouse():
	G = DiGraph()

	# Nodes for all states in scope. #
	G.add_nodes_from([(x, y, d) for x in range(0, 9) for y in range(0, 5) for d in ['N', 'S', 'E', 'W']])

	##### Turns #####
	# Squares/Corners #
	G.add_edges_from([((0, y, 'W'), (0, y, 'E')) for y in range(0,5)], weight = 1, inst = "u") # Column 0
	G.add_edges_from([((8, y, 'E'), (8, y, 'W')) for y in range(0,5)], weight = 1, inst = "u") # Column 8
	G.add_edges_from([((x, y, 'W'), (x, y, 'E')) for x in [3, 6] for y in range(1,4)], weight = 1, inst = "u") # Column 2, 5
	G.add_edges_from([((x, y, 'E'), (x, y, 'W')) for x in [2, 5] for y in range(1,4)], weight = 1, inst = "u") # Column 2, 5

	# Middle Spots #
	midRights = [('N', 'E'), ('E', 'S'), ('W', 'N'), ('S', 'W')]
	G.add_edges_from([((x, y, ds), (x, y, dt)) for x in [1, 4, 7] for y in range(1, 4) for ds, dt in midRights], weight = 1, inst = "r")
	G.add_edges_from([((x, y, ds), (x, y, dt)) for x in [1, 4, 7] for y in range(1, 4) for dt, ds in midRights], weight = 1, inst = "l")

	# Top Edges #
	topRights = [('N', 'E'), ('E', 'S'), ('S', 'W'), ('W', 'E')]
	topLefts = [('N', 'W'), ('W', 'S'), ('S', 'E'), ('E', 'W')]
	G.add_edges_from([((x, 0, ds), (x, 0, dt)) for x in [1, 4, 7] for ds, dt in topRights], weight = 1, inst = "r") # Column 1 Top - Rights
	G.add_edges_from([((x, 0, ds), (x, 0, dt)) for x in [1, 4, 7] for ds, dt in topLefts], weight = 1, inst = "l") # Column 1 Top - Lefts

	# Bottom Edges #
	bottomRights = [('N', 'E'), ('W', 'N'), ('S', 'W'), ('E', 'W')]
	bottomLefts = [('N', 'W'), ('W', 'E'), ('E', 'N'), ('S', 'E')]
	G.add_edges_from([((x, 4, ds), (x, 4, dt)) for x in [1, 4, 7] for ds, dt in bottomRights], weight = 1, inst = "r") # Column 1 Bottom - Rights
	G.add_edges_from([((x, 4, ds), (x, 4, dt)) for x in [1, 4, 7] for ds, dt in bottomLefts], weight = 1, inst = "l") # Column 1 Bottom - Lefts

	##### Paths #####
	# Columns 0 and 8 #
	for y in range(0, 5):
		G.add_edge((0, y, 'E'), (1, y, 'E'), weight = 1, inst = 't') # Col 0 to Col 1
		G.add_edge((8, y, 'W'), (7, y, 'W'), weight = 1, inst = 't') # Col 8 to Col 7

	# Columns 2 and 5
	G.add_edges_from([((x, y, 'W'), (x-1, y, 'W')) for x in [2, 5] for y in range(1, 4)], weight = 1, inst = 't')

	# Columns 3 and 6 #
	G.add_edges_from([((x, y, 'E'), (x+1, y, 'E')) for x in [3, 6] for y in range(1, 4)], weight = 1, inst = 't')	

	# Columns 1, 4, and 7 #
	for x in [1, 4, 7]:
		for y in range(0, 5):
			if y != 0:
				G.add_edge((x, y, "N"), (x, y-1, "N"), weight = 1, inst = 't')
			if y != 4:
				G.add_edge((x, y, "S"), (x, y+1, "S"), weight = 1, inst = 't')
		for y in range(1, 4):
			G.add_edge((x, y, "W"), (x-1, y, "W"), weight = 1, inst = 't')
			G.add_edge((x, y, "E"), (x+1, y, "E"), weight = 1, inst = 't')
		for y in [0, 4]:
			if x in [1, 4]:
				G.add_edge((x, y, "E"), (x+3, y, "E"), weight = 1, inst = 't')
			if x in [4, 7]:
				G.add_edge((x, y, "W"), (x-3, y, "W"), weight = 1, inst = 't')
			if x == 1:
				G.add_edge((x, y, "W"), (x-1, y, "W"), weight = 1, inst = 't')
			if x == 7:
				G.add_edge((x, y, "W"), (x+1, y, "E"), weight = 1, inst = 't')
	return G

W = make_warehouse()
print(W.edges())
cPickle.dump(W, open('graph.txt', 'wb'))
