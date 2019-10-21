class Cell:

	def __init__(cell):
		"""
		whether or not it is a mine or safe (or currently covered)
		value = 0 => safe cell
		value = 1 => mine cell
		value = -1 => covered/unknown cell
		"""
		cell.value = -1

		# boolean to check if a cell has mine or is safe
		cell.is_mine = False

		# if safe, the number of mines surrounding it indicated by the clue
		cell.clue = 0

		# the number of safe squares identified around it 
		cell.safe_cells = 0

		# the number of mines identified around it
		cell.mines = 0

		# the number of hidden squares around it
		cell.hidden_squares = 8

		# total number of neighbors
		cell.no_of_neigbors = 8

		# probablity of cell being a mine
		cell.probability = -1.0

		# # set to total unknown mines 
		# cell.set_of_unknown_neighbors = set({})

		# # no. of hidding mines (cell.clue - cell.mines)
		# cell.set_value = -1