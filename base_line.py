import game_board as gb
import random
import sys
from collections import OrderedDict
from cell import Cell
import pdb
import time

def mine_found_update(row_index, col_index, board):
	neighbors = gb.get_neighbors(board, row_index, col_index)
	for neighbor in neighbors:
		neighbor_cell = board[neighbor[0]][neighbor[1]]
		neighbor_cell.hidden_squares = neighbor_cell.hidden_squares - 1
		neighbor_cell.mines = neighbor_cell.mines + 1

def safe_cell_found_update(row_index, col_index, board):
	neighbors = gb.get_neighbors(board, row_index, col_index)
	for neighbor in neighbors:
		neighbor_cell = board[neighbor[0]][neighbor[1]]
		neighbor_cell.hidden_squares = neighbor_cell.hidden_squares - 1
		neighbor_cell.safe_cells = neighbor_cell.safe_cells + 1						

# right-click in the actual game
def mark_cell_as_mine(row_index, col_index, board):
	cell = board[row_index][col_index]
	cell.value = 1
	mine_found_update(row_index, col_index, board)

# left-click in the actual game
def query_cell(row_index, col_index, board):
	cell = board[row_index][col_index]
	if cell.is_mine:
		cell.value = 1
		mine_found_update(row_index, col_index, board)
	else:
		cell.value = 0
		safe_cell_found_update(row_index, col_index, board)
	return board

def get_unexplored_cells(dim, board):
	unexplored_cells = []
	for i in range(dim):
		for j in range(dim):
			if board[i][j].value == -1:
				unexplored_cells.append((i,j))
	return unexplored_cells

# return the coordinates of a random unexplored cell
def get_random_cords(unexplored_cells):
	n = len(unexplored_cells)
	index = random.randint(0,n-1)
	x_cord = unexplored_cells[index][0]
	y_cord = unexplored_cells[index][1]
	return x_cord, y_cord

def remove_uncovered(cords, board):
	new_cords = []
	for cord in cords:
		cell = board[cord[0]][cord[1]]
		if cell.value == -1:
			new_cords.append(cord)
	cords = []
	return new_cords

# run clue check on the queried or marked cell along with its neighbors
def run_clue_check(row_index, col_index, board):
	neighbors = gb.get_neighbors(board, row_index, col_index)
	neighbors.insert(0, (row_index, col_index))
	mine_cells = []
	safe_cells = []
	for neighbor in neighbors:
		cell = board[neighbor[0]][neighbor[1]]
		if cell.value == 0:
			if cell.clue - cell.mines == cell.hidden_squares and cell.hidden_squares > 0:
				mine_cells.extend(gb.get_neighbors(board, neighbor[0], neighbor[1]))
			elif cell.no_of_neigbors - cell.clue - cell.safe_cells == cell.hidden_squares and cell.hidden_squares > 0:
				safe_cells.extend(gb.get_neighbors(board, neighbor[0], neighbor[1]))
	return [list(OrderedDict.fromkeys(remove_uncovered(mine_cells, board))), list(OrderedDict.fromkeys(remove_uncovered(safe_cells, board)))]	

# run the algorithm on the entire board till there is nothing more to infer based on local knowledge
def run_baseline(board, fringe, explored_count, unexplored_cells, dim, score):
	while(fringe and len(fringe) > 0):
		((x_cord, y_cord)) = fringe.pop(0)
		if explored_count == dim*dim:
			return explored_count, unexplored_cells, score

		# get the list of safe and mine cells
		mine_cells, safe_cells = run_clue_check(x_cord, y_cord, board)

		# mark all the cells identified as mines
		for cords in mine_cells:
			mark_cell_as_mine(cords[0], cords[1], board)
			explored_count += 1
			unexplored_cells.remove((cords[0], cords[1]))
			# gb.visualize_agent_board(game_board)
			score = score + 1
		fringe.extend(mine_cells)

		# open all the cells identified as safe cells
		for cords in safe_cells:
			board = query_cell(cords[0], cords[1], board)
			explored_count += 1
			unexplored_cells.remove((cords[0], cords[1]))
			# gb.visualize_agent_board(game_board)
		fringe.extend(safe_cells)

		# remove duplicates from the fringe and keep the latest entry
		fringe = list(OrderedDict.fromkeys(fringe))

	return explored_count, unexplored_cells, score

def start_baseline(board):
	start_time = time.time()
	random_picks = 0

	explored_count = 0
	score = 0
	dim = len(board)
	unexplored_cells = get_unexplored_cells(dim, board)

	while True:
		(row_index, col_index) = get_random_cords(unexplored_cells)
		# print "Random cell picked: ", row_index, col_index
		random_picks+=1
		fringe = [(row_index, col_index)]
		board = query_cell(row_index, col_index, board)
		explored_count += 1
		unexplored_cells.remove((row_index, col_index))
		# gb.visualize_agent_board(game_board)
		explored_count, unexplored_cells, score = run_baseline(board, fringe, explored_count, unexplored_cells, dim, score)
		if explored_count == dim*dim:
			return score, random_picks, time.time() - start_time
	return score, random_picks, time.time() - start_time

# Main Code
dimension = 5
no_of_mines = 10
game_board = gb.get_board(dimension, no_of_mines)
# gb.visualize_board(game_board)
score, random_picks, exec_time = start_baseline(game_board)
# print "Game over! Score: " + str(score) + "/" + str(no_of_mines)