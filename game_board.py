import random
from cell import Cell

# import the visualization libraries
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap

# set number of neighbors of edge cells to 5
def assign_hidden_squares_to_edge_cells(board, dim):
	if dim > 1:
		for index in xrange(1, dim-1):
			# cell in the left-most column
			cell = board[index][0]
			cell.hidden_squares = 5
			cell.no_of_neigbors = 5

			# cell in the right-most column
			cell = board[index][dim-1]
			cell.hidden_squares = 5
			cell.no_of_neigbors = 5

			# cell in the top-most row
			cell = board[0][index]
			cell.hidden_squares = 5
			cell.no_of_neigbors = 5

			# cell in the bottom-most row
			cell = board[dim-1][index]
			cell.hidden_squares = 5
			cell.no_of_neigbors = 5

# set number of neighbors of corner cells to 3
def assign_hidden_squares_to_corner_cells(board, dim):
	# top-left corner
	cell = board[0][0]
	cell.hidden_squares = 3
	cell.no_of_neigbors = 3

	# top-right corner
	cell = board[0][dim-1]
	cell.hidden_squares = 3
	cell.no_of_neigbors = 3

	# bottom-left corner
	cell = board[dim-1][0]
	cell.hidden_squares = 3
	cell.no_of_neigbors = 3

	# bottom-right corner
	cell = board[dim-1][dim-1]
	cell.hidden_squares = 3
	cell.no_of_neigbors = 3

# returns a list of all valid neighbors around a given cell
def get_neighbors(board, x, y):
	dim = len(board)
	neighbor_coordinates = []
	if(y-1>=0):
		neighbor_coordinates.append((x, y-1))
	if(y+1<=dim-1):
		neighbor_coordinates.append((x, y+1))	

	if(x-1>=0):
		neighbor_coordinates.append((x-1, y))
		if(y-1>=0):
			neighbor_coordinates.append((x-1, y-1))
		if(y+1<=dim-1):
			neighbor_coordinates.append((x-1, y+1))

	if(x+1<=dim-1):
		neighbor_coordinates.append((x+1, y))
		if(y-1>=0):
			neighbor_coordinates.append((x+1, y-1))
		if(y+1<=dim-1):
			neighbor_coordinates.append((x+1, y+1))

	return neighbor_coordinates

# returns board with dimension dim with n mines
def get_board(dim, n):
	board = [[Cell() for i in range(dim)] for j in range(dim)]
	
	# this returns a list of n numbers that are locations of mines
	# indexed in row-wise manner
	mine_index = random.sample(range(dim*dim), n)
	# print mine_index
	# get the coordinates x and y using the position index
	mine_locations = []
	for mine_location in mine_index:
		row = mine_location/dim
		col = mine_location%dim
		board[row][col].is_mine = True
		mine_locations.append((row, col))
	
	# get the neighbors of the mine cells and update the clue value
	for mine_location in mine_locations:
		row = mine_location[0]
		col = mine_location[1]
		neighbors = get_neighbors(board, row, col)
		# print row, col, neighbors
		for neighbor in neighbors:
			neighbor_cell = board[neighbor[0]][neighbor[1]]
			if not neighbor_cell.is_mine:
				neighbor_cell.clue += 1

	# for row_index in range(0, dim):
	# 	for col_index in range(0, dim):
	# 		cell = board[row_index][col_index]
	# 		neighbors = get_neighbors(board, row_index, col_index)
	# 		cell.set_of_unknown_neighbors = set(neighbors)

	assign_hidden_squares_to_corner_cells(board, dim)
	assign_hidden_squares_to_edge_cells(board, dim)
	
	return board

# print the current knowledge of the agent
def display_knowledge_base(knowledge_base):
	print "Knowledge Base"
	count = 1
	for key, value in knowledge_base.items():
	    print "Equation", count, sorted(key), "=", value
	    count+=1

# visualises the underlying game board generated
def visualize_board(board):
	basic_board = []
	dim = len(board)

	for i in range(dim):
		basic_board.append([])
		for j in range(dim):
			if board[i][j].is_mine:
				basic_board[i].append(10)
			else:
				if board[i][j].value == 0:
					basic_board[i].append(board[i][j].clue)
				else:
					basic_board[i].append(board[i][j].clue)
	draw_board(basic_board)

def draw_board(basic_board):

	colors = ["dimgray", "lightgray", "lightcoral", "black"]
	cmap = sns.color_palette(colors)
	ax = sns.heatmap(basic_board, annot=True, cmap=cmap, cbar=False, \
		vmax = 30, vmin = -10,
		linewidths=.1, linecolor="Black")

	for text in ax.texts:
	    if text.get_text() == '0' or text.get_text() == '-1':
	        text.set_size(0)
	        text.set_weight('bold')
	        text.set_style('italic')
	    if text.get_text() == '1':
	        text.set_weight('bold')
	        text.set_color('blue')
	    if text.get_text() == '2':
	        text.set_weight('bold')
	        text.set_color('green')
	    if text.get_text() == '3':
	        text.set_weight('bold')
	        text.set_color('crimson')
	    if text.get_text() == '4':
	        text.set_weight('bold')
	        text.set_color('darkblue')
	    if text.get_text() == '5':
	        text.set_weight('bold')
	        text.set_color('darkred')
	    if text.get_text() == '6':
	        text.set_weight('bold')
	        text.set_color('olive')
	    if text.get_text() == '7':
	        text.set_weight('bold')
	        text.set_color('midnightblue')
	    if text.get_text() == '8':
	        text.set_weight('bold')
	        text.set_color('midnightblue')
	    if text.get_text() == '9':
	        text.set_weight('bold')
	        text.set_color('midnightblue')
	        text.set_text('?')
	    if text.get_text() == '20':
	        text.set_weight('bold')
	        text.set_color('white')
	        text.set_text('|>')
	    if text.get_text() == '10':
	        text.set_weight('bold')
	        text.set_color('white')
	        text.set_text('X')
	plt.show()
	plt.close()

# visualises the current game board as seen by the agent
def visualize_agent_board(board):
	basic_board = []
	dim = len(board)

	for i in range(dim):
		basic_board.append([])
		for j in range(dim):
			if board[i][j].value==-1:
				basic_board[i].append(-1)
			else:
				if board[i][j].is_mine:
					if board[i][j].value == 1:
						basic_board[i].append(10)
					else:
						basic_board[i].append(20)
				else:
					if board[i][j].value == 0:
						basic_board[i].append(board[i][j].clue)
					else:
						basic_board[i].append(9)
					
	# ax = sns.heatmap(round(corr,2), annot=True, ax=ax, cmap="coolwarm",fmt='.2f', linewidths=.1, linecolor="Black")
	# ax = sns.heatmap(basic_board, annot=True, cmap="Blues", cbar=False, linewidths=.1, linecolor="Black")
	# plt.show()
	# plt.close()
	draw_board(basic_board)

# visualises the number of hidden squares around each cell
def visualize_board_hidden_cells():
	basic_board = []
	dim = len(board)
	for i in range(dim):
		basic_board.append([])
		for j in range(dim):
			basic_board[i].append(board[i][j].hidden_squares)

	# ax = sns.heatmap(round(corr,2), annot=True, ax=ax, cmap="coolwarm",fmt='.2f', linewidths=.1, linecolor="Black")
	ax = sns.heatmap(basic_board, annot=True, cmap="Blues", cbar=False, linewidths=.1, linecolor="Black")
	plt.show()
	plt.close()

'''
# Test code
game_board = get_board(5,10)
visualize_board(game_board)
'''