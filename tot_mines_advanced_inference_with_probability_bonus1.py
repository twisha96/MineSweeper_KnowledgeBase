import game_board as gb
import random
from collections import OrderedDict
from cell import Cell
import time
import copy


# function called whenever a random cell is mine or a cell is marked as mine
def mine_found_update(row_index, col_index, board):
    # get all the neighbors of mine cells
    neighbors = gb.get_neighbors(board, row_index, col_index)
    for neighbor in neighbors:
        neighbor_cell = board[neighbor[0]][neighbor[1]]
        # for each neighbor reduce the number of hidden squares by 1
        neighbor_cell.hidden_squares -= 1
        # for each neighbor increase the number of mines discovered by 1
        neighbor_cell.mines += 1


# function called whenever a safe cell is being queried
def safe_cell_found_update(row_index, col_index, board):
    # get all the neighbors of mine cells
    neighbors = gb.get_neighbors(board, row_index, col_index)
    for neighbor in neighbors:
        neighbor_cell = board[neighbor[0]][neighbor[1]]
        # for each neighbor reduce the number of hidden squares by 1
        neighbor_cell.hidden_squares -= 1
        # for each neighbor increase the number of safe cells discovered by 1
        neighbor_cell.safe_cells += 1


# remove the uncovered cells from any list
def remove_uncovered(cords, board):
    new_cords = []
    for cord in cords:
        cell = board[cord[0]][cord[1]]
        if cell.value == -1:
            new_cords.append(cord)
    cords = []
    return new_cords


# function which works as a left-click in the original game
def query_cell(row_index, col_index, board, undiscovered_mines, clue_prob):
    # print "Query cell -------------", row_index, col_index
    cell = board[row_index][col_index]
    if cell.is_mine:
        # print "Oops... Mine cell queried"
        cell.value = 1
        mine_found_update(row_index, col_index, board)
        undiscovered_mines -= 1
    else:
        # Generate random probability
        rand_clue_prob = random.uniform(0, 1)
        # Safe cell and clue is revealed
        if rand_clue_prob < clue_prob:
            cell.value = 0
            # print "Clue revealed"
        # Safe cell but clue is not revealed
        else:
            cell.value = 2
            # print "Clue not revealed"
        # list of unknown neighbor is generated by looking at the neighbors
        safe_cell_found_update(row_index, col_index, board)
    return undiscovered_mines


# function which works as a right-click in the original game
def mark_cell_as_mine(row_index, col_index, board, undiscovered_mines):
    # print "Marking cell -------------", row_index, col_index
    cell = board[row_index][col_index]
    cell.value = 1
    mine_found_update(row_index, col_index, board)
    undiscovered_mines -= 1
    return undiscovered_mines


# get unexplored cells from the entire board
def get_unexplored_cells(dim, board):
    unexplored_cells = []
    for i in range(dim):
        for j in range(dim):
            if board[i][j].value == -1:
                unexplored_cells.append((i, j))
    return unexplored_cells


def get_min_max_probability_cells(knowledge_base, unexplored_cells):
    equations = knowledge_base.keys()
    overall_min_of_max = 1
    cells_based_on_max = []

    for cell in unexplored_cells:
        cell_max_prob = 0
        count = 0
        for equation in equations:
            if cell in equation:
                count += 1
                value = knowledge_base[equation]
                curr_prob = float(value)/len(equation)
                if curr_prob > cell_max_prob:
                    cell_max_prob = curr_prob

        if cell_max_prob < overall_min_of_max:
            overall_min_of_max = cell_max_prob
            cells_based_on_max = []
            cells_based_on_max.append(cell)

        if cell_max_prob == overall_min_of_max:
            cells_based_on_max.append(cell)

    return cells_based_on_max


def get_min_max_based_random_cell(knowledge_base, unexplored_cells):
    cell_pool = get_min_max_probability_cells(knowledge_base, unexplored_cells)
    n = len(cell_pool)
    if n == 1:
        return cell_pool[0]
    index = random.randint(0, n - 1)
    return cell_pool[index]


