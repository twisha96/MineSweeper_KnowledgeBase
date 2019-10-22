from numpy import *
import math
import matplotlib.pyplot as plt
import game_board as gb
import copy
import pandas as pd

import base_line as bl
import inference_after_baseline as inf

dim = 50
fig, ax = plt.subplots()
dim_array = [8, 9, 10]
y_baseline = []
y_inference = []
legend = []
density_array = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
column_name_list = ['density', 'mines', 'avg score percentage', 'avg random picks', 'avg execution time',
                    'avg score percentage inf', 'avg random picks inf', 'avg execution time inf']
analysis_df = pd.DataFrame(columns=column_name_list)
iterations = 10
y_baseline = []
y_inference = []
for density in density_array:
    print "density: ", density
    mines = int(math.floor(dim * dim * density))
    total_score_percent = total_exec_time = total_random_picks = 0
    total_score_percent_inf = total_exec_time_inf = total_random_picks_inf = 0
    for k in range(iterations):
        game_board = gb.get_board(dim, mines)
        board1 = copy.deepcopy(game_board)
        board2 = copy.deepcopy(game_board)
        score, random_picks, exec_time = bl.start_baseline(board1)
        score_inf, random_picks_inf, exec_time_inf = inf.start_baseline(board2, mines, knowledge_base = {})
        print "BASELINE- score: ", score, ", random picks: ", random_picks, ", exec time: ", exec_time
        print "INFERENCE- score: ", score_inf, ", random picks: ", random_picks_inf, ", exec time: ", exec_time_inf

        score_percent = float(score) * 100 / mines
        total_score_percent += score_percent
        total_exec_time += exec_time
        total_random_picks += random_picks

        score_percent_inf = float(score_inf) * 100 / mines
        total_score_percent_inf += score_percent_inf
        total_exec_time_inf += exec_time_inf
        total_random_picks_inf += random_picks_inf

    avg_score_percent = total_score_percent / iterations
    avg_exec_time = total_exec_time / iterations
    avg_random_picks = total_random_picks / iterations

    avg_score_percent_inf = total_score_percent_inf / iterations
    avg_exec_time_inf = total_exec_time_inf / iterations
    avg_random_picks_inf = total_random_picks_inf / iterations
    df_entry = pd.DataFrame([(density, mines, avg_score_percent, avg_random_picks, avg_exec_time,
                              avg_score_percent_inf, avg_random_picks_inf, avg_exec_time_inf)],
                            columns = column_name_list, index = [dim])
    print "df entry", df_entry
    analysis_df = analysis_df.append(df_entry)
    y_baseline.append(avg_score_percent)
    y_inference.append(avg_score_percent_inf)
    analysis_df.to_csv("analysis.csv")

ax.plot(density_array, y_baseline)
ax.plot(density_array, y_inference)
legend = ['Baseline', 'Inference']

plt.xlabel('Mine Density')
plt.ylabel('Avg Score Percentage')
plt.legend(legend, title = 'Algorithm')
plt.show()
analysis_df.to_csv("analysis.csv")
