# Trains Timetable Conflicts Solutions Optimization

This solution is solving trains timetable conflicts and optimize the solution of it. It uses modified Latvian railways data and prints the trains timetable to a .pdf and .png files. This solutions uses quantum and linear programing.

## Data

Data can be found in data folder, where is locationLinksData.csv file, which contains location links between stations of a latvian railway network and LDZ_timetable_filtered{problem_number}.xml files contains the data of the choosen railway network timetables data.

## How to use it?

### How to create QUBO matrix?

In console write line: **python QUBO_generator.py (problem_number)**

It will generate QUBO_matrix.npz file in files folder.

### How to solve it using quantums?

When QUBO matrix is generated, write line in console:
- For real quantum computing: **python Qfile_solve.py 'quantum' (problem_number) 0 0**

- For simulated quantum computing: **python Qfile_solve.py 'simulated' (problem_number) 2000 240**
  
### How to see all the solutions and timetables?

In console write line: **python solution_analysis.py (problem_number) (console/png)**

It will print all the solutions in console or create train_schedule_linear{problem_number}.pdf/train_schedule_linear{problem_number}.png, train_schedule_original{problem_number}.pdf/train_schedule_original{problem_number}.png, train_schedule_simulated{problem_number}.pdf/train_schedule_simulated{problem_number}.png, train_schedule_quantums{problem_number}_{chain_stength}.pdf/train_schedule_quantums{problem_number}_{chain_stength}.png files in solutions folder containing the timetable.