def get_min_avg_probability_cells(knowledge_base, unexplored_cells):
    equations = knowledge_base.keys()
    overall_min_of_avg = 1
    cells_based_on_avg = []

    for cell in unexplored_cells:
        cell_avg_prob = 0
        count = 0
        for equation in equations:
            if cell in equation:
                count += 1
                value = knowledge_base[equation]
                curr_prob = float(value)/len(equation)
                cell_avg_prob = float((count - 1)*cell_avg_prob + curr_prob)/count

        if cell_avg_prob < overall_min_of_avg:
            overall_min_of_avg = cell_avg_prob
            cells_based_on_avg = []
            cells_based_on_avg.append(cell)

        if cell_avg_prob == overall_min_of_avg:
            cells_based_on_avg.append(cell)

    return cells_based_on_avg


def get_min_avg_based_random_cell(knowledge_base, unexplored_cells):
    cell_pool = get_min_avg_probability_cells(knowledge_base, unexplored_cells)
    n = len(cell_pool)
    if n == 1:
        return cell_pool[0]
    index = random.randint(0, n - 1)
    return cell_pool[index]


# return the coordinates of a random unexplored cell
def get_random_cords(unexplored_cells):
    n = len(unexplored_cells)
    index = random.randint(0, n - 1)
    x_cord = unexplored_cells[index][0]
    y_cord = unexplored_cells[index][1]
    return x_cord, y_cord


# get a equation for a new cell
def get_equation(x_cord, y_cord, board, knowledge_base):
    cell = board[x_cord][y_cord]
    neighbors = gb.get_neighbors(board, x_cord, y_cord)
    variables = frozenset(remove_uncovered(neighbors, board))
    knowledge_base[variables] = cell.clue - cell.mines
    return knowledge_base


# update the knowledge base based on newly discovered safe cells and mine cells
def update_knowledge_base(knowledge_base, board, mine_cells, safe_cells):
    # print "update knowledge mine_cells: ", mine_cells
    # print "update knowledge safe_cells: ", safe_cells
    for cell in safe_cells:
        if board[cell[0]][cell[1]].value == 0:
            knowledge_base = get_equation(cell[0], cell[1], board, knowledge_base)

    for variables, value in knowledge_base.items():
        knowledge_base.pop(variables)
        intersection_mine_cells = set(variables).intersection(set(mine_cells))
        # print "intersection_mine_cells", intersection_mine_cells
        intersection_safe_cells = set(variables).intersection(set(safe_cells))
        # print "intersection_safe_cells", intersection_safe_cells
        variables = set(variables) - intersection_safe_cells - intersection_mine_cells
        value -= len(intersection_mine_cells)
        if len(variables) > 0:
            knowledge_base[frozenset(variables)] = value

    return knowledge_base


# advanced inference
def advanced_inference(knowledge_base, board):
    mine_cells = []
    safe_cells = []

    # keep reducing the equations till no more reductions are possible
    while True:
        all_equations = knowledge_base.keys()
        # # # print "all_equations: ", all_equations
        flag = 0
        for equation1 in all_equations:
            for equation2 in all_equations:
                if equation1 not in all_equations:
                    break
                if equation2 not in all_equations:
                    continue
                value1 = knowledge_base[frozenset(equation1)]
                value2 = knowledge_base[frozenset(equation2)]
                # # # print "equation1", equation1, value1
                # # # print "equation2", equation2, value2

                intersection_set = set(equation1).intersection(set(equation2))
                # # # print "intersection set:", intersection_set
                if intersection_set:
                    if value1 > value2:
                        # # # print "case1"
                        tmp_set = set(equation1) - intersection_set
                        tmp_set_value = value1 - value2
                        # # # print "tmp set:", tmp_set
                        # # # print "tmp set value:", tmp_set_value
                        if len(tmp_set) > 0 and len(tmp_set) == tmp_set_value:
                            # # # print "mine cells case1: ", tmp_set
                            mine_cells.extend(list(tmp_set))
                            flag = 1
                            knowledge_base.pop(frozenset(equation1))
                            if equation1 in all_equations:
                                all_equations.remove(equation1)
                            equation1 = equation1 - tmp_set
                            value1 -= tmp_set_value
                            knowledge_base[frozenset(equation1)] = value1

                    elif value2 > value1:
                        # # # print "case2"
                        tmp_set = set(equation2) - intersection_set
                        tmp_set_value = value2 - value1
                        # # # print "tmp set:", tmp_set
                        # # # print "tmp set value:", tmp_set_value
                        if len(tmp_set) > 0 and len(tmp_set) == tmp_set_value:
                            # # # print "mine cells case2: ", tmp_set
                            mine_cells.extend(list(tmp_set))
                            flag = 1
                            knowledge_base.pop(frozenset(equation2))
                            if equation2 in all_equations:
                                all_equations.remove(equation2)
                            equation2 = equation2 - tmp_set
                            value2 -= tmp_set_value
                            knowledge_base[frozenset(equation2)] = value2

        if flag == 0:
            break

    return list(OrderedDict.fromkeys(remove_uncovered(mine_cells, board))), \
           knowledge_base


# check for subsets to reduce the equations in knowledge base
def infer_from_knowledge_base(knowledge_base, board):
    mine_cells = []
    safe_cells = []

    # keep reducing the equations till no more reductions are possible
    while True:
        all_equations = knowledge_base.keys()
        # # # print "all_equations: ", all_equations
        flag = 0
        for equation1 in all_equations:
            for equation2 in all_equations:
                if equation1 not in all_equations:
                    break
                if equation2 not in all_equations:
                    continue
                value1 = knowledge_base[frozenset(equation1)]
                value2 = knowledge_base[frozenset(equation2)]
                # # # print "equation1", equation1, value1
                # # # print "equation2", equation2, value2

                if equation1 != equation2 and set(equation2).issubset(set(equation1)):
                    flag = 1
                    # print "Flag=1: Is subset"
                    knowledge_base.pop(frozenset(equation1))
                    if equation1 in all_equations:
                        all_equations.remove(equation1)
                    equation1 = set(equation1) - set(equation2)
                    value1 -= value2
                    knowledge_base[frozenset(equation1)] = value1
                # all_equations.append(frozenset(equation1))

                if len(equation1) == value1:
                    flag = 1
                    # print "Flag=1: Mine cells detected"
                    mine_cells.extend(list(equation1))
                    knowledge_base.pop(frozenset(equation1))
                    if equation1 in all_equations:
                        all_equations.remove(equation1)

                elif value1 == 0:
                    flag = 1
                    # print "Flag=1: Safe cells detected"
                    safe_cells.extend(list(equation1))
                    knowledge_base.pop(frozenset(equation1))
                    if equation1 in all_equations:
                        all_equations.remove(equation1)

        if flag == 0:
            break

    return list(OrderedDict.fromkeys(remove_uncovered(mine_cells, board))), \
           list(OrderedDict.fromkeys(remove_uncovered(safe_cells, board))), \
           knowledge_base


# for baseline algorithm
def run_clue_check(row_index, col_index, board):
    neighbors = gb.get_neighbors(board, row_index, col_index)
    neighbors.insert(0, (row_index, col_index))
    mine_cells = []
    safe_cells = []
    for neighbor in neighbors:
        cell = board[neighbor[0]][neighbor[1]]
        if cell.value == 0:
            if cell.hidden_squares > 0 and (cell.clue - cell.mines) == cell.hidden_squares:
                mine_cells.extend(gb.get_neighbors(board, neighbor[0], neighbor[1]))
            elif cell.hidden_squares > 0 and (cell.no_of_neigbors - cell.clue - cell.safe_cells) == cell.hidden_squares:
                safe_cells.extend(gb.get_neighbors(board, neighbor[0], neighbor[1]))

    # remove the duplicates and remove the uncovered cells from the list
    covered_mine_cells = list(OrderedDict.fromkeys(remove_uncovered(mine_cells, board)))
    covered_safe_cells = list(OrderedDict.fromkeys(remove_uncovered(safe_cells, board)))
    return covered_mine_cells, covered_safe_cells


# run baseline
def run_baseline(board, fringe, explored_count, unexplored_cells, undiscovered_mines, dim, score, knowledge_base,
                 clue_prob):
    # print "Running baseline"
    while (fringe and len(fringe) > 0):
        # # print "Baseline Fringe: ", fringe
        ((x_cord, y_cord)) = fringe.pop(0)
        if explored_count == dim*dim:
            return explored_count, unexplored_cells, undiscovered_mines, score, knowledge_base

        # base line update
        # print "Running baseline on: ", x_cord, y_cord
        mine_cells, safe_cells = run_clue_check(x_cord, y_cord, board)
        # print "mine_cells", mine_cells
        # print "safe_cells", safe_cells
        neighbors = []

        for cords in mine_cells:
            assert board[cords[0]][cords[1]].is_mine == True
            neighbors.extend(gb.get_neighbors(board, cords[0], cords[1]))
            undiscovered_mines = \
                mark_cell_as_mine(cords[0], cords[1], board, undiscovered_mines)
            explored_count += 1
            unexplored_cells.remove((cords[0], cords[1]))
            # print "after marking mine cell knowledge:"
            # gb.display_knowledge_base(knowledge_base)
            # gb.visualize_agent_board(game_board)
            score = score + 1
        fringe.extend(mine_cells)

        if undiscovered_mines == 0:
            for unexplored_cell in unexplored_cells:
                if unexplored_cell not in safe_cells:
                    safe_cells.append(unexplored_cell)

        for cords in safe_cells:
            assert board[cords[0]][cords[1]].is_mine == False
            neighbors.extend(gb.get_neighbors(board, cords[0], cords[1]))
            undiscovered_mines = query_cell(cords[0], cords[1], board, undiscovered_mines, clue_prob)
            explored_count += 1
            unexplored_cells.remove((cords[0], cords[1]))
            # print "after querying safe cell knowledge:"
            # gb.display_knowledge_base(knowledge_base)
        # gb.visualize_agent_board(game_board)
        fringe.extend(safe_cells)

        knowledge_base = update_knowledge_base(knowledge_base, board, mine_cells, safe_cells)
        # remove the duplicates from the fringe and keep the latest entry
        fringe = list(OrderedDict.fromkeys(fringe))

    return explored_count, unexplored_cells, undiscovered_mines, score, knowledge_base


# start the algorithm
def start_baseline(board, total_mines, knowledge_base, clue_prob):
    explored_count = 0
    score = 0
    dim = len(board)
    random_picks = 0
    start_time = time.time()
    unexplored_cells = get_unexplored_cells(dim, board)
    undiscovered_mines = total_mines
    knowledge_base[copy.deepcopy(frozenset(unexplored_cells))] = total_mines

    # For picking the first cell randomly
    # (row_index, col_index) = get_min_max_based_random_cell(knowledge_base, unexplored_cells)
    (row_index, col_index) = get_min_avg_based_random_cell(knowledge_base, unexplored_cells)
    random_picks += 1
    # print "Initial cell ", row_index, col_index
    fringe = [(row_index, col_index)]
    inference_fringe = []
    undiscovered_mines = \
        query_cell(row_index, col_index, board, undiscovered_mines, clue_prob)
    explored_count += 1
    unexplored_cells.remove((row_index, col_index))
    if not board[row_index][col_index].is_mine:
        knowledge_base = update_knowledge_base(knowledge_base, board, [], [(row_index, col_index)])
    else:
        knowledge_base = update_knowledge_base(knowledge_base, board, [(row_index, col_index)], [])
    # print "after querying random cell knowledge:"
    # gb.display_knowledge_base(knowledge_base)
    # gb.visualize_agent_board(game_board)

    # run baseline algorithm after opening one cell randomly
    explored_count, unexplored_cells, undiscovered_mines, score, knowledge_base = \
        run_baseline(board, fringe, explored_count, unexplored_cells, undiscovered_mines, dim, score, knowledge_base,
                     clue_prob)
    if explored_count == dim*dim:
        end_time = time.time()
        return score, random_picks, end_time - start_time

    while True:
        while True:
            # print "Inferring..."
            mine_cells_2, safe_cells_2, knowledge_base = \
                infer_from_knowledge_base(knowledge_base, board)
            # print "mine_cells_2 ",  mine_cells_2
            # print "safe_cells_2 ",  safe_cells_2

            # no inference from basic inference
            if len(mine_cells_2) == 0 and len(safe_cells_2) == 0:
                # # print "Advanced Inference..."
                mine_cells_3, knowledge_base = \
                    advanced_inference(knowledge_base, board)
                # print "mine_cells_3 ",  mine_cells_3

                if len(mine_cells_3) == 0:
                    break
                # print "!!.......EUREKA......!!"
                for cords in mine_cells_3:
                    assert board[cords[0]][cords[1]].is_mine == True
                    undiscovered_mines = \
                        mark_cell_as_mine(cords[0], cords[1], board, undiscovered_mines)
                    explored_count += 1
                    unexplored_cells.remove((cords[0], cords[1]))
                    # print "after marking mine cell knowledge:"
                    # gb.display_knowledge_base(knowledge_base)
                    # gb.visualize_agent_board(game_board)
                    score = score + 1
                fringe.extend(mine_cells_3)

            # some inference from basic inference
            else:
                for cords in mine_cells_2:
                    assert board[cords[0]][cords[1]].is_mine == True
                    undiscovered_mines = \
                        mark_cell_as_mine(cords[0], cords[1], board, undiscovered_mines)
                    explored_count += 1
                    unexplored_cells.remove((cords[0], cords[1]))
                    # print "after marking mine cell knowledge:"
                    # gb.display_knowledge_base(knowledge_base)
                    # gb.visualize_agent_board(game_board)
                    score = score + 1
                fringe.extend(mine_cells_2)

                for cords in safe_cells_2:
                    assert board[cords[0]][cords[1]].is_mine == False
                    undiscovered_mines = query_cell(cords[0], cords[1], board, undiscovered_mines, clue_prob)
                    explored_count += 1
                    unexplored_cells.remove((cords[0], cords[1]))
                    # print "after querying safe cell knowledge:"
                    # gb.display_knowledge_base(knowledge_base)
                # gb.visualize_agent_board(game_board)
                fringe.extend(safe_cells_2)

            knowledge_base = update_knowledge_base(knowledge_base, board, mine_cells_2, safe_cells_2)
            explored_count, unexplored_cells, undiscovered_mines, score, knowledge_base = \
                run_baseline(board, fringe, explored_count, unexplored_cells, undiscovered_mines, dim, score,
                             knowledge_base, clue_prob)
            if explored_count == dim*dim:
                end_time = time.time()
                return score, random_picks, end_time - start_time

        # (row_index, col_index) = get_min_max_based_random_cell(knowledge_base, unexplored_cells)
        (row_index, col_index) = get_min_avg_based_random_cell(knowledge_base, unexplored_cells)
        random_picks += 1
        # no_of_random_cell_calls += 1
        # print "Random cell ", row_index, col_index
        fringe = [(row_index, col_index)]
        undiscovered_mines = query_cell(row_index, col_index, board, undiscovered_mines, clue_prob)
        explored_count += 1
        unexplored_cells.remove((row_index, col_index))
        if not board[row_index][col_index].is_mine:
            knowledge_base = update_knowledge_base(knowledge_base, board, [], [(row_index, col_index)])
        elif board[row_index][col_index].is_mine:
            knowledge_base = update_knowledge_base(knowledge_base, board, [(row_index, col_index)], [])
        # gb.display_knowledge_base(knowledge_base)
        # gb.visualize_agent_board(game_board)

        explored_count, unexplored_cells, undiscovered_mines, score, knowledge_base = \
            run_baseline(board, fringe, explored_count, unexplored_cells, undiscovered_mines, dim, score,
                         knowledge_base, clue_prob)
        if explored_count == dim*dim:
            end_time = time.time()
            return score, random_picks, end_time - start_time

    end_time = time.time()
    return score, random_picks, end_time - start_time


# Main code
dimension = 40
density = 0.2
no_of_mines = int(dimension*dimension*density)
# print "No of mines: ", no_of_mines
clue_prob = 0.7
game_board = gb.get_board(dimension, no_of_mines)
# gb.visualize_board(game_board)
knowledge_base = {}
score, random_picks, exec_time = start_baseline(game_board, no_of_mines, knowledge_base, clue_prob)
# print "Game over! Score: " + str(score) + "/" + str(no_of_mines)
# print "Agent accuracy: ", float(score)/no_of_mines*100, "%"
# print "Random picks: ", random_picks
# print "Exec time: ", exec_time